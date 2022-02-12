from dataclasses import dataclass


@dataclass
class AddCollectionResult:
    status: bool
    collection_id: int
