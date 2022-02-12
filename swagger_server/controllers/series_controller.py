import os
import connexion
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError
from swagger_server.database.models.serie import SerieModel
from swagger_server.exceptions.conflict_exception import ConflictException
from swagger_server.models import (
    Serie,
    ListSeries,
    CreateSerie,
    UpdateSerie,
)
from swagger_server.decorators import request_handler, logger
from swagger_server.models.serie_listable import SerieListable
from swagger_server.services import series_service
from swagger_server.util import to_listable_model
from swagger_server.__main__ import db
from swagger_server.extensions import scheduler


@request_handler(["status", "keyword", "page", "page_size"])
def list_series(
    status=None,
    keyword=None,
    page=None,
    page_size=None,
    order="desc",
    order_by="created_at",
) -> "tuple[ListSeries, HTTPStatus, None, None]":
    """Get the list of Series

    Get the list of all series with support for filtering by status and searching by name or short_word

    :param status:
    :type status: list[str]
    :param keyword:
    :type keyword: str
    :param page:
    :type page: int
    :param page_size:
    :type page_size: int
    :param order: str
    :param order_by: str

    :rtype: tuple[ListSeries, HTTPStatus, None, None]
    """
    filters = {"status": status}
    serie_models: list[SerieModel]
    total_pages: int
    serie_models, total_pages = series_service.list_series(
        filters, keyword, page, page_size, order, order_by
    )
    series: list[SerieListable] = []
    for serie_model in serie_models:
        serie = to_listable_model(serie_model.to_obj(format=True), SerieListable)
        series.append(serie)
    list_series = ListSeries(series=series, total_pages=total_pages)
    return list_series, HTTPStatus.OK, None, None


@request_handler(["body"])
def create_serie(body) -> "tuple[Serie, HTTPStatus, str, None]":
    """Create a new series

    Create a new draft serie inside the genies cms nft subsystem

    :param body: The series object to be created
    :type body: dict

    :rtype: tuple[Serie, HTTPStatus, str, None]
    """
    if connexion.request.is_json:
        body: CreateSerie = CreateSerie.from_dict(connexion.request.get_json())
        new_serie: SerieModel = SerieModel.from_obj(body)
        try:
            series_service.create_serie(new_serie)
            db.session.commit()
            created_serie = new_serie.to_obj(format=True)
            message: str = "Serie successfully created"
            return created_serie, HTTPStatus.CREATED, message, None
        except IntegrityError as error:
            db.session.rollback()
            if "for key 'short_word'" in str(error):
                raise ConflictException(
                    "There is a Serie with the same short_word",
                    "The Serie cannot be created because a Serie with the same short_word already exists",
                )
            else:
                raise error
        except Exception as error:
            db.session.rollback()
            raise error


@request_handler(["id", "format"])
def get_serie(id, format=True) -> "tuple[Serie, HTTPStatus, None, None]":
    """Get a serie

    Get a serie data based on its ID

    :param id: The serie id
    :type id: int
    :param format: Whether to format the response or not
    :type format: boolean

    :rtype: tuple[Serie, HTTPStatus, None, None]
    """
    serie_model: SerieModel = series_service.get_serie(id, include_collections=True)
    serie: Serie = serie_model.to_obj(include_collections=True, format=format)
    return serie, HTTPStatus.OK, None, None


@request_handler(["id", "body"])
def update_serie(body, id) -> "tuple[Serie, HTTPStatus, str, None]":
    """Update a serie

    Update a serie data, if it is a draft all data is updatable, but if it is published only off_chain_metadata can be updated

    :param body: The serie object to be updated
    :type body: dict
    :param id: The serie id
    :type id: int

    :rtype: tuple[Serie, HTTPStatus, str, None]
    """
    if connexion.request.is_json:
        body: UpdateSerie = UpdateSerie.from_dict(connexion.request.get_json())
        try:
            serie_model, message = series_service.update_serie(
                id, SerieModel.from_obj(body)
            )
            db.session.commit()
            updated_serie: Serie = serie_model.to_obj(format=True)
            if not message:
                message = "Serie successfully updated"
            return updated_serie, HTTPStatus.OK, message, None
        except IntegrityError as error:
            db.session.rollback()
            if "for key 'short_word'" in str(error):
                raise ConflictException(
                    "There is a Serie with the same short_word",
                    "The Serie cannot be updated because a Serie with the same short_word already exists",
                )
            else:
                raise error
        except Exception as error:
            db.session.rollback()
            raise error


@request_handler(["id"])
def delete_serie(id) -> "tuple[None, HTTPStatus, str, None]":
    """Delete a Serie

    Delete draft Serie

    :param id: The serie id
    :type id: int

    :rtype: tuple[None, HTTPStatus, str, None]
    """
    try:
        series_service.delete_serie(id)
        db.session.commit()
        message: str = "Serie successfully deleted"
        return None, HTTPStatus.OK, message, None
    except Exception as error:
        db.session.rollback()
        raise error


@logger()
@request_handler(["id"])
def publish_serie(id) -> "tuple[None, HTTPStatus, str, None]":
    """Publish a serie

    Publish a serie to the Dapper system

    :param id: The serie id to be published
    :type id: int

    :rtype: SuccessResponse
    """
    try:
        if os.environ.get("SCHEDULER") == "True":
            with scheduler.app.app_context():
                series_service.publish_serie(id)
                db.session.commit()
        else:
            series_service.publish_serie(id)
            db.session.commit()
        message = "Serie successfully published"
        return None, HTTPStatus.OK, message, None
    except Exception as error:
        db.session.rollback()
        raise error
