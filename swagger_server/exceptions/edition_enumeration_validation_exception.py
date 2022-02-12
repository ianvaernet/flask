from connexion.exceptions import ProblemException
from werkzeug.exceptions import HTTPException
from http import HTTPStatus


class EditionEnumerationValidationException(ProblemException):
    def __init__(
        self,
        title="Invalid Enumeration",
        detail=None,
        headers=None,
        type=HTTPException,
        status=HTTPStatus.BAD_REQUEST,
        instance=None,
        ext=None,
    ):
        self.title = title
        self.detail = detail
        self.headers = headers
        self.type = type
        self.status = status
        self.instance = instance
        self.ext = ext
