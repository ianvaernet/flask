from swagger_server.exceptions.not_found_exception import NotFoundException


class CollectionNotFoundException(NotFoundException):
    def __init__(self, id, title="Collection not found"):
        super().__init__()
        self.title = title
        self.detail = "There is no Collection with the ID=" + str(id)
