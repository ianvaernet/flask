# coding: utf-8
from __future__ import absolute_import
from flask import json
from swagger_server.database.enums.collection_status import CollectionStatus
from swagger_server.database.enums.serie_status import SerieStatus
from swagger_server.database.models import CollectionModel, SerieModel
from swagger_server.database.models.edition import EditionModel
from swagger_server.models import (
    CreateCollection,
    UpdateCollection,
    CollectionOffChainMetadata,
)
from datetime import datetime, timedelta, timezone
from swagger_server.services import scheduler_service
from swagger_server.util import deserialize_datetime, format_datetime
from swagger_server.__main__ import db


def test_init():
    db.drop_all()
    db.create_all()


def test_list_collections_pagination(client, auth_header):
    """Test case for list_collections

    Paginate a list of collections
    """
    page_size = 2
    serie_id = SerieModel.factory().id
    CollectionModel.factory(keys={"serie_id": serie_id})
    CollectionModel.factory(keys={"serie_id": serie_id})
    CollectionModel.factory(keys={"serie_id": serie_id})
    query_string = [("page_size", page_size), ("page", 1)]
    response = client.get(
        "/v1/collections", query_string=query_string, headers=auth_header
    )
    collections_list = response.json["data"]["collections"]
    assert response.status_code == 200
    assert response.json["data"]["total_pages"] > 0
    assert len(collections_list) > 0
    assert len(collections_list) <= page_size


def test_list_collections_filters(client, auth_header):
    """Test case for list_collections

    Filter a list of collections
    """
    name = "test_list_collections_filters"
    status = [CollectionStatus.DRAFT.value, CollectionStatus.PUBLISHED.value]
    serie_id = SerieModel.factory().id
    CollectionModel.factory(
        keys={"name": name + "1", "status": status[0], "serie_id": serie_id}
    )
    CollectionModel.factory(
        keys={"name": name + "2", "status": status[1], "serie_id": serie_id}
    )
    CollectionModel.factory(
        keys={
            "name": name + "3",
            "status": CollectionStatus.INACTIVE,
            "serie_id": serie_id,
        }
    )
    CollectionModel.factory(
        keys={"name": name + "4", "status": status[0]}, has_one={"serie_id": SerieModel}
    )
    query_string = [
        ("keyword", name),
        ("status", ",".join(status)),
        ("serie_id", serie_id),
    ]
    response = client.get(
        "/v1/collections", query_string=query_string, headers=auth_header
    )
    collections_list = response.json["data"]["collections"]
    assert response.status_code == 200
    assert len(collections_list) == 2


def test_list_collections_search_by_name(client, auth_header):
    """Test case for list_collections

    Search collections by name
    """
    name = "test_list_collections_search_by_name"
    serie_id = SerieModel.factory().id
    CollectionModel.factory(keys={"serie_id": serie_id})
    CollectionModel.factory(keys={"serie_id": serie_id, "name": name})
    query_string = [("keyword", name)]
    response = client.get(
        "/v1/collections", query_string=query_string, headers=auth_header
    )
    collections_list = response.json["data"]["collections"]
    assert response.status_code == 200
    assert len(collections_list) == 1


def test_list_collections_search_by_short_word(client, auth_header):
    """Test case for list_collections

    Search collections by short_word
    """
    short_word = "testListCollectionsSearchByShortWord"
    serie_id = SerieModel.factory().id
    CollectionModel.factory(keys={"serie_id": serie_id})
    CollectionModel.factory(keys={"serie_id": serie_id, "short_word": short_word})
    query_string = [("keyword", short_word)]
    response = client.get(
        "/v1/collections", query_string=query_string, headers=auth_header
    )
    collections_list = response.json["data"]["collections"]
    assert response.status_code == 200
    assert len(collections_list) == 1


