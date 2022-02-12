from datetime import datetime
from swagger_server.database.models.drop_edition import DropEditionModel
from swagger_server.exceptions.bad_request_exception import BadRequestException
from swagger_server.services.drop_editions_service import DropEditionsService
from swagger_server.services.minting_service import MintingService
from swagger_server.services.scheduler_service import SchedulerService
from swagger_server.util import (
    publish_time_is_updated,
    validate_required_fields,
    generate_uuid,
    validate_update,
)
from swagger_server.exceptions import (
    DropNotFoundException,
    ForbiddenException,
)
from swagger_server.database.enums import DropStatus
from swagger_server.database.models import DropModel
from typing import List, Tuple


class DropsService:
    """
    Service that contains the bussiness logic to list, create, get, update, delete and publish Drops
    """

    __drop_editions_service: DropEditionsService
    __minting_service: MintingService
    __scheduler_service: SchedulerService

    def __init__(
        self,
        drop_editions_service: DropEditionsService,
        minting_service: MintingService,
        scheduler_service: SchedulerService,
    ) -> None:
        self.__drop_editions_service = drop_editions_service
        self.__minting_service = minting_service
        self.__scheduler_service = scheduler_service

    def list_drops(
        self,
        filters: dict,
        keyword: str,
        page: int,
        page_size: int,
        order: str = "desc",
        order_by: str = "created_at",
    ) -> Tuple[List[DropModel], int]:
        """Lists all the Drops that match the filters and keyword

        :param filters: dict
        :param keyword: str
        :param page: int
        :param page_size: int
        :param order: str
        :param order_by: str

        :return: Tuple[List[DropModel], int]
        """
        drop_models: List[DropModel]
        total_pages: int
        drop_models, total_pages = DropModel.get_all(
            filters, keyword, page, page_size, order, order_by
        )
        return drop_models, total_pages

    def create_drop(
        self, new_drop: DropModel, drop_editions: List[DropEditionModel] = None
    ) -> None:
        """Creates a new Drop

        :param new_drop: DropModel
        :param drop_editions: List[DropEditionModel]

        :return: None
        """
        self.__validate_start_and_end_time(new_drop)
        self.__validate_publish_time(new_drop)
        new_drop.status = DropStatus.DRAFT
        new_drop.uuid = generate_uuid()
        new_drop.add()
        new_drop.flush()
        if drop_editions is not None:
            for drop_edition in drop_editions:
                drop_edition.drop_id = new_drop.id
                self.__drop_editions_service.create_drop_edition(drop_edition)
        if publish_time_is_updated(new_drop):
            self.__create_or_update_publish_job(new_drop)

    def get_drop(self, id: int, include_editions: bool = False) -> DropModel:
        """Gets a single Drop by its id

        :param id: int
        :param format: bool

        :return: DropModel
        """
        drop_model: DropModel = DropModel.get(id, include_editions=include_editions)
        if not drop_model:
            raise DropNotFoundException(id)
        return drop_model

    def update_drop(
        self,
        id: int,
        updated_drop: DropModel,
        drop_editions: List[DropEditionModel] = None,
    ) -> Tuple[DropModel, str]:
        """Updates a Drop by its id

        :param id: int
        :param updated_drop: DropModel
        :param drop_editions: List[DropEditionModel]

        :return: Tuple[DropModel, str]
        """
        message = ""
        publish_time_was_updated = False
        start_time_of_published_drop_was_updated = False
        end_time_of_published_drop_was_updated = False
        drop_model: DropModel = self.get_drop(id, include_editions=True)
        if drop_model.status == DropStatus.DRAFT:
            self.__validate_publish_time(updated_drop, drop_model)
            publish_time_was_updated = (
                not updated_drop.dapper_drop_id
                and publish_time_is_updated(updated_drop, drop_model)
            )
        elif drop_model.status == DropStatus.PUBLISHED:
            tried_to_update = validate_update(
                original_model=drop_model,
                updated_model=updated_drop,
                not_updateable_fields=["publish_time"],
            )
            if tried_to_update:
                message += "The publish time cannot be updated because the Drop has already been published."
            start_time_of_published_drop_was_updated = self.__start_time_is_updated(
                updated_drop, drop_model
            )
            end_time_of_published_drop_was_updated = self.__end_time_is_updated(
                updated_drop, drop_model
            )
        elif drop_model.status == DropStatus.ON_SALE:
            tried_to_update = validate_update(
                original_model=drop_model,
                updated_model=updated_drop,
                not_updateable_fields=[
                    "title",
                    "description",
                    "image_url",
                    "start_time",
                    "publish_time",
                ],
            )
            if tried_to_update:
                message += "Only the end time can be updated because the Drop is already on sale. "
            self.__minting_service.update_drop(drop_model.dapper_drop_id, updated_drop)
            end_time_of_published_drop_was_updated = self.__end_time_is_updated(
                updated_drop, drop_model
            )
        elif drop_model.status == DropStatus.FINISHED:
            raise ForbiddenException(
                "Drop already finished",
                "The Drop cannot be updated because it has already finished",
            )
        self.__validate_start_and_end_time(updated_drop, drop_model)
        if drop_editions is not None:
            self.__drop_editions_service.update_drop_editions(drop_model, drop_editions)
        drop_model.update(updated_drop)
        self.__minting_service.update_drop(drop_model.dapper_drop_id, updated_drop)
        if publish_time_was_updated:
            self.__create_or_update_publish_job(drop_model)
        if start_time_of_published_drop_was_updated:
            self.__create_or_update_set_on_sale_job(drop_model)
        if end_time_of_published_drop_was_updated:
            self.__create_or_update_set_finished_job(drop_model)
        return drop_model, message

    def delete_drop(self, id: int) -> None:
        """Deletes a Drop by its id

        :param id: int

        :return: None
        """
        drop_model: DropModel = self.get_drop(id)
        if drop_model.status != DropStatus.DRAFT:
            raise ForbiddenException(
                "Drop already published",
                "The Drop cannot be deleted because it has already been published",
            )
        if drop_model.publish_time and drop_model.publish_time > datetime.now():
            self.__scheduler_service.remove_job(f"publish_drop_{str(id)}")
        drop_model.delete()

    def __validate_for_publish(self, drop: DropModel) -> None:
        """Validates that the Drop is ready to be published

        :param drop: DropModel

        :return: None
        """
        if drop.status != DropStatus.DRAFT:
            raise BadRequestException(detail="The Drop has already been published")
        required_keys = ["title", "description", "image_url", "drop_editions"]
        validate_required_fields(drop, required_keys)
        self.__validate_start_and_end_time(drop)

    def publish_drop(self, id: int) -> None:
        """Publishes a Drop by its id

        :param id: int

        :return: None
        """
        drop_model: DropModel = self.get_drop(id, include_editions=True)
        self.__validate_for_publish(drop_model)
        success, dapper_drop_id = self.__minting_service.create_drop(drop_model)
        if success:
            updated_drop = DropModel(
                status=DropStatus.PUBLISHED, dapper_drop_id=dapper_drop_id
            )
            if not drop_model.publish_time or drop_model.publish_time > datetime.now():
                updated_drop.publish_time = datetime.now()
            if not drop_model.start_time:
                updated_drop.start_time = (
                    updated_drop.publish_time
                    if updated_drop.publish_time
                    else drop_model.publish_time
                )
                updated_drop.status = DropStatus.ON_SALE
                drop_model.update(updated_drop)
                self.update_drop(id, drop_model)
            else:
                drop_model.update(updated_drop)
                self.update_drop(id, drop_model)
                self.__create_or_update_set_on_sale_job(drop_model)
            if drop_model.end_time:
                self.__create_or_update_set_finished_job(drop_model)

    def __validate_publish_time(
        self,
        new_drop: DropModel,
        current_drop: DropModel = None,
    ) -> None:
        """If it isn't an internal update (manually published), validates that:
        - The publish_time is not in the past

        :param new_drop: DropModel
        :param current_drop: DropModel

        :return: None
        """
        if new_drop.dapper_drop_id:
            return

        tzinfo = new_drop.publish_time.tzinfo if new_drop.publish_time else None
        publish_time_is_updated = new_drop.publish_time and (
            not getattr(current_drop, "publish_time", None)
            or current_drop.publish_time.replace(tzinfo=tzinfo) != new_drop.publish_time
        )

        if publish_time_is_updated:
            if new_drop.publish_time < datetime.now(tzinfo):
                raise BadRequestException(
                    detail="The publish_time cannot be in the past"
                )

    def __validate_start_and_end_time(
        self, new_drop: DropModel, current_drop: DropModel = None
    ):
        """Validates that the start_time is not in the past and the end_time is after the start_time

        :param new_drop: DropModel

        :return: None
        """
        if new_drop.start_time and not new_drop.dapper_drop_id:
            if new_drop.start_time < datetime.now(new_drop.start_time.tzinfo):
                raise BadRequestException(detail="The start_time cannot be in the past")
            end_time = (
                new_drop.end_time
                if new_drop.end_time
                else getattr(current_drop, "end_time", None)
            )
            if end_time and new_drop.start_time > end_time.replace(
                tzinfo=new_drop.start_time.tzinfo
            ):
                raise BadRequestException(
                    detail="The end_time must be after the start_time"
                )
        elif new_drop.end_time:
            start_time = (
                new_drop.start_time
                if new_drop.start_time
                else getattr(current_drop, "start_time", None)
            )
            if start_time:
                if new_drop.end_time < start_time.replace(
                    tzinfo=new_drop.end_time.tzinfo
                ):
                    raise BadRequestException(
                        detail="The end_time must be after the start_time"
                    )
            else:
                publish_time = (
                    new_drop.publish_time
                    if new_drop.publish_time
                    else getattr(current_drop, "publish_time", None)
                )
                if publish_time:
                    if new_drop.end_time < publish_time.replace(
                        tzinfo=new_drop.end_time.tzinfo
                    ):
                        raise BadRequestException(
                            detail="The end_time must be after the publish_time"
                        )
                else:
                    if new_drop.end_time < datetime.now(new_drop.end_time.tzinfo):
                        raise BadRequestException(
                            detail="The end_time cannot be in the past"
                        )

    def __create_or_update_publish_job(self, drop: DropModel):
        """Creates or updates the publish job of a Drop

        :param drop: DropModel

        :return: None
        """
        self.__validate_for_publish(drop)
        id = drop.id
        self.__scheduler_service.add_job(
            id=f"publish_drop_{str(id)}",
            func="swagger_server.controllers.drops_controller:publish_drop",
            args=[id],
            trigger="date",
            run_date=drop.publish_time,
            replace_existing=True,
        )

    def __create_or_update_set_on_sale_job(self, drop: DropModel):
        """Creates or updates the set on sale job of a Drop

        :param drop: DropModel

        :return: None
        """
        id = drop.id
        self.__scheduler_service.add_job(
            id=f"set_on_sale_drop_{str(id)}",
            func="swagger_server.controllers.drops_controller:update_drop_status",
            args=[id, DropStatus.ON_SALE.value],
            trigger="date",
            run_date=drop.start_time,
            replace_existing=True,
        )

    def __create_or_update_set_finished_job(self, drop: DropModel):
        """Creates or updates the set finished job of a Drop

        :param drop: DropModel

        :return: None
        """
        id = drop.id
        self.__scheduler_service.add_job(
            id=f"set_finished_drop_{str(id)}",
            func="swagger_server.controllers.drops_controller:update_drop_status",
            args=[id, DropStatus.FINISHED.value],
            trigger="date",
            run_date=drop.end_time,
            replace_existing=True,
        )

    def __start_time_is_updated(
        self, new_drop: DropModel, current_drop: DropModel = None
    ) -> bool:
        """Determines if the start_time of the Drop is updated

        :param new_model: DropModel
        :param current_model: DropModel

        :return: bool
        """
        if not new_drop.start_time:
            return False
        tzinfo = new_drop.start_time.tzinfo
        return (
            not getattr(current_drop, "start_time", None)
            or current_drop.start_time.replace(tzinfo=tzinfo) != new_drop.start_time
        )

    def __end_time_is_updated(
        self, new_drop: DropModel, current_drop: DropModel = None
    ) -> bool:
        """Determines if the end_time of the Drop is updated

        :param new_model: DropModel
        :param current_model: DropModel

        :return: bool
        """
        if not new_drop.end_time:
            return False
        tzinfo = new_drop.end_time.tzinfo
        return (
            not getattr(current_drop, "end_time", None)
            or current_drop.end_time.replace(tzinfo=tzinfo) != new_drop.end_time
        )
