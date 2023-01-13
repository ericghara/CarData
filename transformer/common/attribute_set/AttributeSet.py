from typing import Optional, List, Iterator

from transformer.common.attribute_set.metadata_updater.MetadataUpdater import MetadataUpdater
from transformer.common.dto.AttributeDto import AttributeDto
from transformer.common.dto.AttributeMetadata import AttributeMetadata


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
        if self.updater.update(dictMetadata=oldMetadata, newMetadata=newMetadata):
            self.elements[newAttribute] = newMetadata
            return True
        return False

    def getMetadata(self, attribute: AttributeDto) -> Optional[List[AttributeMetadata]]:
        if attribute not in self.elements:
            raise KeyError(f"Attribute {attribute} not found")
        return self.elements[attribute]

    def __iter__(self) -> Iterator[AttributeDto]:
        attributeDtos = list()
        for attribute, metadata in self.elements.items():
            mergedParams = {**attribute.__dict__, **{"metadata" : metadata}} if metadata else {**attribute.__dict__}
            attributeDtos.append(attribute.__class__(**mergedParams) )
        return iter(attributeDtos)