import os
import connexion
from typing import List
from http import HTTPStatus
from swagger_server.database.enums.drop_status import DropStatus
from swagger_server.database.models.drop import DropModel
from swagger_server.database.models.drop_edition import DropEditionModel
from swagger_server.models import (
    CreateDrop,
    Drop,
    ListDrops,
    UpdateDrop,
)
from swagger_server.decorators import request_handler, logger
from swagger_server.models.drop_listable import DropListable
from swagger_server.services import drops_service
from swagger_server.util import to_listable_model
from swagger_server.__main__ import db
from swagger_server.extensions import scheduler


@request_handler(["status", "keyword", "page", "page_size"])
def list_drops(
    status=None,
    keyword=None,
    page=None,
    page_size=None,
    order="desc",
    order_by="created_at",
) -> "tuple[ListDrops, HTTPStatus, None, None]":
    """Get the list of drops

    Get the list of all drops with support for filtering by status and searching by title

    :param status:
    :type status: list[str]
    :param serch:
    :type serch: str
    :param page:
    :type page: int
    :param page_size:
    :type page_size: int
    :param order: str
    :param order_by: str

    :rtype: tuple[ListDrops, HTTPStatus, None, None]
    """
    filters = {"status": status}
    drop_models: List[DropModel]
    total_pages: int
    drop_models, total_pages = drops_service.list_drops(
        filters, keyword, page, page_size, order, order_by
    )
    drops: List[DropListable] = []
    for drop_model in drop_models:
        drop = to_listable_model(drop_model.to_obj(format=True), DropListable)
        drops.append(drop)
    list_drops = ListDrops(drops=drops, total_pages=total_pages)
    return list_drops, HTTPStatus.OK, None, None


@request_handler(["body"])
def create_drop(body) -> "tuple[Drop, HTTPStatus, str, None]":
    """Create a new drop

    Create a new draft drop inside the genies cms nft subsystem

    :param body: The drop object to be created
    :type body: dict

    :rtype: tuple[Drop, HTTPStatus, str, None]
    """
    if connexion.request.is_json:
        body = CreateDrop.from_dict(connexion.request.get_json())
        new_drop: DropModel = DropModel.from_obj(body)
        drop_editions: list[DropEditionModel] = None
        if body.drop_editions is not None:
            drop_editions = []
            for drop_edition in body.drop_editions:
                drop_editions.append(
                    DropEditionModel(
                        edition_id=drop_edition.edition_id,
                        price=drop_edition.price,
                    )
                )
        try:
            drops_service.create_drop(new_drop, drop_editions)
            db.session.commit()
            created_drop: Drop = new_drop.to_obj(format=True)
            message: str = "Drop successfully created"
            return created_drop, HTTPStatus.CREATED, message, None
        except Exception as error:
            db.session.rollback()
            raise error


@request_handler(["id", "format"])
def get_drop(id, format=True) -> "tuple[Drop, HTTPStatus, None, None]":
    """Get a drop

    Get a drop data based on its ID

    :param id: The drop id
    :type id: int
    :param format: Whether to format the response or not
    :type format: boolean

    :rtype: tuple[Drop, HTTPStatus, None, None]
    """
    drop_model: DropModel = drops_service.get_drop(id, include_editions=True)
    drop: Drop = drop_model.to_obj(include_editions=True, format=format)
    return drop, HTTPStatus.OK, None, None


@request_handler(["id", "body"])
def update_drop(body, id) -> "tuple[Drop, HTTPStatus, str, None]":
    """Update a drop

    Update a drop data, if it's a draft all data is updatable

    :param body: The drop object to be updated
    :type body: dict
    :param id: The drop id
    :type id: int

    :rtype: tuple[Drop, HTTPStatus, str, None]
    """
    if connexion.request.is_json:
        body = UpdateDrop.from_dict(connexion.request.get_json())
        drop_editions: list[DropEditionModel] = None
        if body.drop_editions is not None:
            drop_editions = []
            for drop_edition in body.drop_editions:
                drop_editions.append(
                    DropEditionModel(
                        drop_id=id,
                        edition_id=drop_edition.edition_id,
                        price=drop_edition.price,
                    )
                )
        try:
            drop_model, message = drops_service.update_drop(
                id, DropModel.from_obj(body), drop_editions
            )
            db.session.commit()
            updated_drop: Drop = drop_model.to_obj(format=True)
            if not message:
                message = "Drop successfully updated"
            return updated_drop, HTTPStatus.OK, message, None
        except Exception as error:
            db.session.rollback()
            raise error


@request_handler(["id"])
def delete_drop(id) -> "tuple[None, HTTPStatus, str, None]":
    """Delete a drop

    Delete draft drop

    :param id: The drop id
    :type id: int

    :rtype: tuple[None, HTTPStatus, str, None]
    """
    try:
        drops_service.delete_drop(id)
        db.session.commit()
        message: str = "Drop successfully deleted"
        return None, HTTPStatus.OK, message, None
    except Exception as error:
        db.session.rollback()
        raise error


@logger()
@request_handler(["id"])
def publish_drop(id) -> "tuple[None, HTTPStatus, str, None]":
    """Publish a drop

    Publish a drop to the Dapper system

    :param id: The drop id to be published
    :type id: int

    :rtype: SuccessResponse
    """
    try:
        if os.environ.get("SCHEDULER") == "True":
            with scheduler.app.app_context():
                drops_service.publish_drop(id)
                db.session.commit()
        else:
            drops_service.publish_drop(id)
            db.session.commit()
        message = "Drop successfully published"
        return None, HTTPStatus.OK, message, None
    except Exception as error:
        db.session.rollback()
        raise error


@logger()
def update_drop_status(id: int, updated_drop_status: DropStatus):
    """Sets the status of a Drop to ON_SALE (method used by the scheduler)

    :param id: int

    :return: None
    """
    if os.environ.get("SCHEDULER") == "True":
        with scheduler.app.app_context():
            drops_service.update_drop(
                id, DropModel(status=DropStatus(updated_drop_status))
            )
            db.session.commit()
    else:
        drops_service.update_drop(id, DropModel(status=DropStatus(updated_drop_status)))
        db.session.commit()
