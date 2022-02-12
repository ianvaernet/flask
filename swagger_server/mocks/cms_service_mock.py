class CmsServiceMock:
    """Mock client to consume the cms resources"""

    def __init__(self):
        pass

    def get_wearable_data(self, id: int) -> dict:
        """Get SKU, images and videos of the wearable with the specified id from the CMS

        :param id: int

        :return: dict
        """
        return {
            "sku": "2021-serie-collection-asset",
            "collection_id": id,
            "file_list": [
                "http://genies.test/hero.png",
                "http://genies.test/mannequin-1.png",
                "http://genies.test/unboxing.mp4",
            ],
        }
