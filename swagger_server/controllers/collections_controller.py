import os
import connexion
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError
from swagger_server.database.models.collection import CollectionModel
from swagger_server.exceptions.bad_request_exception import BadRequestException
from swagger_server.exceptions.conflict_exception import ConflictException
from swagger_server.models import (
    CreateCollection,
    Collection,
    ListCollections,
    UpdateCollection,
)
from swagger_server.decorators import request_handler, logger
from swagger_server.models.collection_listable import CollectionListable
from swagger_server.services import collections_service
from swagger_server.util import to_listable_model
from swagger_server.__main__ import db
from swagger_server.extensions import scheduler


@request_handler(["status", "serie_id", "keyword", "page", "page_size"])
def list_collections(
    status=None,
    serie_id=None,
    keyword=None,
    page=None,
    page_size=None,
    order="desc",
    order_by="created_at",
) -> "tuple[ListCollections, HTTPStatus, None, None]":
    """Get the list of collections

    Get the list of all collections with support for filtering by status or serie_id and searching by name or short_word

    :param status:
    :type status: list[str]
    :param serie_id:
    :type serie_id: int
    :param serch:
    :type serch: str
    :param page:
    :type page: int
    :param page_size:
    :type page_size: int
    :param order: str
    :param order_by: str

    :rtype: tuple[ListCollections, HTTPStatus, None, None]
    """
    filters = {"status": status, "serie_id": serie_id}
    collection_models: list[CollectionModel]
    total_pages: int
    collection_models, total_pages = collections_service.list_collections(
        filters, keyword, page, page_size, order, order_by
    )
    collections: list[CollectionListable] = []
    for collection_model in collection_models:
        collection = to_listable_model(
            collection_model.to_obj(format=True), CollectionListable
        )
        collections.append(collection)
    list_collections = ListCollections(collections=collections, total_pages=total_pages)
    return list_collections, HTTPStatus.OK, None, None


@request_handler(["body"])
def create_collection(body) -> "tuple[Collection, HTTPStatus, str, None]":
    """Create a new collection

    Create a new draft collection inside the genies cms nft subsystem

    :param body: The collection object to be created
    :type body: dict

    :rtype: tuple[Collection, HTTPStatus, str, None]
    """
    if connexion.request.is_json:
        body: CreateCollection = CreateCollection.from_dict(
            connexion.request.get_json()
        )
        new_collection: CollectionModel = CollectionModel.from_obj(body)
        try:
            collections_service.create_collection(new_collection)
            db.session.commit()
            created_collection = new_collection.to_obj(format=True)
            message: str = "Collection successfully created"
            return created_collection, HTTPStatus.CREATED, message, None
        except IntegrityError as error:
            db.session.rollback()
            if "FOREIGN KEY (`serie_id`)" in str(error):
                raise BadRequestException(
                    title="Invalid serie_id",
                    detail="The Collection cannot be created because there is no Serie with the provided id",
                )
            elif "for key 'short_word'" in str(error):
                raise ConflictException(
                    "There is a Collection with the same short_word",
                    "The Collection cannot be created because a Collection with the same_short word already exists",
                )
            else:
                raise error
        except Exception as error:
            db.session.rollback()
            raise error


@request_handler(["id", "format"])
def get_collection(id, format=True) -> "tuple[Collection, HTTPStatus, None, None]":
    """Get a collections

    Get a collection data based on its ID

    :param id: The Collection id
    :type id: int
    :param format: Whether to format the response or not
    :type format: boolean

    :rtype: tuple[Collection, HTTPStatus, None, None]
    """
    collection_model: CollectionModel = collections_service.get_collection(
        id, include_serie=True, include_editions=True
    )
    collection: Collection = collection_model.to_obj(
        include_serie=True, include_editions=True, format=format
    )
    return collection, HTTPStatus.OK, None, None


@request_handler(["id", "body"])
def update_collection(body, id) -> "tuple[Collection, HTTPStatus, str, None]":
    """Update a collection

    Update a collection data, if it is a draft all data is updatable, but if it is published only off_chain_metadata can be updated

    :param body: The collection object to be updated
    :type body: dict
    :param id: The collection id
    :type id: int

    :rtype: tuple[Collection, HTTPStatus, str, None]
    """
    if connexion.request.is_json:
        body: UpdateCollection = UpdateCollection.from_dict(
            connexion.request.get_json()
        )
        try:
            collection_model, message = collections_service.update_collection(
                id,
                CollectionModel.from_obj(body),
                wearables_count_difference=body.wearables_count_difference,
            )
            db.session.commit()
            updated_collection: Collection = collection_model.to_obj(format=True)
            if not message:
                message = "Collection successfully updated"
            return updated_collection, HTTPStatus.OK, message, None
        except IntegrityError as error:
            db.session.rollback()
            if "FOREIGN KEY (`serie_id`)" in str(error):
                raise BadRequestException(
                    title="Invalid serie_id",
                    detail="The Collection cannot be updated because there is no Serie with the provided id",
                )
            elif "for key 'short_word'" in str(error):
                raise ConflictException(
                    "There is a Collection with the same short_word",
                    "The Collection cannot be updated because a Collection with the same_short word already exists",
                )
            else:
                raise error
        except Exception as error:
            db.session.rollback()
            raise error


@request_handler(["id"])
def delete_collection(id) -> "tuple[None, HTTPStatus, str, None]":
    """Delete a collection

    Delete draft collection

    :param id: The collection id
    :type id: int

    :rtype: tuple[None, HTTPStatus, str, None]
    """
    try:
        collections_service.delete_collection(id)
        db.session.commit()
        message: str = "Collection successfully deleted"
        return None, HTTPStatus.OK, message, None
    except Exception as error:
        db.session.rollback()
        raise error


@logger()
@request_handler(["id"])
def publish_collection(id) -> "tuple[None, HTTPStatus, str, None]":
    """Publish a collection

    Publish a collection to the Dapper system

    :param id: The collection id to be published
    :type id: int

    :rtype: SuccessResponse
    """
    try:
        if os.environ.get("SCHEDULER") == "True":
            with scheduler.app.app_context():
                collections_service.publish_collection(id)
                db.session.commit()
        else:
            collections_service.publish_collection(id)
            db.session.commit()
        message = "Collection successfully published"
        return None, HTTPStatus.OK, message, None
    except Exception as error:
        db.session.rollback()
        raise error
