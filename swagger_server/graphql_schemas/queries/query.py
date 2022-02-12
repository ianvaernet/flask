import json
import sys
import abc
from dataclasses import asdict, is_dataclass
from functools import reduce
from swagger_server.graphql_schemas.base_schema import BaseSchema


class Query(BaseSchema):
    """Query abstract class used to describe the base query methods that any
    query should include to be able to generate the query required to
    perform an action in the dapper api
    """

    def to_query(self) -> str:
        """Convert the query instance into the required mutation string
        :return: str
        """
        mutation_body: str = self.to_query_body()
        response_field: str
        if isinstance(self.response_field, list):
            response_field = ",".join(self.response_field)
        else:
            response_field = self.response_field
        return "query{{{name}(input:{body}){{{response_field}}}}}".format(
            name=self.mutation_name, body=mutation_body, response_field=response_field
        )
