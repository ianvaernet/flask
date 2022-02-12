from http import HTTPStatus
from requests import post, Response, exceptions
from swagger_server.exceptions import DapperException


class GraphQLService:
    api_url: str
    api_key: str

    def success(self, value: any) -> bool:
        """Get the success value mapped from the return value"""
        if isinstance(value, str):
            return value.lower() == "true"
        if isinstance(value, bool):
            return value
        raise TypeError("Invalid boolean value")

    def exec(self, query: str) -> Response:
        """Exec a query post to the dapper api

        :param query: str

        :return: Response
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            result: Response = post(
                self.api_url,
                json={"query": query},
                headers=headers,
            )
            if result.status_code == HTTPStatus.OK:
                result_dict: dict = result.json()
                # Let's check if there was any error since Dapper's api
                # sometimes returns an error with a status code 200
                if "errors" in result_dict:
                    raise DapperException(
                        endpoint=self.api_url,
                        body=query,
                        message=result_dict["errors"],
                    )
                return result_dict
            if result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
                message: str = f"""
        Invalid GraphQL Query:
            Error Message: {result.json()}
            Query: {query}
                """
                raise DapperException(
                    endpoint=self.api_url,
                    body=query,
                    message=message,
                )

        except exceptions.RequestException as exp:
            raise DapperException(self.api_url, query) from exp
