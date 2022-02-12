from swagger_server.exceptions.not_found_exception import NotFoundException


class DropEditionNotFoundException(NotFoundException):
    def __init__(
        self,
        drop_id,
        edition_id,
        title="Drop edition not found",
    ):
        super().__init__()
        self.title = title
        self.detail = (
            "There is no Drop Edition for these drop and edition ids "
            + str(drop_id)
            + " and "
            + str(edition_id)
        )
