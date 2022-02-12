# coding: utf-8
from __future__ import absolute_import
from time import sleep
from flask import json
from swagger_server.database.enums import (
    DesignSlot,
    EditionRarity,
    EditionStatus,
    EditionType,
)
from swagger_server.database.enums.collection_status import CollectionStatus
from swagger_server.database.models import (
    EditionModel,
    CollectionModel,
    SerieModel,
)
from swagger_server.database.models.assets_extras import AssetsExtras
from swagger_server.database.models.drop import DropModel
from swagger_server.database.models.drop_edition import DropEditionModel
from swagger_server.database.models.edition_error import EditionErrorModel
from swagger_server.models import (
    CreateEdition,
    CreateOrUpdateEditionOnChainMetadata,
    EditionOffChainMetadata,
    Mint,
    BatchUpdateEditions,
)
from datetime import datetime, timedelta, timezone
from swagger_server.models.update_edition import UpdateEdition
from swagger_server.services import scheduler_service
from swagger_server.util import deserialize_datetime, format_datetime, format_price
from swagger_server.__main__ import db


def test_init():
    db.drop_all()
    db.create_all()


def test_list_editions_pagination(client, auth_header):
    """Test case for list_editions pagination"""
    page_size = 2
    EditionModel.factory()
    EditionModel.factory()
    EditionModel.factory()
    query_string = [("page_size", page_size), ("page", 1)]
    response = client.get(
        "/v1/editions", query_string=query_string, headers=auth_header
    )
    editions_list = response.json["data"]["editions"]
    assert response.status_code == 200
    assert response.json["data"]["total_pages"] > 0
    assert len(editions_list) > 0
    assert len(editions_list) <= page_size


def test_list_editions_filters(client, auth_header):
    """Test case for list_editions filters"""
    status = [EditionStatus.CREATED.value, EditionStatus.ON_SALE.value]
    rarity = EditionRarity.EDITION_RARITY_LEGENDARY
    type = EditionType.EDITION_TYPE_AVATAR_WEARABLE
    design_slot = DesignSlot.EDITION_DESIGN_SLOT_HELMET
    min_price = 5
    max_price = min_price + 5
    avatar_wearable_id = 7
    EditionModel.factory(
        keys={
            "status": status[0],
            "rarity": rarity,
            "type": type,
            "design_slot": design_slot,
            "price": min_price,
            "avatar_wearable_id": avatar_wearable_id,
        }
    )
    EditionModel.factory(
        keys={
            "status": status[1],
            "rarity": rarity,
            "type": type,
            "design_slot": design_slot,
            "price": max_price,
            "avatar_wearable_id": avatar_wearable_id,
        }
    )
    EditionModel.factory(
        keys={
            "status": EditionStatus.DRAFT,
            "rarity": rarity,
            "type": type,
            "design_slot": design_slot,
            "price": min_price,
            "avatar_wearable_id": avatar_wearable_id,
        }
    )
    EditionModel.factory(
        keys={
            "status": status[0],
            "rarity": EditionRarity.EDITION_RARITY_RARE,
            "type": type,
            "design_slot": design_slot,
            "price": min_price,
            "avatar_wearable_id": avatar_wearable_id,
        }
    )
    EditionModel.factory(
        keys={
            "status": status[1],
            "rarity": rarity,
            "type": EditionType.EDITION_TYPE_AVATAR_STATUE,
            "design_slot": design_slot,
            "price": min_price,
            "avatar_wearable_id": avatar_wearable_id,
        }
    )
    EditionModel.factory(
        keys={
            "status": status[0],
            "rarity": rarity,
            "type": type,
            "design_slot": DesignSlot.EDITION_DESIGN_SLOT_JACKET,
            "price": min_price,
            "avatar_wearable_id": avatar_wearable_id,
        }
    )
    EditionModel.factory(
        keys={
            "status": status[1],
            "rarity": rarity,
            "type": type,
            "design_slot": design_slot,
            "price": min_price - 1,
            "avatar_wearable_id": avatar_wearable_id,
        }
    )
    EditionModel.factory(
        keys={
            "status": status[0],
            "rarity": rarity,
            "type": type,
            "design_slot": design_slot,
            "price": max_price + 1,
            "avatar_wearable_id": avatar_wearable_id,
        }
    )
    query_string = [
        ("status", ",".join(status)),
        ("rarity", rarity.value),
        ("type", type.value),
        ("design_slot", design_slot.value),
        ("min_price", min_price),
        ("max_price", max_price),
        ("avatar_wearable_id", avatar_wearable_id),
    ]
    response = client.get(
        "/v1/editions", query_string=query_string, headers=auth_header
    )
    editions_list = response.json["data"]["editions"]
    assert response.status_code == 200
    assert len(editions_list) == 2