def test_create_collection_with_required_fields(client, auth_header):
    """Test case for create_collection

    Create a new Collection with the required fields only
    """
    serie_id = SerieModel.factory(keys={"collections_count": 0}).id
    body = CreateCollection(
        **{
            "name": "create_collection_with_required_fields_name",
            "short_word": "collectionWithRequiredFields",
            "serie_id": serie_id,
        }
    )
    response = client.post(
        "/v1/collections",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 201
    response = client.get(f"/v1/series/{serie_id}", headers=auth_header)
    assert response.json["data"]["collections_count"] == 1


def test_create_collection_with_all_fields(client, auth_header):
    """Test case for create_collection

    Create a new Collection with all the fields
    """
    serie_id = SerieModel.factory(
        keys={"collections_count": 0, "status": SerieStatus.ACTIVE}
    ).id
    publish_time = datetime.now() + timedelta(hours=1)
    body = CreateCollection(
        **{
            "name": "create_collection_with_all_fields",
            "off_chain_metadata": CollectionOffChainMetadata(
                **{"description": "create_collection_with_all_fields"}
            ),
            "short_word": "createCollectionWithAllFields",
            "publish_time": publish_time,
            "serie_id": serie_id,
        }
    )
    response = client.post(
        "/v1/collections",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 201
    collection_id = response.json["data"]["id"]
    response = client.get(f"/v1/series/{serie_id}", headers=auth_header)
    assert response.json["data"]["collections_count"] == 1
    scheduler_job = scheduler_service.get_job(f"publish_collection_{collection_id}")
    assert scheduler_job["run_date"] == str(
        publish_time.replace(tzinfo=timezone.utc).isoformat()
    )
    scheduler_service.remove_job(f"publish_collection_{collection_id}")


def test_try_to_create_collection_without_name(client, auth_header):
    """Test case for create_collection

    Try to create a new Collection without name
    """
    serie_id = SerieModel.factory().id
    body = CreateCollection(
        **{
            "short_word": "createCollectionWithoutName",
            "serie_id": serie_id,
        }
    )
    response = client.post(
        "/v1/collections",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["detail"] == "'name' is a required property"


def test_try_to_create_collection_without_short_word(client, auth_header):
    """Test case for create_collection

    Try to create a new Collection without short_word
    """
    serie_id = SerieModel.factory().id
    body = CreateCollection(
        **{
            "name": "create_collection_without_short_word",
            "serie_id": serie_id,
        }
    )
    response = client.post(
        "/v1/collections",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["detail"] == "'short_word' is a required property"


def test_try_to_create_collection_without_serie_id(client, auth_header):
    """Test case for create_collection

    Try to create a new Collection without serie_id
    """
    body = CreateCollection(
        **{
            "name": "create_collection_without_serie_id",
            "short_word": "createCollectionWithoutSerieId",
        }
    )
    response = client.post(
        "/v1/collections",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["detail"] == "'serie_id' is a required property"


def test_try_to_create_collection_with_past_publish_time(client, auth_header):
    """Test case for create_collection

    Try to create a new Collection with a past publish_time
    """
    serie_id = SerieModel.factory().id
    body = CreateCollection(
        **{
            "name": "create_collection_with_past_publish_time",
            "short_word": "collectionWithPastPublishTime",
            "serie_id": serie_id,
            "publish_time": datetime.now(),
        }
    )
    response = client.post(
        "/v1/collections",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The publish_time cannot be in the past"


def test_try_to_create_collection_with_none_serie_publish_time(client, auth_header):
    """Test case for create_collection

    Try to create a new Collection with publish_time that belongs to a Serie without publish_time
    """
    serie_id = SerieModel.factory(keys={"publish_time": None}).id
    body = CreateCollection(
        **{
            "name": "collection_with_none_serie_publish_time",
            "short_word": "collectionNoneSeriePublishTime",
            "serie_id": serie_id,
            "publish_time": datetime.now() + timedelta(hours=12),
        }
    )
    response = client.post(
        "/v1/collections",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Collection's publish_time cannot be set until the publish_time of its Series is set"
    )


def test_try_to_create_collection_with_publish_time_before_serie(client, auth_header):
    """Test case for create_collection

    Try to create a new Collection with publish_time before Serie's publish_time
    """
    serie_id = SerieModel.factory(
        keys={"publish_time": datetime.now() + timedelta(days=2)}
    ).id
    body = CreateCollection(
        **{
            "name": "create_collection_with_publish_time_before_serie",
            "short_word": "collectionPubTimeBeforeSerie",
            "serie_id": serie_id,
            "publish_time": datetime.now() + timedelta(days=1),
        }
    )
    response = client.post(
        "/v1/collections",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Collection's publish_time cannot be before the publish_time of its Series"
    )


def test_get_collection(client, auth_header):
    """Test case for get_collection

    Get a Collection
    """
    collection_id = CollectionModel.factory(has_one={"serie_id": SerieModel}).id
    response = client.get(f"/v1/collections/{collection_id}", headers=auth_header)
    assert response.status_code == 200


def test_try_to_get_non_existent_collection(client, auth_header):
    """Test case for get_collection

    Try to get a non-existent Collection
    """
    response = client.get("/v1/collections/54321", headers=auth_header)
    assert response.status_code == 404


def test_update_draft_collection(client, auth_header):
    """Test case for update_collection

    Update name, description, short_word, publish_time, serie_id and wearables_count of a draft Collection
    """
    collection = CollectionModel.factory(
        has_one={"serie_id": SerieModel}, keys={"has_published_editions": False}
    )
    name: str = "test_update_draft_collection_name"
    description: str = "test_update_draft_collection_description"
    off_chain_metadata = CollectionOffChainMetadata(description=description)
    short_word: str = "updateDraftCollectionShortWord"
    publish_time: datetime = datetime.now() + timedelta(days=1)
    serie_id: int = SerieModel.factory(keys={"status": SerieStatus.ACTIVE}).id
    wearables_count_difference: int = 5
    wearables_count: int = collection.wearables_count + wearables_count_difference
    body = UpdateCollection(
        name=name,
        off_chain_metadata=off_chain_metadata,
        short_word=short_word,
        publish_time=publish_time,
        serie_id=serie_id,
        wearables_count_difference=wearables_count_difference,
    )
    response = client.put(
        f"/v1/collections/{collection.id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json["data"]["name"] == name
    assert response.json["data"]["off_chain_metadata"]["description"] == description
    assert response.json["data"]["short_word"] == short_word
    assert response.json["data"]["publish_time"] == format_datetime(publish_time)
    assert response.json["data"]["serie"]["id"] == serie_id
    assert response.json["data"]["wearables_count"] == wearables_count
    scheduler_job = scheduler_service.get_job(f"publish_collection_{collection.id}")
    assert scheduler_job["run_date"] == str(
        publish_time.replace(tzinfo=timezone.utc).isoformat()
    )
    scheduler_service.remove_job(f"publish_collection_{collection.id}")


def test_update_published_collection(client, auth_header):
    """Test case for update_collection

    Update description, short_word and wearables_count of a published Collection
    """
    collection = CollectionModel.factory(
        has_one={"serie_id": SerieModel},
        keys={
            "status": CollectionStatus.PUBLISHED,
            "has_published_editions": False,
            "wearables_count": 3,
        },
    )
    description: str = "test_update_published_collection_description"
    off_chain_metadata = CollectionOffChainMetadata(description=description)
    short_word: str = "updatePublishedCollection"
    wearables_count_difference: int = -1
    wearables_count: int = collection.wearables_count + wearables_count_difference
    body = UpdateCollection(
        off_chain_metadata=off_chain_metadata,
        short_word=short_word,
        wearables_count_difference=wearables_count_difference,
    )
    response = client.put(
        f"/v1/collections/{collection.id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json["data"]["off_chain_metadata"]["description"] == description
    assert response.json["data"]["short_word"] == short_word
    assert response.json["data"]["wearables_count"] == wearables_count


def test_update_short_word_of_a_collection_with_editions(client, auth_header):
    """Test case for update_collection

    Update short_word of a Collection with no published Editions
    """
    original_sku: str = "2021-serie-shortWordOfACollectionWithEditions-asset"
    updated_short_word: str = "newShortWordCollectionEditions"
    updated_sku: str = "2021-serie-newShortWordCollectionEditions-asset"
    serie_id = SerieModel.factory().id
    collection_id = CollectionModel.factory(
        keys={"serie_id": serie_id, "has_published_editions": False}
    ).id
    edition_id = EditionModel.factory(
        keys={"collection_id": collection_id, "avatar_wearable_sku": original_sku}
    ).id
    body = UpdateCollection(short_word=updated_short_word)
    response = client.put(
        f"/v1/collections/{collection_id}",
        data=json.dumps(body),
        content_type="application/json",
        headers=auth_header,
    )
    assert response.status_code == 200
    assert response.json["data"]["short_word"] == updated_short_word
    response = client.get(f"/v1/editions/{edition_id}", headers=auth_header)
    assert (
        response.json["data"]["on_chain_metadata"]["avatar_wearable_sku"] == updated_sku
    )


def test_try_to_update_short_word_of_a_collection_with_published_editions(
    client, auth_header
):
    """Test case for update_collection

    Update short_word of a Collection with published Editions
    """
    original_sku: str = "2021-serie-shortWordOfACollectionWithPublishedEditions-asset"
    updated_short_word: str = "newShortWordCollectPubEditions"
    serie_id = SerieModel.factory().id
    collection_id = CollectionModel.factory(
        keys={"serie_id": serie_id, "has_published_editions": True}
    ).id
    edition_id = EditionModel.factory(
        keys={"collection_id": collection_id, "avatar_wearable_sku": original_sku}
    ).id
    body = UpdateCollection(short_word=updated_short_word)
    response = client.put(
        f"/v1/collections/{collection_id}",
        data=json.dumps(body),
        content_type="application/json",
        headers=auth_header,
    )
    assert response.status_code == 409
    response = client.get(f"/v1/editions/{edition_id}", headers=auth_header)
    assert (
        response.json["data"]["on_chain_metadata"]["avatar_wearable_sku"]
        == original_sku
    )


def test_try_to_update_collection_with_past_publish_time(client, auth_header):
    """Test case for update_collection

    Try to update a Collection with a past publish_time
    """
    collection_id = CollectionModel.factory(has_one={"serie_id": SerieModel}).id
    body = UpdateCollection(
        **{
            "publish_time": datetime.now(),
        }
    )
    response = client.put(
        f"/v1/collections/{collection_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The publish_time cannot be in the past"


def test_try_to_update_collection_publish_time_with_none_serie_publish_time(
    client, auth_header
):
    """Test case for update_collection

    Try to set a Collection's publish_time which belongs to a Serie without publish_time
    """
    serie_id = SerieModel.factory(keys={"publish_time": None}).id
    collection_id = CollectionModel.factory(keys={"serie_id": serie_id}).id
    body = UpdateCollection(**{"publish_time": datetime.now() + timedelta(hours=12)})
    response = client.put(
        f"/v1/collections/{collection_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Collection's publish_time cannot be set until the publish_time of its Series is set"
    )


def test_try_to_update_collection_with_publish_time_before_serie(client, auth_header):
    """Test case for update_collection

    Try to update a Collection with publish_time before Serie's publish_time
    """
    serie_id = SerieModel.factory(
        keys={"publish_time": datetime.now() + timedelta(hours=12)}
    ).id
    collection_id = CollectionModel.factory(keys={"serie_id": serie_id}).id
    body = UpdateCollection(**{"publish_time": datetime.now() + timedelta(hours=6)})
    response = client.put(
        f"/v1/collections/{collection_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Collection's publish_time cannot be before the publish_time of its Series"
    )


def test_try_to_update_collection_with_publish_time_after_edition(client, auth_header):
    """Test case for update_collection

    Try to update a Collection with publish_time after Edition's publish_time
    """
    collection_id = CollectionModel.factory(
        keys={"publish_time": datetime.now() + timedelta(days=1)},
        has_one={"serie_id": SerieModel},
    ).id
    EditionModel.factory(
        keys={
            "collection_id": collection_id,
            "publish_time": datetime.now() + timedelta(days=2),
        }
    )
    body = UpdateCollection(**{"publish_time": datetime.now() + timedelta(days=3)})
    response = client.put(
        f"/v1/collections/{collection_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        "The Collection's publish_time cannot be after the publish_time of its Editions"
        in response.json["message"]
    )


def test_try_to_update_collection_setting_serie_without_publish_time(
    client, auth_header
):
    """Test case for update_collection

    Try to update a Collection setting a Serie without publish_time
    """
    serie_id = SerieModel.factory().id
    serie_id_2 = SerieModel.factory(keys={"publish_time": None}).id
    collection_id = CollectionModel.factory(keys={"serie_id": serie_id}).id
    body = UpdateCollection(**{"serie_id": serie_id_2})
    response = client.put(
        f"/v1/collections/{collection_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Collection's publish_time cannot be set until the publish_time of its Series is set"
    )


def test_try_to_update_collection_setting_serie_with_publish_time_after_collection(
    client, auth_header
):
    """Test case for update_collection

    Try to update a Collection setting a Serie with publish_time after Collection's publish_time
    """
    serie_id = SerieModel.factory().id
    serie_id_2 = SerieModel.factory(
        keys={"publish_time": datetime.now() + timedelta(hours=12)}
    ).id
    collection_id = CollectionModel.factory(keys={"serie_id": serie_id}).id
    body = UpdateCollection(**{"serie_id": serie_id_2})
    response = client.put(
        f"/v1/collections/{collection_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Collection's publish_time cannot be before the publish_time of its Series"
    )


def test_try_to_update_collection_publish_time_and_set_serie_without_publish_time(
    client, auth_header
):
    """Test case for update_collection

    Try to update a Collection's publish_time and set a Series without publish_time
    """
    serie_id = SerieModel.factory().id
    serie_id_2 = SerieModel.factory(keys={"publish_time": None}).id
    collection_id = CollectionModel.factory(keys={"serie_id": serie_id}).id
    body = UpdateCollection(
        **{"publish_time": datetime.now() + timedelta(hours=12), "serie_id": serie_id_2}
    )
    response = client.put(
        f"/v1/collections/{collection_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Collection's publish_time cannot be set until the publish_time of its Series is set"
    )


def test_try_to_update_collection_publish_time_and_set_serie_with_publish_time_after_collection(
    client, auth_header
):
    """Test case for update_collection

    Try to update a Collection's publish_time and set a Serie with publish_time after Collection's publish_time
    """
    serie_id = SerieModel.factory().id
    serie_id_2 = SerieModel.factory(
        keys={"publish_time": datetime.now() + timedelta(hours=12)}
    ).id
    collection_id = CollectionModel.factory(keys={"serie_id": serie_id}).id
    body = UpdateCollection(
        **{"publish_time": datetime.now() + timedelta(hours=6), "serie_id": serie_id_2}
    )
    response = client.put(
        f"/v1/collections/{collection_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        response.json["message"]
        == "The Collection's publish_time cannot be before the publish_time of its Series"
    )


def test_try_to_update_name_of_published_collection(client, auth_header):
    """Test case for update_collection

    Try to update name of a published Collection
    """
    collection = CollectionModel.factory(
        has_one={"serie_id": SerieModel}, keys={"status": CollectionStatus.PUBLISHED}
    )
    old_name: str = collection.name
    new_name: str = "update_name_of_published_collection"
    body = UpdateCollection(name=new_name)
    response = client.put(
        f"/v1/collections/{collection.id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json["data"]["name"] == old_name


def test_try_to_update_publish_time_of_published_collection(client, auth_header):
    """Test case for update_collection

    Try to update publish_time of a published Collection
    """
    collection = CollectionModel.factory(
        has_one={"serie_id": SerieModel}, keys={"status": CollectionStatus.PUBLISHED}
    )
    old_publish_time: datetime = collection.publish_time
    new_publish_time: datetime = datetime.now() + timedelta(hours=18)
    body = UpdateCollection(publish_time=new_publish_time)
    response = client.put(
        f"/v1/collections/{collection.id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json["data"]["publish_time"] == format_datetime(old_publish_time)


def test_try_to_update_serie_id_of_published_collection(client, auth_header):
    """Test case for update_collection

    Try to update serie_id of a published Collection
    """
    collection = CollectionModel.factory(
        has_one={"serie_id": SerieModel}, keys={"status": CollectionStatus.PUBLISHED}
    )
    old_serie_id: int = collection.serie_id
    new_serie_id: int = SerieModel.factory().id
    body = UpdateCollection(serie_id=new_serie_id)
    response = client.put(
        f"/v1/collections/{collection.id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json["data"]["serie"]["id"] == old_serie_id


def test_try_to_update_short_word_of_collection_with_published_editions(
    client, auth_header
):
    """Test case for update_collection

    Try to update short_word of a Collection with published Editions
    """
    collection = CollectionModel.factory(
        has_one={"serie_id": SerieModel},
        keys={"status": CollectionStatus.PUBLISHED, "has_published_editions": True},
    )
    short_word: str = "collectionPublishedEditions"
    body = UpdateCollection(short_word=short_word)
    response = client.put(
        f"/v1/collections/{collection.id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 409
    assert "short_word cannot be updated" in response.json["message"]


def test_delete_collection(client, auth_header):
    """Test case for delete_collection

    Delete a Collection
    """
    serie_id = SerieModel.factory(keys={"collections_count": 1}).id
    collection = CollectionModel.factory(
        keys={"serie_id": serie_id, "wearables_count": 0}
    )
    response = client.delete(f"/v1/collections/{collection.id}", headers=auth_header)
    assert response.status_code == 200
    response = client.get(f"/v1/series/{serie_id}", headers=auth_header)
    assert response.json["data"]["collections_count"] == 0


def test_try_to_delete_non_existent_collection(client, auth_header):
    """Test case for delete_collection

    Try to delete a non-existent collection
    """
    response = client.delete("/v1/collections/54321", headers=auth_header)
    assert response.status_code == 404


def test_try_to_delete_published_collection(client, auth_header):
    """Test case for delete_collection

    Try to delete a published collection
    """
    collection_id = CollectionModel.factory(
        has_one={"serie_id": SerieModel},
        keys={"wearables_count": 0, "status": CollectionStatus.PUBLISHED},
    ).id
    response = client.delete(f"/v1/collections/{collection_id}", headers=auth_header)
    assert response.status_code == 403
    assert (
        response.json["message"]
        == "The Collection cannot be deleted because it has already been published"
    )


def test_try_to_delete_inactive_collection(client, auth_header):
    """Test case for delete_collection

    Try to delete a published collection
    """
    collection_id = CollectionModel.factory(
        has_one={"serie_id": SerieModel},
        keys={"wearables_count": 0, "status": CollectionStatus.INACTIVE},
    ).id
    response = client.delete(f"/v1/collections/{collection_id}", headers=auth_header)
    assert response.status_code == 403
    assert (
        response.json["message"]
        == "The Collection cannot be deleted because it has already been published"
    )


def test_try_to_delete_collection_with_wearables(client, auth_header):
    """Test case for delete_collection

    Try to delete a collection with wearables dependent on it
    """
    collection = CollectionModel.factory(
        has_one={"serie_id": SerieModel}, keys={"wearables_count": 1}
    )
    response = client.delete(f"/v1/collections/{collection.id}", headers=auth_header)
    assert response.status_code == 409
    assert (
        response.json["message"]
        == "The Collection cannot be deleted because it has Wearables dependent on it"
    )


def test_publish_collection(client, auth_header):
    """Test case for publish_collection

    Publish a collection
    """
    serie_id: int = SerieModel.factory(keys={"status": SerieStatus.ACTIVE}).id
    collection_id: int = CollectionModel.factory(keys={"serie_id": serie_id}).id
    response = client.post(
        f"/v1/collections/{collection_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 200
    response = client.get(
        f"/v1/collections/{collection_id}?format=false",
        headers=auth_header,
    )
    assert response.json["data"]["status"] == CollectionStatus.PUBLISHED.value
    publish_time = deserialize_datetime(response.json["data"]["publish_time"])
    assert publish_time <= datetime.now(publish_time.tzinfo)


def test_try_to_publish_collection_without_description(client, auth_header):
    """Test case for publish_collection

    Try to publish a Collection without description
    """
    serie_id: int = SerieModel.factory().id
    collection_id: int = CollectionModel.factory(
        keys={"serie_id": serie_id, "description": None}
    ).id
    response = client.post(
        f"/v1/collections/{collection_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        "Some fields required to publish don't have a value" in response.json["message"]
    )


def test_try_to_publish_collection_of_draft_serie(client, auth_header):
    """Test case for publish_collection

    Try to publish a Collection that belongs to a draft Serie
    """
    serie_id: int = SerieModel.factory().id
    collection_id: int = CollectionModel.factory(keys={"serie_id": serie_id}).id
    response = client.post(
        f"/v1/collections/{collection_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert response.json["message"] == "The Collection must belong to an active Series"


def test_try_to_publish_collection_of_inactive_serie(client, auth_header):
    """Test case for publish_collection

    Try to publish a Collection that belongs to an inactive Serie
    """
    serie_id: int = SerieModel.factory(keys={"status": SerieStatus.INACTIVE}).id
    collection_id: int = CollectionModel.factory(keys={"serie_id": serie_id}).id
    response = client.post(
        f"/v1/collections/{collection_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert response.json["message"] == "The Collection must belong to an active Series"
