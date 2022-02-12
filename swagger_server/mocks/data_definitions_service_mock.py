from os import environ
from swagger_server.services.graphql_service import GraphQLService
from swagger_server.graphql_schemas.queries.query import Query
from swagger_server.graphql_schemas.queries import EnumerationValuesQuery


class DataDefinitionsServiceMock(GraphQLService):
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

    def get_edition_design_slots(self) -> dict:
        """
        Get the EDITION_DESIGN_SLOTS enumeration

        :return dict
        """
        query: EnumerationValuesQuery = EnumerationValuesQuery(
            name="EDITION_DESIGN_SLOT",
            body_values=["name"],
        )
        return {
            "EDITION_DESIGN_SLOT": [
                "EDITION_DESIGN_SLOT_NIL",
                "EDITION_DESIGN_SLOT_GLASSES",
                "EDITION_DESIGN_SLOT_HELMET",
                "EDITION_DESIGN_SLOT_MASK",
                "EDITION_DESIGN_SLOT_SHIRT",
                "EDITION_DESIGN_SLOT_JACKET",
                "EDITION_DESIGN_SLOT_PANTS",
                "EDITION_DESIGN_SLOT_SHOES",
            ]
        }

    def get_edition_type(self) -> dict:
        """
        Get the EDITION_TYPE enumeration

        :return dict
        """
        query: EnumerationValuesQuery = EnumerationValuesQuery(
            name="EDITION_TYPE",
            body_values=["name"],
        )
        return {
            "EDITION_TYPE": [
                "EDITION_TYPE_AVATAR_NIL",
                "EDITION_TYPE_AVATAR_STATUE",
                "EDITION_TYPE_AVATAR_WEARABLE",
            ]
        }

    def get_edition_rarity(self) -> dict:
        """
        Get the EDITION_RARITY enumeration

        :return dict
        """
        query: EnumerationValuesQuery = EnumerationValuesQuery(
            name="EDITION_RARITY",
            body_values=["name"],
        )

        return {
            "EDITION_RARITY": [
                "EDITION_RARITY_NIL",
                "EDITION_RARITY_UNIQUE",
                "EDITION_RARITY_LEGENDARY",
                "EDITION_RARITY_EPIC",
                "EDITION_RARITY_RARE",
                "EDITION_RARITY_STANDARD",
                "EDITION_RARITY_COMMON",
            ]
        }

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

        return {
            "EDITION_DESIGN_SLOT": [
                "EDITION_DESIGN_SLOT_NIL",
                "EDITION_DESIGN_SLOT_GLASSES",
                "EDITION_DESIGN_SLOT_HELMET",
                "EDITION_DESIGN_SLOT_MASK",
                "EDITION_DESIGN_SLOT_SHIRT",
                "EDITION_DESIGN_SLOT_JACKET",
                "EDITION_DESIGN_SLOT_PANTS",
                "EDITION_DESIGN_SLOT_SHOES",
            ],
            "EDITION_TYPE": [
                "EDITION_TYPE_AVATAR_NIL",
                "EDITION_TYPE_AVATAR_STATUE",
                "EDITION_TYPE_AVATAR_WEARABLE",
            ],
            "EDITION_RARITY": [
                "EDITION_RARITY_NIL",
                "EDITION_RARITY_UNIQUE",
                "EDITION_RARITY_LEGENDARY",
                "EDITION_RARITY_EPIC",
                "EDITION_RARITY_RARE",
                "EDITION_RARITY_STANDARD",
                "EDITION_RARITY_COMMON",
            ],
        }
