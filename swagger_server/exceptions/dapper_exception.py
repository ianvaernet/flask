class DapperException(Exception):
    def __init__(
        self, endpoint: str, body: str, message="Error performing the request"
    ):
        self.endpoint = endpoint
        self.body = body
        super().__init__(message)
