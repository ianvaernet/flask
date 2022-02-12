from connexion.exceptions import ProblemException
from werkzeug.exceptions import HTTPException


class InternalException(ProblemException):
    def __init__(
        self,
        title="Internal error",
        detail=None,
        headers=None,
        type=HTTPException,
        status=500,
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
