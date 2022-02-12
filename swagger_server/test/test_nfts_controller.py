# coding: utf-8

from __future__ import absolute_import
from swagger_server.database.models import (
    SerieModel,
    CollectionModel,
    EditionModel,
    NftModel,
)
from swagger_server.database.enums import EditionRarity, NftStatus
from swagger_server.__main__ import db


def test_init():
    db.drop_all()
    db.create_all()


def test_list_nfts_pagination(client, auth_header):
    """Test case for list_nfts pagination"""
    page_size = 2
    serie_id = SerieModel.factory().id
    collection_id = CollectionModel.factory(keys={"serie_id": serie_id}).id
    edition_id = EditionModel.factory(keys={"collection_id": collection_id}).id
    NftModel.factory(keys={"edition_id": edition_id})
    NftModel.factory(keys={"edition_id": edition_id})
    NftModel.factory(keys={"edition_id": edition_id})
    query_string = [("page_size", page_size), ("page", 1)]
    response = client.get("/v1/nfts", query_string=query_string, headers=auth_header)
    nfts_list = response.json["data"]["nfts"]
    assert response.status_code == 200
    assert response.json["data"]["total_pages"] > 0
    assert len(nfts_list) > 0
    assert len(nfts_list) <= page_size


def test_list_nfts_filters(client, auth_header):
    """Test case for list_nfts filters"""
    serial_number = 1234
    reserved = True
    status = NftStatus.MINTED
    rarity = EditionRarity.EDITION_RARITY_RARE.value
    serie_id = SerieModel.factory().id
    serie_id_2 = SerieModel.factory().id
    collection_id = CollectionModel.factory(keys={"serie_id": serie_id}).id
    collection_id_2 = CollectionModel.factory(keys={"serie_id": serie_id_2}).id
    edition_id = EditionModel.factory(
        keys={"collection_id": collection_id, "rarity": rarity}
    ).id
    edition_id_2 = EditionModel.factory(
        keys={"collection_id": collection_id_2, "rarity": rarity}
    ).id
    edition_id_3 = EditionModel.factory(
        keys={
            "collection_id": collection_id,
            "rarity": EditionRarity.EDITION_RARITY_STANDARD.value,
        }
    ).id
    NftModel.factory(
        keys={
            "dapper_flow_id": serial_number * 1,
            "reserved": reserved,
            "status": status,
            "edition_id": edition_id,
        }
    )
    NftModel.factory(
        keys={
            "dapper_flow_id": serial_number * 10,
            "reserved": False,
            "status": status,
            "edition_id": edition_id,
        }
    )
    NftModel.factory(
        keys={
            "dapper_flow_id": serial_number * 100,
            "reserved": reserved,
            "status": NftStatus.GIFTED,
            "edition_id": edition_id,
        }
    )
    NftModel.factory(
        keys={
            "dapper_flow_id": serial_number * 1000,
            "reserved": reserved,
            "status": status,
            "edition_id": edition_id_2,
        }
    )
    NftModel.factory(
        keys={
            "dapper_flow_id": serial_number * 10000,
            "reserved": reserved,
            "status": status,
            "edition_id": edition_id_3,
        }
    )
    query_string = [
        ("keyword", serial_number),
        ("reserved", reserved),
        ("status", status.value),
        ("rarity", rarity),
        ("serie_id", serie_id),
        ("collection_id", collection_id),
    ]
    response = client.get("/v1/nfts", query_string=query_string, headers=auth_header)
    nfts_list = response.json["data"]["nfts"]
    assert response.status_code == 200
    assert len(nfts_list) == 1


def test_list_nfts_search_by_edition_name(client, auth_header):
    """Test case for list_nfts search by Edition's name"""
    edition_name = "test_list_nfts_search_by_edition_name"
    serie_id = SerieModel.factory().id
    collection_id = CollectionModel.factory(keys={"serie_id": serie_id}).id
    edition_id = EditionModel.factory(
        keys={"collection_id": collection_id, "name": edition_name}
    ).id
    edition_id_2 = EditionModel.factory(keys={"collection_id": collection_id}).id
    NftModel.factory(keys={"edition_id": edition_id})
    NftModel.factory(keys={"edition_id": edition_id_2})
    query_string = [("keyword", edition_name)]
    response = client.get("/v1/nfts", query_string=query_string, headers=auth_header)
    nfts_list = response.json["data"]["nfts"]
    assert response.status_code == 200
    assert len(nfts_list) == 1


