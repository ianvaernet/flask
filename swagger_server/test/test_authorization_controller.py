# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.auth import Auth  # noqa: E501


def test_authorization(client):
    """Test case for authorization

    Authenticate to the genies cms backend
    """
    body = {"username": "wenceslao@42mate.com", "password": "password1"}
    response = client.post(
        "/v1/auth", data=json.dumps(body), content_type="application/json"
    )
    assert response.status_code == 200
