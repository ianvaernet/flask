from connexion.exceptions import ProblemException
from werkzeug.exceptions import HTTPException


class BadRequestException(ProblemException):
    def __init__(
        self,
        title="Bad request",
        detail=None,
        headers=None,
        type=HTTPException,
        instance=None,
        ext=None,
    ):
        super().__init__()
        self.title = title
        self.detail = detail
        self.headers = headers
        self.type = type
        self.instance = instance
        self.ext = ext
