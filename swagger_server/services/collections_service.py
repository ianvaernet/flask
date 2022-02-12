from datetime import datetime
from swagger_server.database.enums.serie_status import SerieStatus
from swagger_server.database.models.serie import SerieModel
from swagger_server.models.enums.entity import Entity
from swagger_server.services.editions_service import EditionsService
from swagger_server.services.minting_service import MintingService
from swagger_server.services.scheduler_service import SchedulerService
from swagger_server.util import (
    publish_time_is_updated,
    validate_required_fields,
    generate_uuid,
    validate_short_word,
    validate_update,
)
from swagger_server.exceptions.conflict_exception import ConflictException
from swagger_server.exceptions import (
    CollectionNotFoundException,
    ForbiddenException,
    BadRequestException,
)
from swagger_server.database.enums import CollectionStatus
from swagger_server.database.models import CollectionModel
from typing import Any, List, Tuple


class CollectionsService:
    """
    Service that contains the bussiness logic to list, create, get, update, delete and publish Collections
    """

    __series_service: Any
    __editions_service: EditionsService
    __minting_service: MintingService
    __scheduler_service: SchedulerService

    def __init__(
        self,
        series_service,
        minting_service: MintingService,
        scheduler_service: SchedulerService,
    ) -> None:
        self.__series_service = series_service
        self.__minting_service = minting_service
        self.__scheduler_service = scheduler_service

    def set_editions_service(self, editions_service: EditionsService) -> None:
        """Sets the EditionsService

        :param editions_service: EditionsService

        :return: None
        """
        self.__editions_service = editions_service

    def list_collections(
        self,
        filters: dict,
        keyword: str,
        page: int,
        page_size: int,
        order: str = "desc",
        order_by: str = "created_at",
    ) -> Tuple[List[CollectionModel], int]:
        """Lists all the Collections that match the filters and keyword

        :param filters: dict
        :param keyword: str
        :param page: int
        :param page_size: int
        :param order: str
        :param order_by: str

        :return: Tuple[List[CollectionModel], int]
        """
        collection_models: list[CollectionModel]
        total_pages: int
        collection_models, total_pages = CollectionModel.get_all(
            filters, keyword, page, page_size, order=order, order_by=order_by
        )
        return collection_models, total_pages

    def create_collection(self, new_collection: CollectionModel) -> None:
        """Creates a new Collection

        :param new_collection: CreateCollection

        :return: None
        """
        validate_short_word(new_collection.short_word)
        self.__validate_publish_time(new_collection)
        new_collection.status = CollectionStatus.DRAFT
        new_collection.uuid = generate_uuid()
        new_collection.add()
        new_collection.flush()
        if publish_time_is_updated(new_collection):
            self.__create_or_update_publish_job(new_collection)
        self.__series_service.update_collections_count(new_collection.serie_id, 1)

    def get_collection(
        self, id: int, include_serie: bool = True, include_editions: bool = False
    ) -> CollectionModel:
        """Gets a single Collection by its id

        :param id: int
        :param format: bool

        :return: CollectionModel
        """
        collection_model: CollectionModel = CollectionModel.get(
            id, include_serie=include_serie, include_editions=include_editions
        )
        if not collection_model:
            raise CollectionNotFoundException(id)
        return collection_model

    def update_collection(
        self,
        id: int,
        updated_collection: CollectionModel,
        wearables_count_difference: int = None,
    ) -> Tuple[CollectionModel, str]:
        """Updates a Collection by its id

        :param id: int
        :param updated_collection: CollectionModel

        :return: Tuple[CollectionModel, str]
        """
        message = ""
        publish_time_was_updated = False
        collection_model: CollectionModel = self.get_collection(
            id, include_serie=False, include_editions=False
        )
        if collection_model.status == CollectionStatus.DRAFT:
            self.__validate_publish_time(updated_collection, collection_model)
            publish_time_was_updated = (
                not updated_collection.dapper_flow_id
                and publish_time_is_updated(updated_collection, collection_model)
            )
        else:
            if collection_model.status == CollectionStatus.INACTIVE:
                raise ForbiddenException(title="Inactive collections can't be updated")
            tried_to_update_on_chain_data = validate_update(
                original_model=collection_model,
                updated_model=updated_collection,
                not_updateable_fields=["name", "publish_time", "serie_id"],
            )
            if tried_to_update_on_chain_data:
                message += "The name, publish_time and serie_id cannot be updated because the Collection has already been published. "
            if (
                updated_collection.description
                and updated_collection.description != collection_model.description
            ):
                self.__minting_service.update_collection(
                    collection_model.dapper_flow_id, updated_collection
                )
        if (
            updated_collection.short_word
            and updated_collection.short_word != collection_model.short_word
        ):
            validate_short_word(updated_collection.short_word)
            self.__update_shortword(collection_model, updated_collection.short_word)
        if wearables_count_difference:
            collection_model.wearables_count += wearables_count_difference
        collection_model.update(updated_collection)
        if publish_time_was_updated:
            self.__create_or_update_publish_job(collection_model)
        return collection_model, message

    def delete_collection(self, id: int) -> None:
        """Deletes a Collection by its id

        :param id: int

        :return: None
        """
        collection_model: CollectionModel = self.get_collection(
            id, include_serie=False, include_editions=False
        )
        if collection_model.status != CollectionStatus.DRAFT:
            raise ForbiddenException(
                "Collection already published",
                "The Collection cannot be deleted because it has already been published",
            )
        if collection_model.wearables_count > 0:
            raise ConflictException(
                "The Collection has Wearables",
                "The Collection cannot be deleted because it has Wearables dependent on it",
            )
        if (
            collection_model.publish_time
            and collection_model.publish_time > datetime.now()
        ):
            self.__scheduler_service.remove_job(f"publish_collection_{str(id)}")
        collection_model.delete()
        self.__series_service.update_collections_count(collection_model.serie_id, -1)

    def __validate_for_publish(
        self, collection: CollectionModel, publish_now: bool = False
    ) -> None:
        """Validates that the Collection is ready to be published

        :param collection: CollectionModel
        :param publish_now: bool

        :return: None
        """
        if collection.status != CollectionStatus.DRAFT:
            raise BadRequestException(
                detail="The Collection has already been published"
            )
        required_keys = ["name", "description", "short_word", "serie_id"]
        validate_required_fields(collection, required_keys)
        if not collection.serie:
            raise BadRequestException(
                detail="The Collection must belong to an existing Series"
            )
        if publish_now and (
            collection.serie.status != SerieStatus.ACTIVE
            or not collection.serie.dapper_flow_id
        ):
            raise BadRequestException(
                detail="The Collection must belong to an active Series"
            )

    def publish_collection(self, id: int) -> None:
        """Publishes a Collection by its id

        :param id: int

        :return: None
        """
        collection_model: CollectionModel = self.get_collection(
            id, include_serie=True, include_editions=False
        )
        self.__validate_for_publish(collection_model, True)
        success, dapper_flow_id = self.__minting_service.create_collection(
            collection=collection_model,
        )
        if success:
            updated_collection = CollectionModel(
                status=CollectionStatus.PUBLISHED,
                dapper_flow_id=dapper_flow_id,
            )
            if (
                not collection_model.publish_time
                or collection_model.publish_time > datetime.now()
            ):
                updated_collection.publish_time = datetime.now()
            self.update_collection(id, updated_collection)

    def update_has_published_editions(self, collection_model: CollectionModel) -> None:
        """Sets to True the has_published_edition field of the Collection

        :return: None
        """
        collection_model.has_published_editions = True

    def __update_shortword(
        self,
        collection_model: CollectionModel,
        updated_short_word: str,
    ) -> None:
        """In case the Collection doesn't have any published Edition, updates the wearable SKU in the draft Editions

        :param serie_model: CollectionModel
        :param updated_short_word: str

        :return: None
        """
        if collection_model.has_published_editions:
            raise ConflictException(
                "short_word cannot be updated",
                "The short_word cannot be updated because the Collection has published Editions dependent on it.",
            )
        else:
            for edition in collection_model.editions:
                self.__editions_service.update_avatar_wearable_sku(
                    edition, Entity.COLLECTION, updated_short_word
                )

    def __validate_publish_time(
        self,
        new_collection: CollectionModel,
        current_collection: CollectionModel = None,
    ) -> None:
        """If it isn't an internal update (manually published), validates that:
        - The publish_time is not in the past
        - The publish_time is after its Serie's publish_time (which can't be None)
        - The Collection hasn't any Edition with a publish_time before its own publish_time

        :param new_collection: CollectionModel
        :param current_collection: CollectionModel

        :return: None
        """
        if new_collection.dapper_flow_id:
            return
        tzinfo = (
            new_collection.publish_time.tzinfo if new_collection.publish_time else None
        )
        serie_is_updated = (
            new_collection.serie_id
            and new_collection.serie_id != getattr(current_collection, "serie_id", None)
        )
        publish_time_is_set = current_collection and current_collection.publish_time

        if serie_is_updated:
            serie: SerieModel = self.__series_service.get_serie(
                new_collection.serie_id, include_collections=False
            )
        else:
            serie: SerieModel = current_collection.serie

        if publish_time_is_updated(new_collection, current_collection):
            if new_collection.publish_time < datetime.now(tzinfo):
                raise BadRequestException(
                    detail="The publish_time cannot be in the past"
                )
            if not serie.publish_time:
                raise BadRequestException(
                    detail="The Collection's publish_time cannot be set until the publish_time of its Series is set"
                )
            if serie.publish_time.replace(tzinfo=tzinfo) > new_collection.publish_time:
                raise BadRequestException(
                    detail="The Collection's publish_time cannot be before the publish_time of its Series"
                )
            if current_collection and current_collection.editions:
                editions_with_publish_time_before_collection = []
                for edition in current_collection.editions:
                    if (
                        edition.publish_time
                        and edition.publish_time.replace(tzinfo=tzinfo)
                        < new_collection.publish_time
                    ):
                        editions_with_publish_time_before_collection.append(
                            edition.name
                        )
                if editions_with_publish_time_before_collection:
                    raise BadRequestException(
                        detail="The Collection's publish_time cannot be after the publish_time of its Editions: "
                        + str(editions_with_publish_time_before_collection)
                    )
        elif serie_is_updated and publish_time_is_set:
            if not serie.publish_time:
                raise BadRequestException(
                    detail="The Collection's publish_time cannot be set until the publish_time of its Series is set"
                )
            if (
                serie.publish_time.replace(tzinfo=tzinfo)
                > current_collection.publish_time
            ):
                raise BadRequestException(
                    detail="The Collection's publish_time cannot be before the publish_time of its Series"
                )

    def __create_or_update_publish_job(
        self,
        collection: CollectionModel,
    ):
        """Creates or updates the publish job of a Collection

        :param collection: CollectionModel

        :return: None
        """
        self.__validate_for_publish(collection)
        id = collection.id
        self.__scheduler_service.add_job(
            id=f"publish_collection_{str(id)}",
            func="swagger_server.controllers.collections_controller:publish_collection",
            args=[id],
            trigger="date",
            run_date=collection.publish_time,
            replace_existing=True,
        )
