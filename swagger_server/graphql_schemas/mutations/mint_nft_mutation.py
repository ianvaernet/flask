import os
from dataclasses import dataclass, field
from swagger_server.graphql_schemas.mutations.mutation import Mutation
from swagger_server.graphql_schemas.attribute import Attribute
from swagger_server.graphql_schemas.schemas import MintNftOrderInputSchema


@dataclass
class MintNftMutation(Mutation):
    """MintNftMutation class represents a mint nft mutation to run the minting
    process in the dapper api

    :Attribute:
        mutation_name: str
        orders: Attribute (list)
        wallet: Attribute (str)

        response_field: str
    """

    mutation_name: str = "mintNFTs"

    orders: Attribute = Attribute(key="orders", value_type=list)
    wallet: Attribute = Attribute(key="flowReceiverAddress", value_type=str)
    idempotency_key: Attribute = Attribute(key="idempotencyKey", value_type=str)

    response_field: list = field(default_factory=lambda: ["success", "mintedNFTs"])

    def __init__(self, edition_id: int, quantity: int, idempotency_key: str):
        order: MintNftOrderInputSchema = MintNftOrderInputSchema()
        order.edition_id.value = edition_id
        order.quantity.value = quantity
        orders = []
        orders.append(order)
        self.orders.value = orders
        self.wallet.value = os.getenv("WALLET")
        mintedNFTs: str = "mintedNFTs {nftFlowID}"
        self.idempotency_key.value = idempotency_key
        self.response_field = ["success", mintedNFTs]