def test_list_available_editions(client, auth_header):
    """Test case for list_editions available filter"""
    name = "test_list_available_editions"
    EditionModel.factory(
        keys={"name": name + "1", "status": EditionStatus.DRAFT},
        has_one={"collection_id": CollectionModel},
    )
    EditionModel.factory(
        keys={"name": name + "2", "status": EditionStatus.CREATED},
        has_one={"collection_id": CollectionModel},
    )
    EditionModel.factory(
        keys={"name": name + "3", "status": EditionStatus.MINTED},
        has_one={"collection_id": CollectionModel},
    )
    available_edition_id: int = EditionModel.factory(
        keys={"name": name + "4", "status": EditionStatus.ON_SALE},
        has_one={"collection_id": CollectionModel},
    ).id
    edition_in_drop: EditionModel = EditionModel.factory(
        keys={"name": name + "5", "status": EditionStatus.ON_SALE}
    ).id
    drop: DropModel = DropModel.factory()
    DropEditionModel.factory(
        keys={"drop_id": drop.id, "edition_id": edition_in_drop, "price": 10}
    )
    query_string = [("available", True), ("keyword", name)]
    response = client.get(
        "/v1/editions", query_string=query_string, headers=auth_header
    )
    editions_list = response.json["data"]["editions"]
    assert response.status_code == 200
    assert len(editions_list) == 1
    assert editions_list[0]["id"] == available_edition_id


def test_list_editions_search_by_name(client, auth_header):
    """Test case for list_editions search by name"""
    name = "test_list_editions_search_by_name"
    EditionModel.factory()
    EditionModel.factory(keys={"name": name})
    query_string = [("keyword", name)]
    response = client.get(
        "/v1/editions", query_string=query_string, headers=auth_header
    )
    editions_list = response.json["data"]["editions"]
    assert response.status_code == 200
    assert len(editions_list) == 1


def test_list_editions_search_by_artist(client, auth_header):
    """Test case for list_editions search by artist"""
    artist = "test_list_editions_search_by_artist"
    EditionModel.factory()
    EditionModel.factory(keys={"artist": artist})
    query_string = [("keyword", artist)]
    response = client.get(
        "/v1/editions", query_string=query_string, headers=auth_header
    )
    editions_list = response.json["data"]["editions"]
    assert response.status_code == 200
    assert len(editions_list) == 1


def test_list_editions_search_by_celebrity(client, auth_header):
    """Test case for list_editions search by celebrity"""
    celebrity = "test_list_editions_search_by_celebrity"
    EditionModel.factory()
    EditionModel.factory(keys={"celebrity": celebrity})
    query_string = [("keyword", celebrity)]
    response = client.get(
        "/v1/editions", query_string=query_string, headers=auth_header
    )
    editions_list = response.json["data"]["editions"]
    assert response.status_code == 200
    assert len(editions_list) == 1


def test_list_editions_search_by_publisher(client, auth_header):
    """Test case for list_editions search by publisher"""
    publisher = "test_list_editions_search_by_publisher"
    EditionModel.factory()
    EditionModel.factory(keys={"publisher": publisher})
    query_string = [("keyword", publisher)]
    response = client.get(
        "/v1/editions", query_string=query_string, headers=auth_header
    )
    editions_list = response.json["data"]["editions"]
    assert response.status_code == 200
    assert len(editions_list) == 1


def test_list_editions_search_by_trademark(client, auth_header):
    """Test case for list_editions search by trademark"""
    trademark = "test_list_editions_search_by_trademark"
    EditionModel.factory()
    EditionModel.factory(keys={"trademark": trademark})
    query_string = [("keyword", trademark)]
    response = client.get(
        "/v1/editions", query_string=query_string, headers=auth_header
    )
    editions_list = response.json["data"]["editions"]
    assert response.status_code == 200
    assert len(editions_list) == 1


def test_list_editions_search_by_avatar_wearable_sku(client, auth_header):
    """Test case for list_editions search by avatar_wearable_sku"""
    avatar_wearable_sku = "test_list_editions_search_by_avatar_wearable_sku"
    EditionModel.factory()
    EditionModel.factory(keys={"avatar_wearable_sku": avatar_wearable_sku})
    query_string = [("keyword", avatar_wearable_sku)]
    response = client.get(
        "/v1/editions", query_string=query_string, headers=auth_header
    )
    editions_list = response.json["data"]["editions"]
    assert response.status_code == 200
    assert len(editions_list) == 1


