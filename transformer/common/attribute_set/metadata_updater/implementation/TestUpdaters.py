from typing import List

from common.domain.dto.AttributeMetadata import AttributeMetadata
from transformer.common.attribute_set.metadata_updater.MetadataUpdater import MetadataUpdater


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