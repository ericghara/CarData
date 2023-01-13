from typing import Optional, List, Any

from transformer.common.attribute_set.metadata_updater.MetadataUpdater import MetadataUpdater
from transformer.common.dto.AttributeMetadata import AttributeMetadata
from transformer.common.enum.MetadataType import MetadataType


class PriceUpdater(MetadataUpdater):

    def __init__(self, metadataType: MetadataType, keepLowest: Optional[bool] = True):
        self.metadataType = metadataType
        self.shouldUpdate = self._keepLowest if keepLowest else self._keepHighest

    def update(self, dictMetadata: List[AttributeMetadata], newMetadata: List[AttributeMetadata]) -> bool:
        if (not dictMetadata and not newMetadata) or not newMetadata:
            return False
        if not dictMetadata:
            return True
        newPrices = [elem for elem in newMetadata if elem.metadataType == self.metadataType]
        if len(newPrices) > 1:
            raise ValueError(f"newMetadata has duplicate {self.metadataType} elements.")
        oldPrices = [elem for elem in dictMetadata if elem.metadataType == self.metadataType]
        if (not oldPrices and not newPrices) or not newPrices:
            return False
        newPrice = newPrices[0].value
        oldPrice = newPrices[0].value
        if newPrice is None:
            raise ValueError(f"newMatadata has a {self.metadataType} element with a null price")
        return self.shouldUpdate(old=oldPrice, new=newPrice)

    def _keepLowest(self, old: Any, new: Any) -> bool:
        return new < old

    def _keepHighest(self, old: Any, new: Any) -> bool:
        return new > old
