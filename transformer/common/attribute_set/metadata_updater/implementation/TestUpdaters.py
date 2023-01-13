from typing import List

from transformer.common.attribute_set.metadata_updater.MetadataUpdater import MetadataUpdater
from transformer.common.dto.AttributeMetadata import AttributeMetadata


class AlwaysRaises(MetadataUpdater):
    """
    For Testing.
    """

    def update(self, dictMetadata: List[AttributeMetadata], newMetadata: List[AttributeMetadata]) -> bool:
        raise AssertionError("Update should not be called")

class AlwaysUpdates(MetadataUpdater):

    def update(self, dictMetadata: List[AttributeMetadata], newMetadata: List[AttributeMetadata]) -> bool:
        return True

class NeverUpdates(MetadataUpdater):

    def update(self, dictMetadata: List[AttributeMetadata], newMetadata: List[AttributeMetadata]) -> bool:
        return False