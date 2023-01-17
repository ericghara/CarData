from typing import Any, Type, Dict, Optional

from domain.json.object_encoder.ObjectEncoder import ObjectEncoder
from repository.AttributeType import AttributeType
from transformer.common.dto.AttributeMetadata import AttributeMetadata


class AttributeMetadataEncoder(ObjectEncoder):
    objectType: Type
    objTypeToAttributeType: Dict[Type, AttributeType]
    jsonEncoder: Optional['JSONEncoder']  # used to translate metadata

    def __init__(self):
        self.objectType = AttributeMetadata

    def toSerializable(self, object: AttributeMetadata) -> Any:
        return {'metadataType': object.metadataType.name,
                'value': object.value,
                'unit': object.unit.name if object.unit else None}

