from swagger_server.exceptions.not_found_exception import NotFoundException


class DropNotFoundException(NotFoundException):
    def __init__(
        self,
        id,
        title="Drop not found",
    ):
        super().__init__()
        self.title = title
        self.detail = "There is no Drop with the ID=" + str(id)
