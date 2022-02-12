from connexion.exceptions import ProblemException
from werkzeug.exceptions import HTTPException


class ConflictException(ProblemException):
    def __init__(
        self,
        title="Conflict processing the request",
        detail=None,
        headers=None,
        type=HTTPException,
        status=409,
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
