from typing import Optional, List, Any

from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from transformer.domain.attribute_set.metadata_updater.MetadataUpdater import MetadataUpdater


class PriceUpdater(MetadataUpdater):

    def __init__(self, metadataType: MetadataType, keepLowest: Optional[bool] = True):
        self.metadataType = metadataType
        self.shouldUpdate = self._keepLowest if keepLowest else self._keepHighest

    def update(self, dictMetadata: Optional[List[AttributeMetadata]], newMetadata: Optional[List[AttributeMetadata]]) -> bool:
        if (not dictMetadata and not newMetadata) or not newMetadata: # handle null newMetadata
            return False
        newPrices = [elem for elem in newMetadata if elem.metadataType == self.metadataType]
        # validate newPrices
        if len(newPrices) > 1:
            raise ValueError(f"newMetadata has duplicate {self.metadataType} elements.")
        if len(newPrices) == 1 and newPrices[0].value is None:
            raise ValueError(f"newMatadata has a {self.metadataType} element with a null price")
        if not dictMetadata: # null dict metadata valid newMetadata (and newPrices)
            return True
        oldPrices = [elem for elem in dictMetadata if elem.metadataType == self.metadataType]
        if (not oldPrices and not newPrices) or not newPrices: # handle no newPrice
            return False
        if not oldPrices and newPrices: # handle no oldPrice
            return True
        # handle valid & present oldPrice and newPrice
        newPrice = newPrices[0].value
        oldPrice = oldPrices[0].value
        return self.shouldUpdate(old=oldPrice, new=newPrice)

    def _keepLowest(self, old: Any, new: Any) -> bool:
        return new < old

    def _keepHighest(self, old: Any, new: Any) -> bool:
        return new > old
