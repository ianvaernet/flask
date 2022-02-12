from dataclasses import dataclass, field
from swagger_server.graphql_schemas.queries.query import Query
from swagger_server.util import snake_to_pascal
from copy import deepcopy


@dataclass
class EnumerationValuesQuery(Query):
    """Enumeration Value Query lets you get all the values from an specific enumeration
    :Attributes:
        name: str
        body_values: list
    """

    body: dict

    def __init__(self, name: str, body_values: list):
        pascal_case_name: str = snake_to_pascal(name)
        upper_snake_case_name: str = name.upper()
        body_values_str: str = ",".join(body_values)

        body: dict = {"enumValues": body_values_str}

        self.body = {
            f'{upper_snake_case_name}: __type(name: "{pascal_case_name}")': body
        }

    # adding two enumeration_values_query
    def __add__(
        self, enumeration_values_query: "EnumerationValuesQuery"
    ) -> "EnumerationValuesQuery":
        new_query: EnumerationValuesQuery = deepcopy(self)
        new_query.body = self.body | enumeration_values_query.body
        return new_query

    def to_query(self) -> str:
        """Convert the query instance into the required query string
        :return: str
        """
        query_string: str = ""
        for key, value in self.body.items():
            value_key = list(value.keys())[0]
            value_value = value[value_key]
            query_string += "{key} {{{value_key} {{{value_value}}}}} \n".format(
                key=key,
                value_key=value_key,
                value_value=value_value,
            )
        return "query{{{body}}}".format(body=query_string)
