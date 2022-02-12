# coding: utf-8
from __future__ import absolute_import
from flask import json
from swagger_server.database.enums import DropStatus
from swagger_server.database.enums.edition_status import EditionStatus
from swagger_server.database.models import (
    CollectionModel,
    EditionModel,
    DropModel,
    DropEditionModel,
    NftModel,
)
from swagger_server.models import (
    CreateDrop,
    UpdateDrop,
    CreateOrUpdateDropEdition,
)
from datetime import datetime, timedelta, timezone
from swagger_server.services import scheduler_service
from swagger_server.util import deserialize_datetime
from swagger_server.__main__ import db


def test_init():
    db.drop_all()
    db.create_all()


def test_list_drops_pagination(client, auth_header):
    """Test case for list_drops pagination"""
    page_size = 2
    DropModel.factory()
    DropModel.factory()
    DropModel.factory()
    query_string = [("page_size", page_size), ("page", 1)]
    response = client.get("/v1/drops", query_string=query_string, headers=auth_header)
    drops_list = response.json["data"]["drops"]
    assert response.status_code == 200
    assert response.json["data"]["total_pages"] > 0
    assert len(drops_list) > 0
    assert len(drops_list) <= page_size


def test_list_drops_filters(client, auth_header):
    """Test case for list_drops filters"""
    title = "test_list_drops_filters"
    status = [DropStatus.DRAFT.value, DropStatus.PUBLISHED.value]
    DropModel.factory(keys={"title": title + "1", "status": status[0]})
    DropModel.factory(keys={"title": title + "2", "status": status[1]})
    DropModel.factory(keys={"title": title + "3", "status": DropStatus.FINISHED})
    query_string = [("keyword", title), ("status", ",".join(status))]
    response = client.get("/v1/drops", query_string=query_string, headers=auth_header)
    drops_list = response.json["data"]["drops"]
    assert response.status_code == 200
    assert len(drops_list) == 2


def test_list_drops_search_by_title(client, auth_header):
    """Test case for list_drops search"""
    title = "test_list_drops_search_by_title"
    DropModel.factory()
    DropModel.factory(keys={"title": title})
    query_string = [("keyword", title)]
    response = client.get("/v1/drops", query_string=query_string, headers=auth_header)
    drops_list = response.json["data"]["drops"]
    assert response.status_code == 200
    assert len(drops_list) == 1


