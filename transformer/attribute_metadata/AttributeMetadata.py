from typing import Any, Optional

from transformer.attribute_metadata.MetadataType import MetadataType


class AttributeMetadata:

    def __init__(self, metadataType: MetadataType, value: Any, units: Optional[str] = None ):
        self.key = metadataType.name
        self.label = metadataType.value
        self.value = value
        self.units = units

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash((self.key, self.label, self.value, self.units))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.key}, {self.label}, {self.value}, {self.units})"
