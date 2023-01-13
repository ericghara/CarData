from typing import Any, Optional

from transformer.common.enum.MetadataType import MetadataType
from transformer.common.enum.MetadataUnit import MetadataUnit


class AttributeMetadata:

    def __init__(self, metadataType: MetadataType, value: Any, unit: Optional[MetadataUnit] = None):
        self.metadataType = metadataType
        self.value = value
        self.unit = unit

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash((self.metadataType, self.value, self.unit))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.metadataType}, {self.value}, {self.unit})"