def test_create_edition_with_required_fields(client, auth_header):
    """Test case for create_edition

    Create a new Edition only with the required fields
    """
    body = CreateEdition(
        name="create_edition_with_required_fields_name",
        avatar_wearable_id=1,
    )
    response = client.post(
        "/v1/editions",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 201


def test_create_edition_with_all_fields(client, auth_header):
    """Test case for create_edition

    Create a new Edition with all the fields
    """
    collection_id = CollectionModel.factory(
        has_one={"serie_id": SerieModel},
        keys={
            "publish_time": datetime.now() + timedelta(hours=2),
            "status": CollectionStatus.PUBLISHED,
        },
    ).id
    on_chain_metadata = CreateOrUpdateEditionOnChainMetadata(
        artist="create_edition_with_all_fields_artist",
        celebrity="create_edition_with_all_fields_celebrity",
        design_slot=DesignSlot.EDITION_DESIGN_SLOT_NIL.value,
        publisher="create_edition_with_all_fields_publisher",
        rarity=EditionRarity.EDITION_RARITY_NIL.value,
        trademark="create_edition_with_all_fields_trademark",
        type=EditionType.EDITION_TYPE_AVATAR_NIL.value,
    )
    off_chain_metadata = EditionOffChainMetadata(
        description="create_edition_with_all_fields_description"
    )
    publish_time = datetime.now() + timedelta(days=1)
    body = CreateEdition(
        name="create_edition_with_all_fields_name",
        avatar_wearable_id=collection_id,
        on_chain_metadata=on_chain_metadata,
        off_chain_metadata=off_chain_metadata,
        reserve_percentage=10,
        publish_time=publish_time,
        price=77.7,
    )
    response = client.post(
        "/v1/editions",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 201
    edition_id = response.json["data"]["id"]
    scheduler_job = scheduler_service.get_job(f"publish_edition_{edition_id}")
    assert scheduler_job["run_date"] == str(
        publish_time.replace(tzinfo=timezone.utc).isoformat()
    )
    scheduler_service.remove_job(f"publish_edition_{edition_id}")


def test_try_to_create_edition_with_past_publish_time(client, auth_header):
    """Test case for create_edition

    Try to create a new Edition with a past publish_time
    """
    collection_id = CollectionModel.factory(has_one={"serie_id": SerieModel}).id
    body = CreateEdition(
        **{
            "name": "create_edition_with_past_publish_time_name",
            "avatar_wearable_id": collection_id,  # The collection id will be the same as avatar_wearable_id due to cms_service_mock
            "publish_time": datetime.now(),
        }
    )
    response = client.post(
        "/v1/editions",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The publish_time cannot be in the past"


def test_try_to_create_edition_with_none_collection_publish_time(client, auth_header):
    """Test case for create_edition

    Try to create a new Edition with publish_time which belongs to a Collection without publish_time
    """
    collection_id = CollectionModel.factory(
        keys={"publish_time": None}, has_one={"serie_id": SerieModel}
    ).id
    body = CreateEdition(
        **{
            "name": "collection_with_none_serie_publish_time_name",
            "avatar_wearable_id": collection_id,
            "publish_time": datetime.now() + timedelta(hours=12),
        }
    )
    response = client.post(
        "/v1/editions",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Edition's publish_time cannot be set until the publish_time of its Collection is set"
    )


def test_try_to_create_edition_with_publish_time_before_collection(client, auth_header):
    """Test case for create_edition

    Try to create a new Edition with publish_time before Collection's publish_time
    """
    collection_id = CollectionModel.factory(
        keys={"publish_time": datetime.now() + timedelta(hours=8)},
        has_one={"serie_id": SerieModel},
    ).id
    body = CreateEdition(
        **{
            "name": "edition_with_publish_time_before_collection_name",
            "avatar_wearable_id": collection_id,
            "publish_time": datetime.now() + timedelta(hours=4),
        }
    )
    response = client.post(
        "/v1/editions",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Edition's publish_time cannot be before the publish_time of its Collection"
    )


def test_try_to_create_edition_without_name(client, auth_header):
    """Test case for create_edition

    Try to create a new Edition without name
    """
    on_chain_metadata = CreateOrUpdateEditionOnChainMetadata(
        artist="create_edition_without_name_artist",
        celebrity="create_edition_without_name_celebrity",
        design_slot=DesignSlot.EDITION_DESIGN_SLOT_NIL.value,
        publisher="create_edition_without_name_publisher",
        rarity=EditionRarity.EDITION_RARITY_NIL.value,
        trademark="create_edition_without_name_trademark",
        type=EditionType.EDITION_TYPE_AVATAR_NIL.value,
    )
    off_chain_metadata = EditionOffChainMetadata(
        description="create_edition_without_name_description"
    )
    body = CreateEdition(
        avatar_wearable_id=32,
        on_chain_metadata=on_chain_metadata,
        off_chain_metadata=off_chain_metadata,
        reserve_percentage=10,
        publish_time=datetime.now(),
        price=77.7,
    )
    response = client.post(
        "/v1/editions",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["detail"] == "'name' is a required property"


def test_try_to_create_edition_without_wearable_id(client, auth_header):
    """Test case for create_edition

    Try to create a new Edition without avatar_wearable_id
    """
    on_chain_metadata = CreateOrUpdateEditionOnChainMetadata(
        artist="create_edition_without_wearable_id_artist",
        celebrity="create_edition_without_wearable_id_celebrity",
        design_slot=DesignSlot.EDITION_DESIGN_SLOT_NIL.value,
        publisher="create_edition_without_wearable_id_publisher",
        rarity=EditionRarity.EDITION_RARITY_NIL.value,
        trademark="create_edition_without_wearable_id_trademark",
        type=EditionType.EDITION_TYPE_AVATAR_NIL.value,
    )
    off_chain_metadata = EditionOffChainMetadata(
        description="create_edition_without_wearable_id_description"
    )
    body = CreateEdition(
        on_chain_metadata=on_chain_metadata,
        off_chain_metadata=off_chain_metadata,
        reserve_percentage=10,
        publish_time=datetime.now(),
        price=77.7,
    )
    response = client.post(
        "/v1/editions",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["detail"] == "'avatar_wearable_id' is a required property"


def test_try_to_create_edition_with_negative_price(client, auth_header):
    """Test case for create_edition

    Try to create a new Edition with price < 0
    """
    body = CreateEdition(
        name="create_edition_with_negative_price", avatar_wearable_id=15, price=-3
    )
    response = client.post(
        "/v1/editions",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The price must be greater than or equal to 0"


def test_get_edition(client, auth_header):
    """Test case for get_edition

    Get the data of an specific edition
    """
    collection = CollectionModel.factory(has_one={"serie_id": SerieModel})
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection.id}
    ).id
    response = client.get(f"/v1/editions/{edition_id}", headers=auth_header)
    assert response.status_code == 200


def test_update_draft_edition(client, auth_header):
    """Test case for update_edition

    Update a draft Edition
    """
    collection_id = CollectionModel.factory(has_one={"serie_id": SerieModel}).id
    collection_id_2 = CollectionModel.factory(
        has_one={"serie_id": SerieModel},
        keys={
            "publish_time": datetime.now() - timedelta(hours=2),
            "status": CollectionStatus.PUBLISHED,
        },
    ).id
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection_id}
    ).id
    name = "update_draft_edition_name"
    description = "update_draft_edition_description"
    publish_time = datetime.now() + timedelta(hours=12)
    artist = "update_draft_edition_artist"
    celebrity = "update_draft_edition_celebrity"
    design_slot = DesignSlot.EDITION_DESIGN_SLOT_SHIRT.value
    publisher = "update_draft_edition_publisher"
    rarity = EditionRarity.EDITION_RARITY_UNIQUE.value
    trademark = "update_draft_edition_trademark"
    type = EditionType.EDITION_TYPE_AVATAR_WEARABLE.value
    price = 14.5
    reserve_percentage = 10
    body = UpdateEdition(
        **{
            "name": name,
            "off_chain_metadata": EditionOffChainMetadata(description=description),
            "publish_time": publish_time,
            "avatar_wearable_id": collection_id_2,
            "on_chain_metadata": CreateOrUpdateEditionOnChainMetadata(
                artist=artist,
                celebrity=celebrity,
                design_slot=design_slot,
                publisher=publisher,
                rarity=rarity,
                trademark=trademark,
                type=type,
            ),
            "price": price,
            "reserve_percentage": reserve_percentage,
        }
    )
    response = client.put(
        f"/v1/editions/{edition_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json["data"]["name"] == name
    assert response.json["data"]["off_chain_metadata"]["description"] == description
    assert response.json["data"]["publish_time"] == format_datetime(publish_time)
    assert response.json["data"]["on_chain_metadata"]["artist"] == artist
    assert response.json["data"]["on_chain_metadata"]["celebrity"] == celebrity
    assert response.json["data"]["on_chain_metadata"]["design_slot"] == design_slot
    assert response.json["data"]["on_chain_metadata"]["publisher"] == publisher
    assert response.json["data"]["on_chain_metadata"]["rarity"] == rarity
    assert response.json["data"]["on_chain_metadata"]["trademark"] == trademark
    assert response.json["data"]["on_chain_metadata"]["type"] == type
    assert response.json["data"]["price"] == format_price(price)
    assert response.json["data"]["avatar_wearable_id"] == collection_id_2
    scheduler_job = scheduler_service.get_job(f"publish_edition_{edition_id}")
    assert scheduler_job["run_date"] == str(
        publish_time.replace(tzinfo=timezone.utc).isoformat()
    )
    scheduler_service.remove_job(f"publish_edition_{edition_id}")


def test_try_to_update_edition_with_past_publish_time(client, auth_header):
    """Test case for update_edition

    Try to update an Edition with a past publish_time
    """
    edition_id = EditionModel.factory(has_one={"collection_id": CollectionModel}).id
    body = UpdateEdition(
        **{
            "publish_time": datetime.now(),
        }
    )
    response = client.put(
        f"/v1/editions/{edition_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The publish_time cannot be in the past"


def test_try_to_update_edition_publish_time_with_none_collection_publish_time(
    client, auth_header
):
    """Test case for update_edition

    Try to set an Edition's publish_time which belongs to a Collection without publish_time
    """
    collection_id = CollectionModel.factory(
        keys={"publish_time": None}, has_one={"serie_id": SerieModel}
    ).id
    edition_id = EditionModel.factory(keys={"collection_id": collection_id}).id
    body = UpdateEdition(**{"publish_time": datetime.now() + timedelta(hours=12)})
    response = client.put(
        f"/v1/editions/{edition_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Edition's publish_time cannot be set until the publish_time of its Collection is set"
    )


def test_try_to_update_edition_with_publish_time_before_collection(client, auth_header):
    """Test case for update_edition

    Try to update an Edition with publish_time before Collection's publish_time
    """
    collection_id = CollectionModel.factory(
        keys={"publish_time": datetime.now() + timedelta(hours=12)},
        has_one={"serie_id": SerieModel},
    ).id
    edition_id = EditionModel.factory(keys={"collection_id": collection_id}).id
    body = UpdateEdition(**{"publish_time": datetime.now() + timedelta(hours=6)})
    response = client.put(
        f"/v1/editions/{edition_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Edition's publish_time cannot be before the publish_time of its Collection"
    )


def test_try_to_update_edition_with_publish_time_after_drop(client, auth_header):
    """Test case for update_edition

    Try to update an Edition with a publish_time after the Drop's publish time
    """
    collection_id = CollectionModel.factory(
        keys={"publish_time": datetime.now() + timedelta(hours=12)},
        has_one={"serie_id": SerieModel},
    ).id
    edition_id = EditionModel.factory(
        keys={
            "publish_time": datetime.now() + timedelta(days=1),
            "collection_id": collection_id,
        },
    ).id
    drop_id = DropModel.factory(
        keys={"publish_time": datetime.now() + timedelta(days=2)}
    ).id
    DropEditionModel.factory(keys={"drop_id": drop_id, "edition_id": edition_id})
    body = UpdateEdition(**{"publish_time": datetime.now() + timedelta(days=3)})
    response = client.put(
        f"/v1/editions/{edition_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        "The Edition's publish_time cannot be after the publish_time of its Drops"
        in response.json["message"]
    )


def test_try_to_update_edition_setting_collection_without_publish_time(
    client, auth_header
):
    """Test case for update_edition

    Try to update an Edition setting a Collection without publish_time
    """
    serie_id = SerieModel.factory().id
    collection_id = CollectionModel.factory(keys={"serie_id": serie_id}).id
    collection_id_2 = CollectionModel.factory(
        keys={"serie_id": serie_id, "publish_time": None}
    ).id
    edition_id = EditionModel.factory(keys={"collection_id": collection_id}).id
    body = UpdateEdition(avatar_wearable_id=collection_id_2)
    response = client.put(
        f"/v1/editions/{edition_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Edition's publish_time cannot be set until the publish_time of its Collection is set"
    )


def test_try_to_update_edition_setting_collection_with_publish_time_after_edition(
    client, auth_header
):
    """Test case for update_edition

    Try to update an Edition setting a Collection with publish_time after Edition's publish_time
    """
    serie_id = SerieModel.factory().id
    collection_id = CollectionModel.factory(keys={"serie_id": serie_id}).id
    collection_id_2 = CollectionModel.factory(
        keys={"serie_id": serie_id, "publish_time": datetime.now() + timedelta(hours=2)}
    ).id
    edition_id = EditionModel.factory(keys={"collection_id": collection_id}).id
    body = UpdateEdition(avatar_wearable_id=collection_id_2)
    response = client.put(
        f"/v1/editions/{edition_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Edition's publish_time cannot be before the publish_time of its Collection"
    )


def test_try_to_update_edition_publish_time_and_set_collection_without_publish_time(
    client, auth_header
):
    """Test case for update_edition

    Try to update an Edition's publish time and set a Collection without publish_time
    """
    collection_id = CollectionModel.factory(has_one={"serie_id": SerieModel}).id
    collection_id_2 = CollectionModel.factory(
        has_one={"serie_id": SerieModel}, keys={"publish_time": None}
    ).id
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection_id}
    ).id
    body = UpdateEdition(
        **{
            "publish_time": datetime.now() + timedelta(hours=12),
            "avatar_wearable_id": collection_id_2,
        }
    )
    response = client.put(
        f"/v1/editions/{edition_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Edition's publish_time cannot be set until the publish_time of its Collection is set"
    )


def test_try_to_update_edition_publish_time_and_set_collection_with_publish_time_after_edition(
    client, auth_header
):
    """Test case for update_edition

    Try to update an Edition's publish time and set a Collection with publish_time after Edition's publish_time
    """
    collection_id = CollectionModel.factory(has_one={"serie_id": SerieModel}).id
    collection_id_2 = CollectionModel.factory(
        has_one={"serie_id": SerieModel},
        keys={"publish_time": datetime.now() + timedelta(hours=18)},
    ).id
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection_id}
    ).id
    body = UpdateEdition(
        **{
            "publish_time": datetime.now() + timedelta(hours=12),
            "avatar_wearable_id": collection_id_2,
        }
    )
    response = client.put(
        f"/v1/editions/{edition_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Edition's publish_time cannot be before the publish_time of its Collection"
    )


