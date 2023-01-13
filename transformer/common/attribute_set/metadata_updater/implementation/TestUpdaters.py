from typing import List

from transformer.common.attribute_set.metadata_updater.MetadataUpdater import MetadataUpdater
from transformer.common.dto.AttributeMetadata import AttributeMetadata


class AlwaysRaisesUpdater(MetadataUpdater):
    """
    For Testing.
    """

    def update(self, dictMetadata: List[AttributeMetadata], newMetadata: List[AttributeMetadata]):
        raise AssertionError("Update should not be called")