from swagger_server.exceptions.not_found_exception import NotFoundException


class SerieNotFoundException(NotFoundException):
    def __init__(self, id, title="Serie not found"):
        super().__init__()
        self.title = title
        self.detail = "There is no Serie with the ID=" + str(id)
