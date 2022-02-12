from swagger_server.database.enums.edition_status import EditionStatus
from swagger_server.database.models.edition import EditionModel
from swagger_server.exceptions import (
    DropEditionNotFoundException,
    BadRequestException,
    ForbiddenException,
)
from swagger_server.database.models import DropEditionModel, DropModel
from swagger_server.models import DropEdition
from swagger_server.database.enums import DropStatus
from typing import List, Tuple
from swagger_server.services.editions_service import EditionsService
from swagger_server.util import generate_uuid, validate_price


class DropEditionsService:
    """
    Service that contains the bussiness logic to create, get, update and delete Drop Editions
    """

    __editions_service: EditionsService

    def __init__(self, editions_service: EditionsService) -> None:
        self.__editions_service = editions_service

    def create_drop_edition(self, new_drop_edition: DropEditionModel) -> None:
        """Creates a new DropEdition

        :param new_drop_edition: DropEditionModel

        :return: None
        """
        edition_model: EditionModel = self.__editions_service.get_edition(
            new_drop_edition.edition_id,
            include_collection=False,
            include_drops=False,
            include_nfts=False,
        )
        if edition_model.status != EditionStatus.MINTED: #this should be ON_SALE
            raise BadRequestException(
                title="Edition not on sale",
                detail="The Edition with ID="
                + str(new_drop_edition.edition_id)
                + " is not on sale yet, so it cannot be part of a Drop",
            )
        # if edition_model.nfts_for_sale <= 0:
        #     raise BadRequestException(
        #         title="Edition without stock",
        #         detail="The Edition with ID="+str(new_drop_edition.edition_id)+" has not available stock",
        #     )
        validate_price(new_drop_edition.price)
        new_drop_edition.uuid = generate_uuid()
        new_drop_edition.add()

    def get_drop_edition(
        self,
        drop_id: int,
        edition_id: int,
        include_drop: bool = True,
        include_edition: bool = True,
    ) -> DropEditionModel:
        """Gets a single Drop edition by its id

        :param id: int
        :param include_drop: bool
        :param include_edition: bool

        :return: DropEditionModel
        """
        drop_edition_model: DropEditionModel = DropEditionModel.get(
            drop_id,
            edition_id,
            include_drop=include_drop,
            include_edition=include_edition,
        )
        if not drop_edition_model:
            raise DropEditionNotFoundException(drop_id, edition_id)
        return drop_edition_model

    def update_drop_editions(
        self,
        current_drop: DropModel,
        updated_drop_editions: List[DropEditionModel] = [],
    ) -> None:
        """Updates all the editions of a Drop

        :param current_drop: DropModel
        :param updated_drop_editions: List[DropEditionModel]

        :return: None
        """
        if not current_drop.drop_editions:
            current_drop.drop_editions = []
        current_edition_ids = map(
            lambda drop_edition: drop_edition.edition_id, current_drop.drop_editions
        )
        updated_edition_ids = map(
            lambda drop_edition: drop_edition.edition_id, updated_drop_editions
        )

        for updated_drop_edition in updated_drop_editions:
            if updated_drop_edition.edition_id in current_edition_ids:
                current_drop_edition = next(
                    current_drop_edition
                    for current_drop_edition in current_drop.drop_editions
                    if current_drop_edition.edition_id
                    == updated_drop_edition.edition_id
                )
                if current_drop_edition.price != updated_drop_edition.price:
                    if current_drop.status == DropStatus.ON_SALE:
                        raise ForbiddenException(
                            title="Drop already on sale",
                            detail="The price of the edition ID="
                            + str(current_drop_edition.edition_id)
                            + " cannot be updated as the Drop is on sale",
                        )
                    else:
                        self.update_drop_edition(
                            current_drop_edition=current_drop_edition,
                            updated_drop_edition=updated_drop_edition,
                        )
            else:
                if current_drop.status == DropStatus.ON_SALE:
                    raise ForbiddenException(
                        title="Drop already on sale",
                        detail="The edition ID="
                        + str(current_drop_edition.edition_id)
                        + " cannot be added to this drop as it is already on sale",
                    )
                else:
                    new_drop_edition = DropEditionModel(
                        drop_id=current_drop.id,
                        edition_id=updated_drop_edition.edition_id,
                        price=updated_drop_edition.price,
                    )
                    self.create_drop_edition(new_drop_edition)
                    current_drop.drop_editions.append(new_drop_edition)

        for current_drop_edition in current_drop.drop_editions:
            if current_drop_edition.edition_id not in updated_edition_ids:
                if current_drop.status == DropStatus.ON_SALE:
                    raise ForbiddenException(
                        title="Drop already on sale",
                        detail="The edition ID="
                        + str(current_drop_edition.edition_id)
                        + " cannot be removed from this drop as it is already on sale",
                    )
                else:
                    self.delete_drop_edition(
                        current_drop.id, current_drop_edition.edition_id
                    )
                    current_drop.drop_editions.remove(current_drop_edition)

    def update_drop_edition(
        self,
        current_drop_edition: DropEditionModel,
        updated_drop_edition: DropEditionModel,
    ) -> Tuple[DropEdition, str]:
        validate_price(updated_drop_edition.price)
        current_drop_edition.price = updated_drop_edition.price

    def delete_drop_edition(self, drop_id: int, edition_id: int) -> None:
        """Deletes a Drop edition by its drop_id and edition_id

        :param drop_id: int
        :param edition_id: int

        :return: None
        """
        drop_edition_model: DropEditionModel = self.get_drop_edition(
            drop_id, edition_id, include_drop=False, include_edition=False
        )
        drop_edition_model.delete()
