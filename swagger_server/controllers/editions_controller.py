import os
import connexion
from typing import List
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError
from swagger_server.database.models import EditionModel, EditionErrorModel
from swagger_server.exceptions.bad_request_exception import BadRequestException
from swagger_server.exceptions.forbidden_exception import ForbiddenException
from swagger_server.models import (
    BatchUpdateEditions,
    CreateEdition,
    Edition,
    EditionError,
    EditionListable,
    ListEditions,
    ListEditionErrors,
    Mint,
    UpdateEdition,
)
from swagger_server.decorators import request_handler, logger
from swagger_server.services import editions_service
from swagger_server.util import to_listable_model
from swagger_server.__main__ import db
from swagger_server.extensions import scheduler


@request_handler(
    [
        "status",
        "available",
        "rarity",
        "type",
        "design_slot",
        "min_price",
        "max_price",
        "avatar_wearable_id",
        "keyword",
        "page",
        "page_size",
        "format",
    ]
)
def list_editions(
    status=None,
    available=None,
    rarity=None,
    type=None,
    design_slot=None,
    min_price=None,
    max_price=None,
    avatar_wearable_id=None,
    keyword=None,
    page=None,
    page_size=None,
    format=True,
    order="desc",
    order_by="created_at",
) -> "tuple[ListEditions, HTTPStatus, None, None]":
    """Get the list of Editions

    Get the list of all Editions with support for filtering by status, availability, rarity, type, design_slot, min_price, max_price or avatar_wearable_id and searching by name, artist, celebrity, publisher, trademark or avatar_wearable_sku

    :param status:
    :type status: list[str]
    :param available:
    :type available: bool
    :param rarity:
    :type rarity: str
    :param type:
    :type type: str
    :param design_slot:
    :type design_slot: str
    :param min_price:
    :type min_price: float
    :param max_price:
    :type max_price: float
    :param avatar_wearable_id:
    :type avatar_wearable_id: int
    :param keyword:
    :type keyword: str
    :param page:
    :type page: int
    :param page_size:
    :type page_size: int
    :param format:
    :type format: bool
    :param order: str
    :param order_by: str

    :rtype: tuple[ListEditions, HTTPStatus, None, None]
    """
    filters = {
        "status": status,
        "available": available,
        "rarity": rarity,
        "type": type,
        "design_slot": design_slot,
        "min_price": min_price,
        "max_price": max_price,
        "avatar_wearable_id": avatar_wearable_id,
    }
    edition_models: list[EditionModel]
    total_pages: int
    edition_models, total_pages = editions_service.list_editions(
        filters, keyword, page, page_size, order, order_by
    )
    editions: List[EditionListable] = []
    for edition_model in edition_models:
        edition = to_listable_model(
            edition_model.to_obj(include_collection=False, format=format),
            EditionListable,
        )
        editions.append(edition)
    list_editions = ListEditions(editions=editions, total_pages=total_pages)
    return list_editions, HTTPStatus.OK, None, None


@request_handler(["body"])
def create_edition(body) -> "tuple[Edition, HTTPStatus, str, None]":
    """Create a new Edition

    Create a new Edition in draft state.

    :param body: Edition object
    :type body: dict

    :rtype: tuple[Edition, HTTPStatus, str, None]
    """
    if connexion.request.is_json:
        body = CreateEdition.from_dict(connexion.request.get_json())
        new_edition = EditionModel.from_obj(body)
        try:
            editions_service.create_edition(new_edition)
            db.session.commit()
            created_edition: Edition = new_edition.to_obj(format=True)
            message: str = "Edition successfully created"
            return created_edition, HTTPStatus.CREATED, message, None
        except IntegrityError as error:
            db.session.rollback()
            if "FOREIGN KEY (`collection_id`)" in str(error):
                raise BadRequestException(
                    title="Invalid Collection id",
                    detail="The Edition cannot be created because there is no Collection with the provided id",
                )
            else:
                raise error
        except Exception as error:
            db.session.rollback()
            raise error


@request_handler(["id", "format"])
def get_edition(id, format=True) -> "tuple[Edition, HTTPStatus, None, None]":
    """Get the data of an specific edition

    Get all the details from an specific edition

    :param id: The edition id
    :type id: int
    :param format: Whether to format the response or not
    :type format: boolean

    :rtype: tuple[Edition, HTTPStatus, None, None]
    """
    edition_model: Edition = editions_service.get_edition(
        id, include_collection=True, include_drops=True, include_nfts=True
    )
    edition: Edition = edition_model.to_obj(
        include_collection=True,
        include_drops=True,
        include_nfts=True,
        format=format,
    )
    return edition, HTTPStatus.OK, None, None


