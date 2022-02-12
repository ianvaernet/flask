from dataclasses import dataclass
from swagger_server.graphql_schemas.attribute import Attribute
from swagger_server.graphql_schemas.mutations.mutation import Mutation


@dataclass
class SellItemsMutation(Mutation):
    """Sell items mutation to put the nft to the store.

    :Attributes:
        mutation_name (str)
        nft_name (Attributes str)
        nft_storage_name (Attribute str)
        nft_flow_ids (Attribute int)
        ft_name (Attribute str)
        ft_storage_name (Attribute str)
        price (Attribute float)
        response_field (str)
    """

    mutation_name: str = "sellItems"

    nft_name: Attribute = Attribute(key="nftName", value_type=str)
    nft_storage_name: Attribute = Attribute(key="nftStorageName", value_type=str)
    nft_flow_ids: Attribute = Attribute(key="nftFlowIDs", value_type=list)
    ft_name: Attribute = Attribute(key="ftName", value_type=str)
    ft_storage_name: Attribute = Attribute(key="ftStorageName", value_type=str)
    price: Attribute = Attribute(key="price", value_type=float)
    idempotency_key: Attribute = Attribute(key="idempotencyKey", value_type=str)

    response_field: str = "success"

    def __init__(
        self,
        nft_name: str,
        nft_storage_name: str,
        nft_flow_ids: list,
        ft_name: str,
        ft_storage_name: str,
        price: float,
        idempotency_key: str,
    ):
        self.nft_name.value = nft_name
        self.nft_storage_name.value = nft_storage_name
        self.nft_flow_ids.value = nft_flow_ids
        self.ft_name.value = ft_name
        self.ft_storage_name.value = ft_storage_name
        self.price.value = price
        self.idempotency_key.value = idempotency_key
