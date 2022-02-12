import connexion
import six

from swagger_server.services import data_definition_service
from http import HTTPStatus
from swagger_server import util
from swagger_server.decorators import request_handler, logger
from swagger_server.models import (
    EditionDesignSlot,
    EditionRarity,
    EditionTypes,
    Enumerations,
)


@logger()
@request_handler()
def list_edition_design_slot_enumerations() -> "tuple[EditionDesignSlot, HTTPStatus, None, None]":
    """Get the list of all dapper edition design slots enumerations
    Get the list of all dapper edition design slots enumerations # noqa: E501
    :rtype: tuple[EditionDesignSlot, HTTPStatus, None, None]
    """
    data: dict = data_definition_service.get_edition_design_slots()
    return data, HTTPStatus.OK, None, None


@logger()
@request_handler()
def list_edition_rarity_enumerations() -> "tuple[EditionRarity, HTTPStatus, None, None]":
    """Get the list of all dapper edition rarity enumerations
    Get the list of all dapper edition rarity enumerations # noqa: E501
    :rtype: tuple[EditionRarity, HTTPStatus, None, None]
    """
    data: dict = data_definition_service.get_edition_rarity()
    return data, HTTPStatus.OK, None, None


@logger()
@request_handler()
def list_edition_type_enumerations() -> "tuple[EditionTypes, HTTPStatus, None, None]":
    """Get the list of all dapper edition types enumerations
    Get the list of all dapper edition types enumerations # noqa: E501
    :rtype: tuple[EditionTypes, HTTPStatus, None, None]
    """
    data: dict = data_definition_service.get_edition_type()
    return data, HTTPStatus.OK, None, None


@logger()
@request_handler()
def list_enumerations() -> "tuple[Enumerations, HTTPStatus, None, None]":
    """Get the list of all dapper enumerations
    Get the list of all dapper enumerations # noqa: E501
    :rtype: tuple[Enumerations, HTTPStatus, None, None]
    """
    data: dict = data_definition_service.get_enumerations()
    return data, HTTPStatus.OK, None, None
