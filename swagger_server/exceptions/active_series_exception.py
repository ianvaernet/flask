from swagger_server.exceptions.conflict_exception import ConflictException


class ActiveSerieException(ConflictException):
    def __init__(self):
        super().__init__()
        self.title = "Current active Series cannot be replaced"
        self.detail = "There are Collections scheduled to be published in the Series"