@request_handler(["id", "body"])
def update_edition(body, id) -> "tuple[Edition, HTTPStatus, str, None]":
    """Update an Edition

    Update an Edition data, if it is a draft, all data is updatable, but if it is published only offChainMetadata can be updated.

    :param body: Edition object
    :type body: dict
    :param id: The edition id
    :type id: int

    :rtype: tuple[Edition, HTTPStatus, str, None]
    """
    if connexion.request.is_json:
        body = UpdateEdition.from_dict(connexion.request.get_json())
        try:
            edition_model, message = editions_service.update_edition(
                id, EditionModel.from_obj(body)
            )
            db.session.commit()
            updated_edition: Edition = edition_model.to_obj(format=True)
            if not message:
                message = "Edition successfully updated"
            return updated_edition, HTTPStatus.OK, message, None
        except IntegrityError as error:
            db.session.rollback()
            if "FOREIGN KEY (`collection_id`)" in str(error):
                raise BadRequestException(
                    title="Invalid Collection id",
                    detail="The Edition cannot be updated because there is no Collection with the provided id",
                )
            else:
                raise error
        except Exception as error:
            db.session.rollback()
            raise error


@request_handler(["body"])
def batch_update_editions(body) -> "tuple[None, HTTPStatus, str, None]":
    """Update Editions by avatar_wearable_id

    Update the collection_id and asset short_word of all the Editions with that avatar_wearable_id.

    :param body: avatar_wearable_id and updated fields (collection_id and short_word)
    :type body: dict

    :rtype: tuple[None, HTTPStatus, str, None]
    """
    if connexion.request.is_json:
        body = BatchUpdateEditions.from_dict(connexion.request.get_json())
        try:
            message = editions_service.batch_update_editions(body)
            db.session.commit()
            return None, HTTPStatus.OK, message, None
        except Exception as error:
            db.session.rollback()
            raise error


@request_handler(["id"])
def delete_edition(id) -> "tuple[None, HTTPStatus, str, None]":
    """Delete an Edition

    Delete draft Edition

    :param id: The edition id
    :type id: int

    :rtype: tuple[None, HTTPStatus, str, None]
    """
    try:
        editions_service.delete_edition(id)
        db.session.commit()
        message: str = "Edition successfully deleted"
        return None, HTTPStatus.OK, message, None
    except IntegrityError as error:
        db.session.rollback()
        if "key column 'drop_editions.edition_id'" in str(error):
            raise ForbiddenException(
                "Edition is part of a Drop",
                "The Edition cannot be deleted because it is part of a Drop",
            )
        else:
            raise error
    except Exception as error:
        db.session.rollback()
        raise error


@logger()
@request_handler(["id"])
def publish_edition(id) -> "tuple[None, HTTPStatus, str, None]":
    """Publish an edition

    Publish an edition to the Dapper system, this will block the onchain metadata.

    :param id: The edition id to be published
    :type id: int

    :rtype: SuccessResponse
    """
    try:
        if os.environ.get("SCHEDULER") == "True":
            with scheduler.app.app_context():
                editions_service.publish_edition(id)
                db.session.commit()
        else:
            editions_service.publish_edition(id)
            db.session.commit()
        message: str = "Edition successfully published"
        return None, HTTPStatus.OK, message, None
    except Exception as error:
        db.session.rollback()
        raise error


@logger()
@request_handler(["id", "body"])
def mint_nft(body, id):
    """Mint an NFT

    Mint an specific amount of one edition based on it's id

    :param body: The quantity of edition structures to be minted
    :type body: dict
    :param id: The edition id
    :type id: int

    :rtype: SuccessResponse
    """
    if connexion.request.is_json:
        body = Mint.from_dict(connexion.request.get_json())
    try:
        edition = editions_service.get_edition(id=id)
        editions_service.mint(
            edition=edition,
            quantity=body.quantity,
        )
        db.session.commit()
        message: str = "Edition successfully minted"
        return None, HTTPStatus.OK, message, None
    except Exception as error:
        db.session.rollback()
        raise error


@logger()
@request_handler(["id", "page", "page_size"])
def list_edition_errors(
    id: int, page: int = None, page_size: int = None
) -> "tuple[ListEditionErrors, HTTPStatus, None, None]":
    """Get the errors of an Edition

    :param id: The Edition's id
    :type id: int

    :rtype: tuple[ListEditionErrors, HTTPStatus, None, None]
    """
    filters = {"edition_id": id}
    edition_error_models: list[EditionErrorModel]
    total_pages: int
    edition_error_models, total_pages = editions_service.list_errors(
        filters, page, page_size
    )
    edition_errors: List[EditionError] = list(
        map(
            lambda edition_error_model: edition_error_model.to_obj(),
            edition_error_models,
        )
    )
    list_edition_errors = ListEditionErrors(
        edition_errors=edition_errors, total_pages=total_pages
    )
    return list_edition_errors, HTTPStatus.OK, None, None
