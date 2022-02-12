from datetime import datetime
from swagger_server.database.models.collection import CollectionModel
from swagger_server.models.enums.entity import Entity
from swagger_server.services.collections_service import CollectionsService
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
from swagger_server.exceptions import (
    SerieNotFoundException,
    ForbiddenException,
    ConflictException,
    BadRequestException,
    ActiveSerieException,
)
from swagger_server.database.enums import SerieStatus, CollectionStatus
from swagger_server.database.models import SerieModel
from swagger_server.models import Serie
from typing import List, Tuple


class SeriesService:
    """
    Service that contains the bussiness logic to list, create, get, update, delete and publish Series
    """

    __minting_service: MintingService
    __scheduler_service: SchedulerService
    __collections_service: CollectionsService
    __editions_service: EditionsService

    def __init__(
        self, minting_service: MintingService, scheduler_service: SchedulerService
    ) -> None:
        self.__minting_service = minting_service
        self.__scheduler_service = scheduler_service

    def set_collections_service(self, collections_service: CollectionsService) -> None:
        """Sets the CollectionsService

        :param collections_service: CollectionsService

        :return: None
        """
        self.__collections_service = collections_service

    def set_editions_service(self, editions_service: EditionsService) -> None:
        """Sets the EditionsService

        :param editions_service: EditionsService

        :return: None
        """
        self.__editions_service = editions_service

    def list_series(
        self,
        filters: dict = None,
        keyword: str = None,
        page: int = None,
        page_size: int = None,
        order: str = "desc",
        order_by: str = "created_at",
    ) -> Tuple[List[SerieModel], int]:
        """Lists all the Series that match the filters and keyword

        :param filters: dict
        :param keyword: str
        :param page: int
        :param page_size: int
        :param order: str
        :param order_by: str

        :return: Tuple[List[SerieModel], int]
        """
        serie_models: List[SerieModel]
        total_pages: int
        serie_models, total_pages = SerieModel.get_all(
            filters, keyword, page, page_size, order, order_by
        )
        return serie_models, total_pages

    def create_serie(self, new_serie: SerieModel) -> None:
        """Creates a new Serie

        :param new_serie: SerieModel

        :return: None
        """
        validate_short_word(new_serie.short_word)
        self.__validate_publish_time(new_serie)
        new_serie.status = SerieStatus.DRAFT
        new_serie.uuid = generate_uuid()
        new_serie.add()
        new_serie.flush()
        if publish_time_is_updated(new_serie):
            self.__create_or_update_publish_job(new_serie)

    def get_serie(
        self, id: int, format: bool = True, include_collections: bool = True
    ) -> Serie:
        """Gets a single Serie by its id including all of its relationships

        :param id: int
        :param format: bool

        :return: SerieModel
        """
        serie_model: SerieModel = SerieModel.get(
            id, include_collections=include_collections
        )
        if not serie_model:
            raise SerieNotFoundException(id)
        return serie_model

    def update_serie(
        self, id: int, updated_serie: SerieModel
    ) -> Tuple[SerieModel, str]:
        """Updates a Serie by its id

        :param id: int
        :param updated_serie: SerieModel

        :return: Tuple[SerieModel, str]
        """
        message = ""
        publish_time_was_updated = False
        serie_model: SerieModel = self.get_serie(id, include_collections=False)
        if serie_model.status == SerieStatus.DRAFT:
            self.__validate_publish_time(updated_serie, serie_model)
            publish_time_was_updated = (
                not updated_serie.dapper_flow_id
                and publish_time_is_updated(updated_serie, serie_model)
            )
        else:
            if serie_model.status == SerieStatus.INACTIVE:
                raise ForbiddenException(title="Inactive series can't be updated")
            tried_to_update_on_chain_data = validate_update(
                original_model=serie_model,
                updated_model=updated_serie,
                not_updateable_fields=["name", "publish_time"],
            )
            if tried_to_update_on_chain_data:
                message += "The name and publish_time cannot be updated because the Serie has already been published. "
        if (
            updated_serie.short_word
            and updated_serie.short_word != serie_model.short_word
        ):
            validate_short_word(updated_serie.short_word)
            self.__update_shortword(serie_model, updated_serie.short_word)
        if (
            getattr(updated_serie, "status", None) == SerieStatus.INACTIVE
            and serie_model.collections
        ):
            for collection in serie_model.collections:
                self.__collections_service.update_collection(
                    collection.id, CollectionModel(status=CollectionStatus.INACTIVE)
                )
        serie_model.update(updated_serie)
        if publish_time_was_updated:
            self.__create_or_update_publish_job(serie_model)
        return serie_model, message

    def delete_serie(self, id: int) -> None:
        """Deletes a Serie by its id

        :param id: int

        :return: None
        """
        serie_model: SerieModel = self.get_serie(id)
        if serie_model.status != SerieStatus.DRAFT:
            raise ForbiddenException(
                "Serie already published",
                "The Serie cannot be deleted because it has already been published",
            )
        if serie_model.collections_count > 0:
            raise ConflictException(
                "The Serie has Collections",
                "The Serie cannot be deleted because it has Collections dependent on it",
            )
        if serie_model.publish_time and serie_model.publish_time > datetime.now():
            self.__scheduler_service.remove_job(f"publish_serie_{str(id)}")
        serie_model.delete()

    def __validate_for_publish(
        self, serie: SerieModel, publish_now: bool = False
    ) -> None:
        """Validates that the Serie is ready to be published

        :param serie: SerieModel

        :return: None
        """
        if serie.status != SerieStatus.DRAFT:
            raise BadRequestException(detail="The Series has already been published")
        required_keys = ["name", "description", "short_word"]
        validate_required_fields(serie, required_keys)
        tzinfo = None
        publish_time: datetime
        if serie.publish_time and not publish_now:
            tzinfo = serie.publish_time.tzinfo
            publish_time = serie.publish_time
        else:
            publish_time = datetime.now()
        active_series, _ = self.list_series(filters={"status": [SerieStatus.ACTIVE]})
        for active_serie in active_series:
            collections = active_serie.collections
            for collection in collections:
                if (
                        collection.publish_time and
                        collection.publish_time.replace(tzinfo=tzinfo) > publish_time
                    ):
                    raise ActiveSerieException()

    def publish_serie(self, id: int) -> None:
        """Publishes a Serie by its id

        :param id: int

        :return: None
        """
        serie_model: SerieModel = self.get_serie(id, include_collections=False)
        self.__validate_for_publish(serie_model, True)
        success, dapper_flow_id = self.__minting_service.create_serie(
            serie=serie_model,
        )
        if success:
            previous_series: List[SerieModel]
            previous_series, _ = self.list_series(
                filters={"status": [SerieStatus.ACTIVE]}
            )
            updated_serie = SerieModel(
                status=SerieStatus.ACTIVE, dapper_flow_id=dapper_flow_id
            )
            if (
                not serie_model.publish_time
                or serie_model.publish_time > datetime.now()
            ):
                updated_serie.publish_time = datetime.now()
            self.update_serie(id, updated_serie)
            for previous_serie in previous_series:
                self.update_serie(
                    previous_serie.id,
                    SerieModel(status=SerieStatus.INACTIVE),
                )

    def update_collections_count(self, serie_id, difference) -> None:
        """Updates the collections_count of a Serie

        :param serie_id: int
        :param difference: int

        :return: None
        """
        serie_model: SerieModel = self.get_serie(serie_id, include_collections=False)
        serie_model.collections_count += difference

    def __update_shortword(
        self, serie_model: SerieModel, updated_short_word: str
    ) -> None:
        """If the Serie doesn't have any published Edition, updates the wearable SKU in the draft Editions. Otherwise, raises an exception.

        :param serie_model: SerieModel
        :param updated_short_word: str

        :return: None
        """
        if serie_model.has_published_editions:
            raise ConflictException(
                "short_word cannot be updated",
                "The short_word cannot be updated because the Series has published Editions dependent on it.",
            )
        else:
            for collection in serie_model.collections:
                for edition in collection.editions:
                    self.__editions_service.update_avatar_wearable_sku(
                        edition, Entity.SERIE, updated_short_word
                    )

    def __validate_publish_time(
        self,
        new_serie: SerieModel,
        current_serie: SerieModel = None,
    ) -> None:
        """If it isn't an internal update (manually published), validates that:
        - The publish_time is not in the past
        - The Serie hasn't any Collection with a publish_time before its own publish_time

        :param new_serie: SerieModel
        :param current_serie: SerieModel

        :return: None
        """
        if new_serie.dapper_flow_id:
            return
        if publish_time_is_updated(new_serie, current_serie):
            tzinfo = new_serie.publish_time.tzinfo
            if new_serie.publish_time < datetime.now(tzinfo):
                raise BadRequestException(
                    detail="The publish_time cannot be in the past"
                )
            if current_serie and current_serie.collections:
                collections_with_publish_time_before_serie = []
                for collection in current_serie.collections:
                    if (
                        collection.publish_time
                        and collection.publish_time.replace(tzinfo=tzinfo)
                        < new_serie.publish_time
                    ):
                        collections_with_publish_time_before_serie.append(
                            collection.name
                        )
                if collections_with_publish_time_before_serie:
                    raise BadRequestException(
                        detail="The Series' publish_time cannot be after the publish_time of its Collections: "
                        + str(collections_with_publish_time_before_serie)
                    )

    def __create_or_update_publish_job(self, serie: SerieModel) -> None:
        """Creates or updates the publish job of a Serie

        :param serie_model: SerieModel

        :return: None
        """
        self.__validate_for_publish(serie)
        id = serie.id
        self.__scheduler_service.add_job(
            id=f"publish_serie_{str(id)}",
            func="swagger_server.controllers.series_controller:publish_serie",
            args=[id],
            trigger="date",
            run_date=serie.publish_time,
            replace_existing=True,
        )
