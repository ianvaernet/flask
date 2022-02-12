from http import HTTPStatus
from swagger_server.decorators.request_handler import request_handler
from swagger_server.models import ListNfts
from swagger_server.services import nft_service


@request_handler(
    [
        "status",
        "rarity",
        "reserved",
        "serie_id",
        "collection_id",
        "keyword",
        "page",
        "page_size",
    ]
)
def list_nfts(
    reserved=None,
    status=None,
    rarity=None,
    serie_id=None,
    collection_id=None,
    keyword=None,
    page=None,
    page_size=None,
) -> "tuple[ListNfts, HTTPStatus, None, None]":
    """Get the list of Nfts

    Get the list of all Nfts with support for filtering by reservation, status, rarity, serie_id or collection_id and searching by serial_number, Edition's name, Collection's name or short_word, Serie's name or short_word

    :param status: A comma separated list of status to filter by
    :type status: list[NftStatus]
    :param rarity:
    :type rarity: EditionRarity
    :param reserved:
    :type reserved: bool
    :param serie_id:
    :type serie_id: int
    :param collection_id:
    :type collection_id: int
    :param keyword:
    :type keyword: str
    :param page:
    :type page: int
    :param page_size:
    :type page_size: int

    :rtype: tuple[ListNfts, HTTPStatus, None, None]
    """
    filters = {
        "reserved": reserved,
        "status": status,
        "rarity": rarity,
        "serie_id": serie_id,
        "collection_id": collection_id,
    }
    nfts: ListNfts = nft_service.list_nfts(filters, keyword, page, page_size)
    return nfts, HTTPStatus.OK, None, None