def test_try_to_update_edition_with_negative_price(client, auth_header):
    """Test case for update_edition

    Try to update a new Edition with price < 0
    """
    edition_id: EditionModel = EditionModel.factory(
        has_one={"collection_id": CollectionModel}
    ).id
    body = UpdateEdition(price=-7.5)
    response = client.put(
        f"/v1/editions/{edition_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The price must be greater than or equal to 0"


def test_delete_edition(client, auth_header):
    """Test case for delete_edition

    Delete an Edition
    """
    collection = CollectionModel.factory(has_one={"serie_id": SerieModel})
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection.id}
    ).id
    response = client.delete(f"/v1/editions/{edition_id}", headers=auth_header)

    assert response.status_code == 200


def test_batch_update_editions(client, auth_header):
    """Test case for batch_update_editions

    Batch update editions by avatar_wearable_id
    """
    avatar_wearable_id = 14
    original_collection_wearables_count = 2
    new_collection_wearables_count = 7
    new_collection_short_word = "newCollection"
    original_avatar_wearable_sku = "2021-serie1-collection1-asset1"
    original_collection_id = CollectionModel.factory(
        keys={"wearables_count": original_collection_wearables_count},
        has_one={"serie_id": SerieModel},
    ).id
    new_collection_id = CollectionModel.factory(
        keys={
            "short_word": new_collection_short_word,
            "wearables_count": new_collection_wearables_count,
        },
        has_one={"serie_id": SerieModel},
    ).id
    new_asset_short_word = "newShortWord"
    new_avatar_wearable_sku = (
        f"2021-serie1-{new_collection_short_word}-{new_asset_short_word}"
    )
    edition_id: EditionModel = EditionModel.factory(
        keys={
            "collection_id": original_collection_id,
            "avatar_wearable_id": avatar_wearable_id,
            "avatar_wearable_sku": original_avatar_wearable_sku,
        }
    ).id
    edition_id_2: EditionModel = EditionModel.factory(
        keys={
            "collection_id": original_collection_id,
            "avatar_wearable_id": avatar_wearable_id,
            "avatar_wearable_sku": original_avatar_wearable_sku,
        }
    ).id
    body = BatchUpdateEditions(
        **{
            "avatar_wearable_id": avatar_wearable_id,
            "short_word": new_asset_short_word,
            "collection_id": new_collection_id,
            "file_list": [
                "http://genies.test/hero.png",
                "http://genies.test/mannequin-1.png",
                "http://genies.test/unboxing.mp4",
            ],
        }
    )
    response = client.put(
        f"/v1/editions/batch_update",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 200
    response = client.get(f"/v1/editions/{edition_id}", headers=auth_header)
    assert response.json["data"]["collection"]["id"] == new_collection_id
    assert (
        response.json["data"]["on_chain_metadata"]["avatar_wearable_sku"]
        == new_avatar_wearable_sku
    )
    response = client.get(f"/v1/editions/{edition_id_2}", headers=auth_header)
    assert response.json["data"]["collection"]["id"] == new_collection_id
    assert (
        response.json["data"]["on_chain_metadata"]["avatar_wearable_sku"]
        == new_avatar_wearable_sku
    )
    assert (
        response.json["data"]["collection"]["wearables_count"]
        == new_collection_wearables_count + 1
    )
    response = client.get(
        f"/v1/collections/{original_collection_id}", headers=auth_header
    )
    assert (
        response.json["data"]["wearables_count"]
        == original_collection_wearables_count - 1
    )


def test_publish_edition(client, auth_header):
    """Test case for publish_edition

    Publish an edition to the dapper system
    """
    serie_id: int = SerieModel.factory(keys={"has_published_editions": False}).id
    collection_id: int = CollectionModel.factory(
        keys={
            "serie_id": serie_id,
            "status": CollectionStatus.PUBLISHED,
            "has_published_editions": False,
        }
    ).id
    edition: EditionModel = EditionModel.factory(
        keys={"collection_id": collection_id, "publish_time": None}
    )
    AssetsExtras.factory(
        keys={
            "avatar_wearable_id": edition.avatar_wearable_id,
            "images": '["http://warehouse-assets.genies.com/2022-test-col-shortw/wearable.png"]',
            "videos": '["http://warehouse-assets.genies.com/2022-test-col-shortw/unboxing.mp4"]',
        }
    )
    response = client.post(
        f"/v1/editions/{edition.id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 200
    response = client.get(
        f"/v1/editions/{edition.id}?format=false", headers=auth_header
    )
    assert response.json["data"]["status"] == EditionStatus.CREATING.value
    sleep(1)
    response = client.get(
        f"/v1/editions/{edition.id}?format=false", headers=auth_header
    )
    assert response.json["data"]["status"] == EditionStatus.CREATED.value
    publish_time = deserialize_datetime(response.json["data"]["publish_time"])
    assert publish_time <= datetime.now(publish_time.tzinfo)
    response = client.get(f"/v1/collections/{collection_id}", headers=auth_header)
    assert response.json["data"]["has_published_editions"] == True
    response = client.get(f"/v1/series/{serie_id}", headers=auth_header)
    assert response.json["data"]["has_published_editions"] == True


def test_publish_edition_with_default_type(client, auth_header):
    """Test case for publish_edition

    Publish an Edition without specifying its type (the default is EDITION_TYPE_AVATAR_WEARABLE)
    """
    serie: SerieModel = SerieModel.factory()
    collection: CollectionModel = CollectionModel.factory(
        keys={"serie_id": serie.id, "status": CollectionStatus.PUBLISHED}
    )
    edition: EditionModel = EditionModel.factory(
        keys={"collection_id": collection.id, "type": None}
    )
    AssetsExtras.factory(
        keys={
            "avatar_wearable_id": edition.avatar_wearable_id,
            "images": '["http://warehouse-assets.genies.com/2022-test-col-shortw/wearable.png"]',
            "videos": '["http://warehouse-assets.genies.com/2022-test-col-shortw/unboxing.mp4"]',
        }
    )
    response = client.post(
        f"/v1/editions/{edition.id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 200


def test_try_to_publish_edition_of_draft_collection(client, auth_header):
    """Test case for publish_edition

    Try to publish an Edition that belongs to a draft Collection
    """
    serie: SerieModel = SerieModel.factory()
    collection: CollectionModel = CollectionModel.factory(keys={"serie_id": serie.id})
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection.id}
    ).id
    response = client.post(
        f"/v1/editions/{edition_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        response.json["message"] == "The Edition must belong to a published Collection"
    )


def test_try_to_publish_edition_of_inactive_collection(client, auth_header):
    """Test case for publish_edition

    Try to publish an Edition that belongs to an inactive Collection
    """
    serie: SerieModel = SerieModel.factory()
    collection: CollectionModel = CollectionModel.factory(
        keys={"serie_id": serie.id, "status": CollectionStatus.INACTIVE}
    )
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection.id}
    ).id
    response = client.post(
        f"/v1/editions/{edition_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        response.json["message"] == "The Edition must belong to a published Collection"
    )