def test_create_drop_with_required_fields(client, auth_header):
    """Test case for create_drop

    Create a new Drop only with the required fields
    """
    body = CreateDrop(
        title="create_drop_with_required_fields_title",
    )
    response = client.post(
        "/v1/drops",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 201


def test_create_drop_with_all_fields(client, auth_header):
    """Test case for create_drop

    Create a new Drop with all the fields
    """
    edition: EditionModel = EditionModel.factory(
        has_one={"collection_id": CollectionModel},
        keys={"status": EditionStatus.ON_SALE, "reserve_percentage": 10},
    )
    edition.factory_has_many({"nfts": {NftModel: {"qty": 10, "key": "edition_id"}}})
    drop_editions: list = [CreateOrUpdateDropEdition(edition_id=edition.id, price=7.5)]
    publish_time = datetime.now() + timedelta(days=1)
    body = CreateDrop(
        title="create_drop_with_all_fields_title",
        description="create_drop_with_all_fields_description",
        publish_time=publish_time,
        start_time=datetime.now() + timedelta(days=2),
        end_time=datetime.now() + timedelta(days=7),
        image_url="https://drop_image.test",
        drop_editions=drop_editions,
    )
    response = client.post(
        "/v1/drops",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 201
    drop_id = response.json["data"]["id"]
    scheduler_job = scheduler_service.get_job(f"publish_drop_{drop_id}")
    assert scheduler_job["run_date"] == str(
        publish_time.replace(tzinfo=timezone.utc).isoformat()
    )
    scheduler_service.remove_job(f"publish_drop_{drop_id}")


def test_try_to_create_drop_with_draft_editions(client, auth_header):
    """Test case for create_drop

    Try to create a new Drop with Editions in draft status
    """
    edition: EditionModel = EditionModel.factory(
        has_one={"collection_id": CollectionModel},
        keys={"status": EditionStatus.DRAFT},
    )
    drop_editions: list = [CreateOrUpdateDropEdition(edition_id=edition.id, price=7.5)]
    body = CreateDrop(
        title="tryToCreateDropWithDraftEditions",
        drop_editions=drop_editions,
    )
    response = client.post(
        "/v1/drops",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        "is not on sale yet, so it cannot be part of a Drop" in response.json["message"]
    )


def test_try_to_create_drop_with_created_editions(client, auth_header):
    """Test case for create_drop

    Try to create a new Drop with Editions in created status
    """
    edition: EditionModel = EditionModel.factory(
        has_one={"collection_id": CollectionModel},
        keys={"status": EditionStatus.CREATED},
    )
    drop_editions: list = [CreateOrUpdateDropEdition(edition_id=edition.id, price=12)]
    body = CreateDrop(
        title="tryToCreateDropWithCreatedEditions",
        drop_editions=drop_editions,
    )
    response = client.post(
        "/v1/drops",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        "is not on sale yet, so it cannot be part of a Drop" in response.json["message"]
    )


def test_try_to_create_drop_with_minted_editions(client, auth_header):
    """Test case for create_drop

    Try to create a new Drop with Editions in minted status
    """
    edition: EditionModel = EditionModel.factory(
        has_one={"collection_id": CollectionModel},
        keys={"status": EditionStatus.MINTED},
    )
    drop_editions: list = [CreateOrUpdateDropEdition(edition_id=edition.id, price=10.3)]
    body = CreateDrop(
        title="tryToCreateDropWithMintedEditions",
        drop_editions=drop_editions,
    )
    response = client.post(
        "/v1/drops",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        "is not on sale yet, so it cannot be part of a Drop" in response.json["message"]
    )


# def test_try_to_create_drop_with_editions_without_stock(client, auth_header):
#     """Test case for create_drop

#     Try to create a new Drop with Editions without available stock
#     """
#     edition: EditionModel = EditionModel.factory(
#         has_one={"collection_id": CollectionModel},
#         keys={"status": EditionStatus.ON_SALE},
#     )
#     drop_editions: list = [CreateOrUpdateDropEdition(edition_id=edition.id, price=5)]
#     body = CreateDrop(
#         title="tryToCreateDropWithEditionsWithoutStock",
#         drop_editions=drop_editions,
#     )
#     response = client.post(
#         "/v1/drops",
#         data=json.dumps(body),
#         headers=auth_header,
#         content_type="application/json",
#     )
#     assert response.status_code == 400


def test_try_to_create_drop_with_past_publish_time(client, auth_header):
    """Test case for create_drop

    Try to create a new Drop with a past publish_time
    """
    edition_id = EditionModel.factory().id
    body = CreateDrop(
        **{
            "title": "create_drop_with_past_publish_time",
            "description": "create_drop_with_past_publish_time",
            "image_url": "https://drop_image.test",
            "drop_editions": [
                CreateOrUpdateDropEdition(edition_id=edition_id, price=7)
            ],
            "publish_time": datetime.now(),
        }
    )
    response = client.post(
        "/v1/drops",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The publish_time cannot be in the past"


def test_try_to_create_drop_without_title(client, auth_header):
    """Test case for create_drop

    Try to create a new Drop without title
    """
    body = CreateDrop(
        description="create_drop_without_title_description",
        start_time=datetime.now(),
        end_time=datetime.now(),
        publish_time=datetime.now(),
        image_url="https://drop_image.test",
    )
    response = client.post(
        "/v1/drops",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["detail"] == "'title' is a required property"


def test_try_to_create_drop_with_negative_price(client, auth_header):
    """Test case for create_drop

    Try to create a new Drop with negative drop_editions price
    """
    edition: EditionModel = EditionModel.factory(
        has_one={"collection_id": CollectionModel},
        keys={"status": EditionStatus.ON_SALE},
    )
    drop_editions: list = [CreateOrUpdateDropEdition(edition_id=edition.id, price=-12)]
    body = CreateDrop(
        title="create_drop_with_required_fields_title",
        drop_editions=drop_editions,
    )
    response = client.post(
        "/v1/drops",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The price must be greater than or equal to 0"


def test_try_to_create_drop_with_past_start_time(client, auth_header):
    """Test case for create_drop

    Try to create a new Drop with a past start_time
    """
    body = CreateDrop(
        **{
            "title": "create_drop_with_past_publish_time",
            "start_time": datetime.now(),
        }
    )
    response = client.post(
        "/v1/drops",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The start_time cannot be in the past"


def test_try_to_create_drop_with_start_time_after_end_time(client, auth_header):
    """Test case for create_drop

    Try to create a new Drop with start_time after end_time
    """
    body = CreateDrop(
        title="create_drop_with_required_fields_title",
        start_time=datetime.now() + timedelta(days=2),
        end_time=datetime.now() + timedelta(days=1),
    )
    response = client.post(
        "/v1/drops",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The end_time must be after the start_time"


def test_get_drop(client, auth_header):
    """Test case for get_drop

    Get a drop
    """
    drop: DropModel = DropModel.factory()
    edition: EditionModel = EditionModel.factory(
        has_one={"collection_id": CollectionModel},
        keys={"status": DropStatus.ON_SALE.value},
    )
    DropEditionModel.factory(keys={"edition_id": edition.id, "drop_id": drop.id})
    response = client.get(f"/v1/drops/{drop.id}", headers=auth_header)
    assert response.status_code == 200


def test_update_drop(client, auth_header):
    """Test case for update_drop

    Update a drop
    """
    edition: EditionModel = EditionModel.factory(keys={"status": EditionStatus.ON_SALE})
    edition.factory_has_many({"nfts": {NftModel: {"qty": 10, "key": "edition_id"}}})
    drop: DropModel = DropModel.factory()
    publish_time = datetime.now() + timedelta(hours=1)
    body = UpdateDrop(
        title="update_drop_title",
        description="update_drop_description",
        image_url="https://drop_image.test",
        publish_time=publish_time,
        start_time=datetime.now() + timedelta(days=1),
        end_time=datetime.now() + timedelta(days=8),
        drop_editions=[CreateOrUpdateDropEdition(edition_id=edition.id, price=10)],
    )
    response = client.put(
        f"/v1/drops/{drop.id}",
        headers=auth_header,
        data=json.dumps(body),
        content_type="application/json",
    )
    assert response.status_code == 200
    scheduler_job = scheduler_service.get_job(f"publish_drop_{drop.id}")
    assert scheduler_job["run_date"] == str(
        publish_time.replace(tzinfo=timezone.utc).isoformat()
    )
    scheduler_service.remove_job(f"publish_drop_{drop.id}")


def test_try_to_update_drop_adding_draft_editions(client, auth_header):
    """Test case for update_drop

    Try to update a Drop adding Editions in draft status
    """
    drop_id: int = DropModel.factory().id
    edition: EditionModel = EditionModel.factory(
        has_one={"collection_id": CollectionModel},
        keys={"status": EditionStatus.DRAFT},
    )
    drop_editions: list = [CreateOrUpdateDropEdition(edition_id=edition.id, price=7.5)]
    body = UpdateDrop(
        title="tryToUpdateDropAddingDraftEditions",
        drop_editions=drop_editions,
    )
    response = client.put(
        f"/v1/drops/{drop_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        "is not on sale yet, so it cannot be part of a Drop" in response.json["message"]
    )


def test_try_to_update_drop_adding_created_editions(client, auth_header):
    """Test case for update_drop

    Try to update a Drop adding Editions in created status
    """
    drop_id: int = DropModel.factory().id
    edition: EditionModel = EditionModel.factory(
        has_one={"collection_id": CollectionModel},
        keys={"status": EditionStatus.CREATED},
    )
    drop_editions: list = [CreateOrUpdateDropEdition(edition_id=edition.id, price=15)]
    body = UpdateDrop(
        title="tryToUpdateDropAddingCreatedEditions",
        drop_editions=drop_editions,
    )
    response = client.put(
        f"/v1/drops/{drop_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        "is not on sale yet, so it cannot be part of a Drop" in response.json["message"]
    )


def test_try_to_update_drop_adding_minted_editions(client, auth_header):
    """Test case for update_drop

    Try to update a Drop adding Editions in minted status
    """
    drop_id: int = DropModel.factory().id
    edition: EditionModel = EditionModel.factory(
        has_one={"collection_id": CollectionModel},
        keys={"status": EditionStatus.MINTED},
    )
    drop_editions: list = [CreateOrUpdateDropEdition(edition_id=edition.id, price=3)]
    body = UpdateDrop(
        title="tryToUpdateDropAddingMintedEditions",
        drop_editions=drop_editions,
    )
    response = client.put(
        f"/v1/drops/{drop_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert (
        "is not on sale yet, so it cannot be part of a Drop" in response.json["message"]
    )


# def test_try_to_update_drop_adding_editions_without_stock(client, auth_header):
#     """Test case for update_drop

#     Try to update a Drop adding Editions in draft status
#     """
#     drop_id: int = DropModel.factory().id
#     edition: EditionModel = EditionModel.factory(
#         has_one={"collection_id": CollectionModel},
#         keys={"status": EditionStatus.ON_SALE},
#     )
#     drop_editions: list = [CreateOrUpdateDropEdition(edition_id=edition.id, price=7)]
#     body = UpdateDrop(
#         title="tryToUpdateDropAddingEditionsWithoutStock",
#         drop_editions=drop_editions,
#     )
#     response = client.put(
#         f"/v1/drops/{drop_id}",
#         data=json.dumps(body),
#         headers=auth_header,
#         content_type="application/json",
#     )
#     assert response.status_code == 400


def test_try_to_update_drop_with_past_publish_time(client, auth_header):
    """Test case for update_drop

    Try to update a Drop with a past publish_time
    """
    drop_id = DropModel.factory().id
    body = UpdateDrop(
        **{
            "publish_time": datetime.now(),
        }
    )
    response = client.put(
        f"/v1/drops/{drop_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The publish_time cannot be in the past"


def test_try_to_update_drop_with_negative_price(client, auth_header):
    """Test case for update_drop

    Try to update a Drop with negative drop_editions price
    """
    edition_id: int = EditionModel.factory(
        has_one={"collection_id": CollectionModel},
        keys={"status": EditionStatus.ON_SALE},
    ).id
    drop_id: int = DropModel.factory().id
    DropEditionModel.factory(
        keys={"edition_id": edition_id, "drop_id": drop_id, "price": 5}
    )
    drop_editions: list = [CreateOrUpdateDropEdition(edition_id=edition_id, price=-4)]
    body = UpdateDrop(drop_editions=drop_editions)
    response = client.put(
        f"/v1/drops/{drop_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The price must be greater than or equal to 0"


def test_try_to_update_drop_with_start_time_after_end_time(client, auth_header):
    """Test case for update_drop

    Try to update a Drop with start_time after end_time
    """
    drop_id = DropModel.factory().id
    body = UpdateDrop(
        start_time=datetime.now() + timedelta(days=1),
        end_time=datetime.now() + timedelta(hours=12),
    )
    response = client.put(
        f"/v1/drops/{drop_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The end_time must be after the start_time"


def test_try_to_update_start_time_of_drop_with_end_time(client, auth_header):
    """Test case for update_drop

    Try to update a Drop setting the start_time after the end_time already set
    """
    drop_id = DropModel.factory(
        keys={
            "start_time": datetime.now() + timedelta(days=1),
            "end_time": datetime.now() + timedelta(days=2),
        }
    ).id
    body = UpdateDrop(start_time=datetime.now() + timedelta(days=3))
    response = client.put(
        f"/v1/drops/{drop_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The end_time must be after the start_time"


def test_try_to_update_end_time_of_drop_with_start_time(client, auth_header):
    """Test case for update_drop

    Try to update a Drop setting the end_time before the start_time already set
    """
    drop_id = DropModel.factory(
        keys={
            "start_time": datetime.now() + timedelta(days=1),
            "end_time": datetime.now() + timedelta(days=2),
        }
    ).id
    body = UpdateDrop(end_time=datetime.now() + timedelta(hours=12))
    response = client.put(
        f"/v1/drops/{drop_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The end_time must be after the start_time"


def test_try_to_update_drop_with_past_start_time(client, auth_header):
    """Test case for update_drop

    Try to update a Drop with past start_time
    """
    drop_id = DropModel.factory().id
    body = UpdateDrop(
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=12),
    )
    response = client.put(
        f"/v1/drops/{drop_id}",
        data=json.dumps(body),
        headers=auth_header,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["message"] == "The start_time cannot be in the past"


def test_delete_drop(client, auth_header):
    """Test case for delete_drop

    Delete a drop
    """
    drop: DropModel = DropModel.factory()
    response = client.delete(f"/v1/drops/{drop.id}", headers=auth_header)
    assert response.status_code == 200


def test_publish_drop(client, auth_header):
    """Test case for publish_drop

    Publish a drop to the dapper system
    """
    edition_id: int = EditionModel.factory(keys={"status": EditionStatus.ON_SALE}).id
    drop_id: int = DropModel.factory(
        keys={
            "publish_time": None,
            "start_time": datetime.now() + timedelta(days=1),
            "end_time": datetime.now() + timedelta(days=4),
        }
    ).id
    DropEditionModel.factory(keys={"drop_id": drop_id, "edition_id": edition_id})
    response = client.post(
        f"/v1/drops/{drop_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 200
    response = client.get(f"/v1/drops/{drop_id}?format=false", headers=auth_header)
    publish_time = deserialize_datetime(response.json["data"]["publish_time"])
    start_time = deserialize_datetime(response.json["data"]["start_time"])
    end_time = deserialize_datetime(response.json["data"]["end_time"])
    assert response.json["data"]["status"] == DropStatus.PUBLISHED.value
    assert publish_time <= datetime.now(publish_time.tzinfo)
    scheduler_on_sale_job = scheduler_service.get_job(f"set_on_sale_drop_{drop_id}")
    assert scheduler_on_sale_job["run_date"] == str(
        start_time.replace(tzinfo=timezone.utc).isoformat()
    )
    scheduler_service.remove_job(f"set_on_sale_drop_{drop_id}")
    scheduler_finished_job = scheduler_service.get_job(f"set_finished_drop_{drop_id}")
    assert scheduler_finished_job["run_date"] == str(
        end_time.replace(tzinfo=timezone.utc).isoformat()
    )
    scheduler_service.remove_job(f"set_finished_drop_{drop_id}")


def test_publish_drop_without_start_time(client, auth_header):
    """Test case for publish_drop

    Publish a drop without start_time to the dapper system
    """
    edition_id: int = EditionModel.factory(keys={"status": EditionStatus.ON_SALE}).id
    drop_id: int = DropModel.factory(
        keys={
            "publish_time": None,
            "start_time": None,
            "end_time": datetime.now() + timedelta(days=7),
        }
    ).id
    DropEditionModel.factory(keys={"drop_id": drop_id, "edition_id": edition_id})
    response = client.post(
        f"/v1/drops/{drop_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 200
    response = client.get(f"/v1/drops/{drop_id}?format=false", headers=auth_header)
    publish_time = deserialize_datetime(response.json["data"]["publish_time"])
    end_time = deserialize_datetime(response.json["data"]["end_time"])
    assert response.json["data"]["status"] == DropStatus.ON_SALE.value
    assert publish_time <= datetime.now(publish_time.tzinfo)
    assert response.json["data"]["publish_time"] == response.json["data"]["start_time"]
    scheduler_finished_job = scheduler_service.get_job(f"set_finished_drop_{drop_id}")
    assert scheduler_finished_job["run_date"] == str(
        end_time.replace(tzinfo=timezone.utc).isoformat()
    )
    scheduler_service.remove_job(f"set_finished_drop_{drop_id}")


def test_publish_drop_without_end_time(client, auth_header):
    """Test case for publish_drop

    Publish a drop without end_time to the dapper system
    """
    edition_id: int = EditionModel.factory(keys={"status": EditionStatus.ON_SALE}).id
    drop_id: int = DropModel.factory(
        keys={
            "publish_time": None,
            "start_time": datetime.now() + timedelta(days=1),
            "end_time": None,
        }
    ).id
    DropEditionModel.factory(keys={"drop_id": drop_id, "edition_id": edition_id})
    response = client.post(
        f"/v1/drops/{drop_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 200
    response = client.get(f"/v1/drops/{drop_id}?format=false", headers=auth_header)
    publish_time = deserialize_datetime(response.json["data"]["publish_time"])
    start_time = deserialize_datetime(response.json["data"]["start_time"])
    assert response.json["data"]["status"] == DropStatus.PUBLISHED.value
    assert publish_time <= datetime.now(publish_time.tzinfo)
    scheduler_on_sale_job = scheduler_service.get_job(f"set_on_sale_drop_{drop_id}")
    assert scheduler_on_sale_job["run_date"] == str(
        start_time.replace(tzinfo=timezone.utc).isoformat()
    )
    scheduler_service.remove_job(f"set_on_sale_drop_{drop_id}")


def test_try_to_publish_drop_without_description(client, auth_header):
    """Test case for publish_drop

    Try to publish a Drop without description
    """
    edition_id: int = EditionModel.factory().id
    drop_id: int = DropModel.factory(
        keys={
            "description": None,
            "publish_time": None,
            "start_time": datetime.now() + timedelta(days=1),
            "end_time": datetime.now() + timedelta(days=4),
        }
    ).id
    DropEditionModel.factory(keys={"drop_id": drop_id, "edition_id": edition_id})
    response = client.post(
        f"/v1/drops/{drop_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        "Some fields required to publish don't have a value" in response.json["message"]
    )


def test_try_to_publish_drop_without_image_url(client, auth_header):
    """Test case for publish_drop

    Try to publish a Drop without image_url
    """
    edition_id: int = EditionModel.factory().id
    drop_id: DropModel = DropModel.factory(
        keys={
            "image_url": None,
            "publish_time": None,
            "start_time": datetime.now() + timedelta(days=1),
            "end_time": datetime.now() + timedelta(days=4),
        }
    ).id
    DropEditionModel.factory(keys={"drop_id": drop_id, "edition_id": edition_id})
    response = client.post(
        f"/v1/drops/{drop_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        "Some fields required to publish don't have a value" in response.json["message"]
    )


def test_try_to_publish_drop_without_drop_editions(client, auth_header):
    """Test case for publish_drop

    Try to publish a Drop without drop_editions
    """
    drop: DropModel = DropModel.factory(
        keys={
            "publish_time": None,
            "start_time": datetime.now() + timedelta(days=1),
            "end_time": datetime.now() + timedelta(days=4),
        }
    )
    response = client.post(
        f"/v1/drops/{drop.id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert (
        "Some fields required to publish don't have a value" in response.json["message"]
    )


def test_try_to_publish_drop_with_past_start_time(client, auth_header):
    """Test case for publish_drop

    Try to publish a drop with start_time in the past
    """
    edition_id: int = EditionModel.factory().id
    drop_id: int = DropModel.factory(
        keys={
            "publish_time": None,
            "start_time": datetime.now(),
            "dapper_drop_id": None,
        }
    ).id
    DropEditionModel.factory(keys={"drop_id": drop_id, "edition_id": edition_id})
    response = client.post(
        f"/v1/drops/{drop_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert response.json["message"] == "The start_time cannot be in the past"


def test_try_to_publish_drop_with_start_time_after_end_time(client, auth_header):
    """Test case for publish_drop

    Try to publish a drop with start_time after end_time
    """
    edition_id: int = EditionModel.factory().id
    drop_id: int = DropModel.factory(
        keys={
            "publish_time": None,
            "start_time": datetime.now() + timedelta(days=2),
            "end_time": datetime.now() + timedelta(days=1),
            "dapper_drop_id": None,
        }
    ).id
    DropEditionModel.factory(keys={"drop_id": drop_id, "edition_id": edition_id})
    response = client.post(
        f"/v1/drops/{drop_id}/publish",
        headers=auth_header,
    )
    assert response.status_code == 400
    assert response.json["message"] == "The end_time must be after the start_time"
