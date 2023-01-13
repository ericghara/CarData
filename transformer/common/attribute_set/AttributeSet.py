from abc import ABC, abstractmethod
from typing import Optional, List, Any, Iterator

from transformer.common.dto.AttributeDto import AttributeDto
from transformer.common.dto.AttributeMetadata import AttributeMetadata
from transformer.common.enum.MetadataType import MetadataType


class MetadataUpdater(ABC):

    @abstractmethod
    def update(self, dictMetadta: List[AttributeMetadata], newMetadata: List[AttributeMetadata]) -> bool:
        """
        Return true if metadata should be updated to newMetadata, false if no update should be made (dict remains
        in current state)
        :param dictMetadta:
        :param newMetadata:
        :return:
        """
        pass

class AttributeSet:
    """
    ``AttributeSet`` is data structure that abstracts handling conflicts between ``AttributeDto``s.
    ``AttributeDto``'s have metadata which is not considered in the implementation of its ``__eq__`` and ``__hash__``.
    AttributeSet is a set implementation that considers this metadata and determines whether to update the metadata
    on an (otherwise identical) AttributeDto conflict.  The ``updater`` implements the ``MetadataUpdater``
    *functional interface* (in Java terms) which determines how conflicts should be resolved.
    """

    def __init__(self, updater: MetadataUpdater):
        self.elements = dict()
        self.updater = updater

    def add(self, element: AttributeDto) -> bool:
        newAttribute = element
        newMetadata = element.metadata
        newAttribute.metadata = None
        if newAttribute not in self.elements:
            self.elements[newAttribute] = newMetadata
            return True
        oldMetadata = self.elements[newAttribute]
        if self.updater.update(dictMetadta=oldMetadata, newMetadata=newMetadata):
            self.elements[newAttribute] = newMetadata
            return True
        return False

    def getMetadata(self, attribute: AttributeDto) -> Optional[List[AttributeMetadata]]:
        if attribute not in self.elements:
            raise KeyError(f"Attribute {attribute} not found")
        return self.elements[attribute]

    def __iter__(self) -> Iterator[AttributeDto]:
        return iter([AttributeDto(attributeType=attribute.attributeType, title=attribute.title, metadata=metadata) for
                     attribute, metadata in self.elements.items()])


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