def test_try_to_publish_edition_without_description(client, auth_header):
    """Test case for publish_edition

    Try to publish an Edition without description
    """
    serie: SerieModel = SerieModel.factory()
    collection: CollectionModel = CollectionModel.factory(
        keys={"serie_id": serie.id, "status": CollectionStatus.PUBLISHED}
    )
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection.id, "description": None}
    ).id
    response = client.post(
        f"/v1/editions/{edition_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        "Some fields required to publish don't have a value" in response.json["message"]
    )


def test_try_to_publish_edition_without_artist(client, auth_header):
    """Test case for publish_edition

    Try to publish an Edition without artist
    """
    serie: SerieModel = SerieModel.factory()
    collection: CollectionModel = CollectionModel.factory(
        keys={"serie_id": serie.id, "status": CollectionStatus.PUBLISHED}
    )
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection.id, "artist": None}
    ).id
    response = client.post(
        f"/v1/editions/{edition_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        "Some fields required to publish don't have a value" in response.json["message"]
    )


def test_try_to_publish_edition_without_celebrity(client, auth_header):
    """Test case for publish_edition

    Try to publish an Edition without celebrity
    """
    serie: SerieModel = SerieModel.factory()
    collection: CollectionModel = CollectionModel.factory(
        keys={"serie_id": serie.id, "status": CollectionStatus.PUBLISHED}
    )
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection.id, "celebrity": None}
    ).id
    response = client.post(
        f"/v1/editions/{edition_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        "Some fields required to publish don't have a value" in response.json["message"]
    )


