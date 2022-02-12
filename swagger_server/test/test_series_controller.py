# coding: utf-8
from __future__ import absolute_import
from datetime import datetime, timedelta, timezone
from flask import json
from swagger_server.database.enums.collection_status import CollectionStatus
from swagger_server.database.enums.serie_status import SerieStatus
from swagger_server.database.models import SerieModel, CollectionModel, EditionModel
from swagger_server.models import (
    CreateSerie,
    UpdateSerie,
)
from swagger_server.util import deserialize_datetime, format_datetime
from swagger_server.__main__ import db
from swagger_server.services import scheduler_service


def test_init():
    db.drop_all()
    db.create_all()


def test_list_series_pagination(client, auth_header):
    """Test case for list_series

    Paginate a list of series
    """
    page_size = 2
    SerieModel.factory()
    SerieModel.factory()
    SerieModel.factory()
    query_string = [("page_size", page_size), ("page", 1)]
    response = client.get("/v1/series", query_string=query_string, headers=auth_header)
    series_list = response.json["data"]["series"]
    assert response.status_code == 200
    assert response.json["data"]["total_pages"] > 0
    assert len(series_list) > 0
    assert len(series_list) <= page_size


def test_list_series_filters(client, auth_header):
    """Test case for list_series

    Filter a list of series
    """
    name = "test_list_series_filters"
    status = [SerieStatus.DRAFT.value, SerieStatus.ACTIVE.value]
    SerieModel.factory(keys={"name": name + "1", "status": status[0]})
    SerieModel.factory(keys={"name": name + "2", "status": status[1]})
    SerieModel.factory(keys={"name": name + "3", "status": SerieStatus.INACTIVE})
    query_string = [("keyword", name), ("status", ",".join(status))]
    response = client.get("/v1/series", query_string=query_string, headers=auth_header)
    series_list = response.json["data"]["series"]
    assert response.status_code == 200
    assert len(series_list) == 2


def test_list_series_search_by_name(client, auth_header):
    """Test case for list_series

    Search series by name
    """
    name = "test_list_series_search_by_name"
    SerieModel.factory()
    SerieModel.factory(keys={"name": name})
    query_string = [("keyword", name)]
    response = client.get("/v1/series", query_string=query_string, headers=auth_header)
    series_list = response.json["data"]["series"]
    assert response.status_code == 200
    assert len(series_list) == 1


def test_list_series_search_by_short_word(client, auth_header):
    """Test case for list_series

    Search series by short_word
    """
    short_word = "testListSeriesSearchByShortWord"
    SerieModel.factory()
    SerieModel.factory(keys={"short_word": short_word})
    query_string = [("keyword", short_word)]
    response = client.get("/v1/series", query_string=query_string, headers=auth_header)
    series_list = response.json["data"]["series"]
    assert response.status_code == 200
    assert len(series_list) == 1