def test_list_nfts_search_by_collection_name(client, auth_header):
    """Test case for list_nfts search by Collection's name"""
    collection_name = "test_list_nfts_search_by_collection_name"
    serie_id = SerieModel.factory().id
    collection_id = CollectionModel.factory(
        keys={"serie_id": serie_id, "name": collection_name}
    ).id
    collection_id_2 = CollectionModel.factory(keys={"serie_id": serie_id}).id
    edition_id = EditionModel.factory(keys={"collection_id": collection_id}).id
    edition_id_2 = EditionModel.factory(keys={"collection_id": collection_id_2}).id
    NftModel.factory(keys={"edition_id": edition_id})
    NftModel.factory(keys={"edition_id": edition_id_2})
    query_string = [("keyword", collection_name)]
    response = client.get("/v1/nfts", query_string=query_string, headers=auth_header)
    nfts_list = response.json["data"]["nfts"]
    assert response.status_code == 200
    assert len(nfts_list) == 1


def test_list_nfts_search_by_collection_short_word(client, auth_header):
    """Test case for list_nfts search by Collection's short_word"""
    collection_short_word = "test_list_nfts_search_by_collection_short_word"
    serie_id = SerieModel.factory().id
    collection_id = CollectionModel.factory(
        keys={"serie_id": serie_id, "short_word": collection_short_word}
    ).id
    collection_id_2 = CollectionModel.factory(keys={"serie_id": serie_id}).id
    edition_id = EditionModel.factory(keys={"collection_id": collection_id}).id
    edition_id_2 = EditionModel.factory(keys={"collection_id": collection_id_2}).id
    NftModel.factory(keys={"edition_id": edition_id})
    NftModel.factory(keys={"edition_id": edition_id_2})
    query_string = [("keyword", collection_short_word)]
    response = client.get("/v1/nfts", query_string=query_string, headers=auth_header)
    nfts_list = response.json["data"]["nfts"]
    assert response.status_code == 200
    assert len(nfts_list) == 1


def test_list_nfts_search_by_serie_name(client, auth_header):
    """Test case for list_nfts search by Serie's name"""
    serie_name = "test_list_nfts_search_by_serie_name"
    serie_id = SerieModel.factory(keys={"name": serie_name}).id
    serie_id_2 = SerieModel.factory().id
    collection_id = CollectionModel.factory(keys={"serie_id": serie_id}).id
    collection_id_2 = CollectionModel.factory(keys={"serie_id": serie_id_2}).id
    edition_id = EditionModel.factory(keys={"collection_id": collection_id}).id
    edition_id_2 = EditionModel.factory(keys={"collection_id": collection_id_2}).id
    NftModel.factory(keys={"edition_id": edition_id})
    NftModel.factory(keys={"edition_id": edition_id_2})
    query_string = [("keyword", serie_name)]
    response = client.get("/v1/nfts", query_string=query_string, headers=auth_header)
    nfts_list = response.json["data"]["nfts"]
    assert response.status_code == 200
    assert len(nfts_list) == 1


def test_list_nfts_search_by_serie_short_word(client, auth_header):
    """Test case for list_nfts search by Serie's short_word"""
    serie_short_word = "test_list_nfts_search_by_serie_short_word"
    serie_id = SerieModel.factory(keys={"short_word": serie_short_word}).id
    serie_id_2 = SerieModel.factory().id
    collection_id = CollectionModel.factory(keys={"serie_id": serie_id}).id
    collection_id_2 = CollectionModel.factory(keys={"serie_id": serie_id_2}).id
    edition_id = EditionModel.factory(keys={"collection_id": collection_id}).id
    edition_id_2 = EditionModel.factory(keys={"collection_id": collection_id_2}).id
    NftModel.factory(keys={"edition_id": edition_id})
    NftModel.factory(keys={"edition_id": edition_id_2})
    query_string = [("keyword", serie_short_word)]
    response = client.get("/v1/nfts", query_string=query_string, headers=auth_header)
    nfts_list = response.json["data"]["nfts"]
    assert response.status_code == 200
    assert len(nfts_list) == 1
