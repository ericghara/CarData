from typing import Any, Type, Dict, Optional

from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.AttributeType import AttributeType
from common.domain.json.object_encoder.ObjectEncoder import ObjectEncoder


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

