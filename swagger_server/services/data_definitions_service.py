from os import environ
from swagger_server.services.graphql_service import GraphQLService
from swagger_server.graphql_schemas.queries.query import Query
from swagger_server.graphql_schemas.queries import EnumerationValuesQuery
from swagger_server.util import print_to_err


class DataDefinitionsService(GraphQLService):
    """
    Data Definition Service used to get all the required data definitions from
    dappers api
    """

    api_url: str
    api_key: str

    def __init__(
        self,
    ) -> None:
        self.api_url = environ.get("DAPPER_URL")
        self.api_key = environ.get("DAPPER_API_KEY")

    def query(self, query: Query) -> dict:
        query_str = query.to_query()
        return self.exec(query_str)

    def format_enumerations(self, enumerations_dict: dict) -> dict:
        """
        Format the enumerations response from dappers api to be:
        { "enumeration_name": [ enumeration_value ] }

        :param enumerations_dict: dict

        :return dict
        """
        new_enumerations_dict: dict = {}
        for key, enumeration in enumerations_dict.items():
            enumeration_instance: dict = enumeration["enumValues"]
            enumeration_values: list = []
            for value in enumeration_instance:
                enumeration_values.append(value["name"])
            new_enumerations_dict[key] = enumeration_values

        return new_enumerations_dict

    def get_edition_design_slots(self) -> dict:
        """
        Get the EDITION_DESIGN_SLOTS enumeration

        :return dict
        """
        query: EnumerationValuesQuery = EnumerationValuesQuery(
            name="EDITION_DESIGN_SLOT",
            body_values=["name"],
        )
        return self.get_enumeration(query)

    def get_edition_type(self) -> dict:
        """
        Get the EDITION_TYPE enumeration

        :return dict
        """
        query: EnumerationValuesQuery = EnumerationValuesQuery(
            name="EDITION_TYPE",
            body_values=["name"],
        )
        return self.get_enumeration(query)

    def get_edition_rarity(self) -> dict:
        """
        Get the EDITION_RARITY enumeration

        :return dict
        """
        query: EnumerationValuesQuery = EnumerationValuesQuery(
            name="EDITION_RARITY",
            body_values=["name"],
        )
        return self.get_enumeration(query)

    def get_enumeration(self, query: EnumerationValuesQuery) -> dict:
        """
        Get an specifc enumeration

        :return dict
        """
        result_dict: dict = self.query(query)
        formated_enumerations: dict = self.format_enumerations(result_dict["data"])
        return formated_enumerations

    def get_enumerations(self) -> dict:
        """
        Get the enumeration dictionary
        """
        edition_rarity_query: EnumerationValuesQuery = EnumerationValuesQuery(
            name="EDITION_RARITY",
            body_values=["name"],
        )
        edition_design_slot_query: EnumerationValuesQuery = EnumerationValuesQuery(
            name="EDITION_DESIGN_SLOT",
            body_values=["name"],
        )
        edition_type_query: EnumerationValuesQuery = EnumerationValuesQuery(
            name="EDITION_TYPE",
            body_values=["name"],
        )

        query: EnumerationValuesQuery = (
            edition_design_slot_query + edition_rarity_query + edition_type_query
        )
        return self.get_enumeration(query)
