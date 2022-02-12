from flask import jsonify
from swagger_server.models import ApiResponse


def render_problem_exception(error: object):
    """Change the request exception render method

    :param error: object

    :return: Tuple[dict, int]
    """

    response_dict: dict = {
        "error": error.title,
        "code": error.status,
        "message": error.detail,
        "data": None,
    }
    response: ApiResponse = ApiResponse.from_dict(response_dict)

    return jsonify(response), error.status