def test_create_serie_with_required_fields(client, auth_header):
    """Test case for create_serie

    Create a new Serie only with the required fields
    """
    body = CreateSerie(
        **{
            "name": "test_create_serie_with_required_fields",
            "short_word": "createSerieWithRequiredFields",
        }
    )
    response = client.post(
        "/v1/series",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 201


def test_create_serie_with_all_fields(client, auth_header):
    """Test case for create_serie

    Create a new Serie with all the fields
    """
    publish_time = datetime.now() + timedelta(days=1)
    body = CreateSerie(
        **{
            "name": "create_serie_with_all_fields",
            "description": "create_serie_with_all_fields",
            "short_word": "createSerieWithAllFields",
            "publish_time": publish_time,
        }
    )
    response = client.post(
        "/v1/series",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 201
    serie_id = response.json["data"]["id"]
    scheduler_job = scheduler_service.get_job(f"publish_serie_{serie_id}")
    assert scheduler_job["run_date"] == str(
        publish_time.replace(tzinfo=timezone.utc).isoformat()
    )
    scheduler_service.remove_job(f"publish_serie_{serie_id}")


def test_try_to_create_serie_without_name(client, auth_header):
    """Test case for create_serie

    Try to create a new Serie without name
    """
    body = CreateSerie(
        **{
            "description": "create_serie_without_name",
            "short_word": "createSerieWithoutName",
            "publish_time": datetime.now() + timedelta(days=1),
        }
    )
    response = client.post(
        "/v1/series",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["detail"] == "'name' is a required property"


def test_try_to_create_serie_without_short_word(client, auth_header):
    """Test case for create_serie

    Try to create a new Serie without short_word
    """
    body = CreateSerie(
        **{
            "name": "create_serie_without_short_word",
            "description": "create_serie_without_short_word",
            "publish_time": datetime.now() + timedelta(days=1),
        }
    )
    response = client.post(
        "/v1/series",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["detail"] == "'short_word' is a required property"


def test_try_to_create_serie_with_past_publish_time(client, auth_header):
    """Test case for create_serie

    Try to create a new Serie with past publish_time
    """
    body = CreateSerie(
        **{
            "name": "create_serie_with_past_publish_time",
            "short_word": "createSerieWithPastPublishTime",
            "publish_time": datetime.now(),
        }
    )
    response = client.post(
        "/v1/series",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The publish_time cannot be in the past"


def test_get_serie(client, auth_header):
    """Test case for get_serie

    Get a Serie
    """
    serie = SerieModel.factory()
    serie.factory_has_many(
        {
            "collections": {
                CollectionModel: {
                    "qty": 20,
                    "key": "serie_id",
                }
            }
        }
    )
    response = client.get(f"/v1/series/{serie.id}", headers=auth_header)
    assert response.status_code == 200


def test_try_to_get_non_existent_serie(client, auth_header):
    """Test case for get_serie

    Try to get a non-existent Serie
    """
    response = client.get("/v1/series/54321", headers=auth_header)
    assert response.status_code == 404


def test_update_draft_serie(client, auth_header):
    """Test case for update_serie

    Update name, description, short_word and publish_time of a draft Serie
    """
    serie_id = SerieModel.factory(keys={"has_published_editions": False}).id
    name: str = "test_update_serie_name"
    description: str = "test_update_serie_description"
    short_word: str = "testUpdateSerieShortWord"
    publish_time: datetime = datetime.now() + timedelta(days=7)
    body = UpdateSerie(
        name=name,
        description=description,
        short_word=short_word,
        publish_time=publish_time,
    )
    response = client.put(
        f"/v1/series/{serie_id}",
        data=json.dumps(body),
        content_type="application/json",
        headers=auth_header,
    )
    assert response.status_code == 200
    assert response.json["data"]["name"] == name
    assert response.json["data"]["description"] == description
    assert response.json["data"]["short_word"] == short_word
    assert response.json["data"]["publish_time"] == format_datetime(publish_time)
    scheduler_job = scheduler_service.get_job(f"publish_serie_{serie_id}")
    assert scheduler_job["run_date"] == str(
        publish_time.replace(tzinfo=timezone.utc).isoformat()
    )
    scheduler_service.remove_job(f"publish_serie_{serie_id}")


def test_update_active_serie(client, auth_header):
    """Test case for update_serie

    Update description and short_word of an active Serie
    """
    serie_id = SerieModel.factory(
        keys={"status": SerieStatus.ACTIVE, "has_published_editions": False}
    ).id
    description: str = "test_update_active_serie_description"
    short_word: str = "testUpdateActiveSerieShortWord"
    body = UpdateSerie(description=description, short_word=short_word)
    response = client.put(
        f"/v1/series/{serie_id}",
        data=json.dumps(body),
        content_type="application/json",
        headers=auth_header,
    )
    assert response.status_code == 200
    assert response.json["data"]["description"] == description
    assert response.json["data"]["short_word"] == short_word


def test_update_short_word_of_a_serie_with_editions(client, auth_header):
    """Test case for update_serie

    Update short_word of a Serie with no published Editions
    """
    original_sku: str = "2021-shortWordOfASerieWithEditions-collection-asset"
    updated_short_word: str = "newShortWordSerieWithEditions"
    updated_sku: str = "2021-newShortWordSerieWithEditions-collection-asset"
    serie_id = SerieModel.factory(keys={"has_published_editions": False}).id
    collection_id = CollectionModel.factory(keys={"serie_id": serie_id}).id
    edition_id = EditionModel.factory(
        keys={"collection_id": collection_id, "avatar_wearable_sku": original_sku}
    ).id
    body = UpdateSerie(short_word=updated_short_word)
    response = client.put(
        f"/v1/series/{serie_id}",
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


def test_try_to_update_short_word_of_a_serie_with_published_editions(
    client, auth_header
):
    """Test case for update_serie

    Update short_word of a Serie with published Editions
    """
    original_sku: str = "2021-shortWordOfASerieWithPublishedEditions-collection-asset"
    updated_short_word: str = "newShortWordSeriePubEditions"
    serie_id = SerieModel.factory(keys={"has_published_editions": True}).id
    collection_id = CollectionModel.factory(keys={"serie_id": serie_id}).id
    edition_id = EditionModel.factory(
        keys={"collection_id": collection_id, "avatar_wearable_sku": original_sku}
    ).id
    body = UpdateSerie(short_word=updated_short_word)
    response = client.put(
        f"/v1/series/{serie_id}",
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


def test_try_to_update_serie_with_past_publish_time(client, auth_header):
    """Test case for update_serie

    Try to update a Serie with a past publish_time
    """
    serie_id = SerieModel.factory().id
    body = UpdateSerie(
        **{
            "publish_time": datetime.now(),
        }
    )
    response = client.put(
        f"/v1/series/{serie_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The publish_time cannot be in the past"


def test_try_to_update_serie_with_publish_time_after_collection(client, auth_header):
    """Test case for update_serie

    Try to update a Serie with a publish_time after Collection's publish_time
    """
    serie_id = SerieModel.factory(
        keys={"publish_time": datetime.now() + timedelta(days=1)}
    ).id
    CollectionModel.factory(
        keys={"serie_id": serie_id, "publish_time": datetime.now() + timedelta(days=2)}
    ).id
    body = UpdateSerie(
        **{
            "publish_time": datetime.now() + timedelta(days=3),
        }
    )
    response = client.put(
        f"/v1/series/{serie_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        "The Series' publish_time cannot be after the publish_time of its Collections"
        in response.json["message"]
    )


def test_try_to_update_name_of_active_serie(client, auth_header):
    """Test case for update_serie

    Try to update the name of an active Serie
    """
    serie = SerieModel.factory(keys={"status": SerieStatus.ACTIVE})
    old_name: str = serie.name
    new_name: str = "test_try_to_update_name_of_active_serie"
    body = UpdateSerie(name=new_name)
    response = client.put(
        f"/v1/series/{serie.id}",
        data=json.dumps(body),
        content_type="application/json",
        headers=auth_header,
    )
    assert response.status_code == 200
    assert response.json["data"]["name"] == old_name


def test_try_to_update_publish_time_of_active_serie(client, auth_header):
    """Test case for update_serie

    Try to update the publish_time of an active Serie
    """
    serie = SerieModel.factory(keys={"status": SerieStatus.ACTIVE})
    old_publish_time: datetime = serie.publish_time
    new_publish_time: datetime = datetime.now() + timedelta(days=5)
    body = UpdateSerie(publish_time=new_publish_time)
    response = client.put(
        f"/v1/series/{serie.id}",
        data=json.dumps(body),
        content_type="application/json",
        headers=auth_header,
    )
    assert response.status_code == 200
    assert response.json["data"]["publish_time"] == format_datetime(old_publish_time)


def test_try_to_update_short_word_of_serie_with_published_editions(client, auth_header):
    """Test case for update_serie

    Try to update the short_word of a Serie with published Editions
    """
    serie_id = SerieModel.factory(keys={"has_published_editions": True}).id
    body = UpdateSerie(short_word="serieWithPublishedEditions")
    response = client.put(
        f"/v1/series/{serie_id}",
        data=json.dumps(body),
        content_type="application/json",
        headers=auth_header,
    )
    assert response.status_code == 409
    assert "short_word cannot be updated" in response.json["message"]


def test_delete_serie(client, auth_header):
    """Test case for delete_serie

    Delete a Serie
    """
    serie_id: SerieModel = SerieModel.factory(keys={"collections_count": 0}).id
    response = client.delete(f"/v1/series/{serie_id}", headers=auth_header)
    assert response.status_code == 200


def test_try_to_delete_non_existent_serie(client, auth_header):
    """Test case for delete_serie

    Try to delete a non-existent serie
    """
    response = client.delete("/v1/series/54321", headers=auth_header)
    assert response.status_code == 404


def test_try_to_delete_active_serie(client, auth_header):
    """Test case for delete_serie

    Try to delete an active Serie
    """
    serie_id: SerieModel = SerieModel.factory(
        keys={"collections_count": 0, "status": SerieStatus.ACTIVE}
    ).id
    response = client.delete(f"/v1/series/{serie_id}", headers=auth_header)
    assert response.status_code == 403
    assert (
        response.json["message"]
        == "The Serie cannot be deleted because it has already been published"
    )


def test_try_to_delete_inactive_serie(client, auth_header):
    """Test case for delete_serie

    Try to delete an inactive Serie
    """
    serie_id: SerieModel = SerieModel.factory(
        keys={"collections_count": 0, "status": SerieStatus.INACTIVE}
    ).id
    response = client.delete(f"/v1/series/{serie_id}", headers=auth_header)
    assert response.status_code == 403
    assert (
        response.json["message"]
        == "The Serie cannot be deleted because it has already been published"
    )


def test_try_to_delete_serie_with_collections(client, auth_header):
    """Test case for delete_serie

    Try to delete a Serie that has Collections dependent on it
    """
    serie_id: SerieModel = SerieModel.factory(keys={"collections_count": 2}).id
    response = client.delete(f"/v1/series/{serie_id}", headers=auth_header)
    assert response.status_code == 409
    assert (
        response.json["message"]
        == "The Serie cannot be deleted because it has Collections dependent on it"
    )


def test_publish_serie(client, auth_header):
    """Test case for publish_serie

    Publish a serie
    """
    previous_serie_id: int = SerieModel.factory(keys={"status": SerieStatus.ACTIVE}).id
    collection_id_of_previous_serie: int = CollectionModel.factory(
        keys={"serie_id": previous_serie_id}
    ).id
    serie_id: int = SerieModel.factory(keys={"publish_time": None}).id
    response = client.post(f"/v1/series/{serie_id}/publish", headers=auth_header)
    assert response.status_code == 200
    response = client.get(f"/v1/series/{serie_id}?format=false", headers=auth_header)
    assert response.json["data"]["status"] == SerieStatus.ACTIVE.value
    publish_time = deserialize_datetime(response.json["data"]["publish_time"])
    assert publish_time <= datetime.now(publish_time.tzinfo)
    response = client.get(f"/v1/series/{previous_serie_id}", headers=auth_header)
    assert response.json["data"]["status"] == SerieStatus.INACTIVE.value
    response = client.get(
        f"/v1/collections/{collection_id_of_previous_serie}", headers=auth_header
    )
    assert response.json["data"]["status"] == CollectionStatus.INACTIVE.value


def test_try_to_publish_serie_without_description(client, auth_header):
    """Test case for publish_serie

    Try to publish a serie without description
    """
    serie_id: int = SerieModel.factory(keys={"description": None}).id
    response = client.post(
        f"/v1/series/{serie_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        "Some fields required to publish don't have a value" in response.json["message"]
    )
