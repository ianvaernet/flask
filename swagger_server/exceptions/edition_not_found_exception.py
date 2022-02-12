from swagger_server.exceptions.not_found_exception import NotFoundException


class EditionNotFoundException(NotFoundException):
    def __init__(self, id, title="Edition not found"):
        super().__init__()
        self.title = title
        self.detail = "There is no Edition with ID=" + str(id)