def test_try_to_publish_edition_without_design_slot(client, auth_header):
    """Test case for publish_edition

    Try to publish an Edition without design_slot
    """
    serie: SerieModel = SerieModel.factory()
    collection: CollectionModel = CollectionModel.factory(
        keys={"serie_id": serie.id, "status": CollectionStatus.PUBLISHED}
    )
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection.id, "design_slot": None}
    ).id
    response = client.post(
        f"/v1/editions/{edition_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        "Some fields required to publish don't have a value" in response.json["message"]
    )


def test_try_to_publish_edition_without_publisher(client, auth_header):
    """Test case for publish_edition

    Try to publish an Edition without publisher
    """
    serie: SerieModel = SerieModel.factory()
    collection: CollectionModel = CollectionModel.factory(
        keys={"serie_id": serie.id, "status": CollectionStatus.PUBLISHED}
    )
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection.id, "publisher": None}
    ).id
    response = client.post(
        f"/v1/editions/{edition_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        "Some fields required to publish don't have a value" in response.json["message"]
    )


def test_try_to_publish_edition_without_rarity(client, auth_header):
    """Test case for publish_edition

    Try to publish an Edition without rarity
    """
    serie: SerieModel = SerieModel.factory()
    collection: CollectionModel = CollectionModel.factory(
        keys={"serie_id": serie.id, "status": CollectionStatus.PUBLISHED}
    )
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection.id, "rarity": None}
    ).id
    response = client.post(
        f"/v1/editions/{edition_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        "Some fields required to publish don't have a value" in response.json["message"]
    )


