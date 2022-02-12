# coding: utf-8
from __future__ import absolute_import
from flask import json


def test_list_enumerations(client, auth_header):
    """Test case for list enumerations"""
    response = client.get("/v1/enumerations", headers=auth_header)
    enumerations_list = response.json["data"]
    assert response.status_code == 200
    assert len(enumerations_list) > 0


def test_get_design_slots(client, auth_header):
    """Test case for get design slotsn"""
    response = client.get("/v1/enumerations/edition-design-slots", headers=auth_header)
    enumerations_list = response.json["data"]
    assert response.status_code == 200
    assert len(enumerations_list) > 0


def test_get_types(client, auth_header):
    """Test case for get types enumerations"""
    response = client.get("/v1/enumerations/edition-types", headers=auth_header)
    enumerations_list = response.json["data"]
    assert response.status_code == 200
    assert len(enumerations_list) > 0


def test_get_rarities(client, auth_header):
    """Test case for get rarity enumerations"""
    response = client.get("/v1/enumerations/edition-rarity", headers=auth_header)
    enumerations_list = response.json["data"]
    assert response.status_code == 200
    assert len(enumerations_list) > 0