def test_try_to_publish_edition_without_trademark(client, auth_header):
    """Test case for publish_edition

    Try to publish an Edition without trademark
    """
    serie: SerieModel = SerieModel.factory()
    collection: CollectionModel = CollectionModel.factory(
        keys={"serie_id": serie.id, "status": CollectionStatus.PUBLISHED}
    )
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection.id, "trademark": None}
    ).id
    response = client.post(
        f"/v1/editions/{edition_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        "Some fields required to publish don't have a value" in response.json["message"]
    )


def test_try_to_publish_edition_without_price(client, auth_header):
    """Test case for publish_edition

    Try to publish an Edition without price
    """
    serie: SerieModel = SerieModel.factory()
    collection: CollectionModel = CollectionModel.factory(
        keys={"serie_id": serie.id, "status": CollectionStatus.PUBLISHED}
    )
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection.id, "price": None}
    ).id
    response = client.post(
        f"/v1/editions/{edition_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        "Some fields required to publish don't have a value" in response.json["message"]
    )


def test_try_to_publish_edition_without_reserve_percentage(client, auth_header):
    """Test case for publish_edition

    Try to publish an Edition without reserve_percentage
    """
    serie: SerieModel = SerieModel.factory()
    collection: CollectionModel = CollectionModel.factory(
        keys={"serie_id": serie.id, "status": CollectionStatus.PUBLISHED}
    )
    edition_id: EditionModel = EditionModel.factory(
        keys={"collection_id": collection.id, "reserve_percentage": None}
    ).id
    response = client.post(
        f"/v1/editions/{edition_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        "Some fields required to publish don't have a value" in response.json["message"]
    )


def test_mint_nft(client, auth_header):
    """Test case for mint_nft

    Mint an NFT
    """
    body = Mint(quantity=10)
    collection = CollectionModel.factory(has_one={"serie_id": SerieModel})
    edition_id: EditionModel = EditionModel.factory(
        keys={
            "collection_id": collection.id,
            "status": EditionStatus.CREATED,
            "reserve_percentage": 20,
        }
    ).id
    response = client.post(
        f"/v1/editions/{edition_id}/mint",
        data=json.dumps(body),
        content_type="application/json",
        headers=auth_header,
    )
    assert response.status_code == 200


def test_list_edition_errors(client, auth_header):
    """Test case for list_edition_errors

    List edition errors
    """
    edition_id: int = EditionModel.factory().id
    edition_id_2: int = EditionModel.factory().id
    EditionErrorModel.factory(keys={"edition_id": edition_id})
    EditionErrorModel.factory(keys={"edition_id": edition_id_2})
    response = client.get(f"/v1/editions/{edition_id}/errors", headers=auth_header)
    assert response.status_code == 200
    assert len(response.json["data"]["edition_errors"]) == 1
