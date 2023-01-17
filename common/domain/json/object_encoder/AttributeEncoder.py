import logging
from typing import Dict, Type

from common.domain.dto.AttributeDto import *
from common.domain.enum.AttributeType import AttributeType
from common.domain.json.object_encoder.ObjectEncoder import ObjectEncoder


class AttributeEncoder(ObjectEncoder):
    objectType: Type
    objTypeToAttributeType: Dict[Type, AttributeType]
    jsonEncoder: Optional['JSONEncoder']  # used to translate metadata
    log: logging.Logger

    def __init__(self):
        self.objectType = AttributeDto
        self.objTypeToAttributeType = {
            Engine: AttributeType.ENGINE,
            Transmission: AttributeType.TRANSMISSION,
            Drive: AttributeType.DRIVE,
            BodyStyle: AttributeType.BODY_STYLE,
            Grade: AttributeType.GRADE,
            Package: AttributeType.PACKAGE,
            InteriorColor: AttributeType.INTERIOR_COLOR,
            ExteriorColor: AttributeType.EXTERIOR_COLOR,
            Accessory: AttributeType.ACCESSORY,
            Other: AttributeType.OTHER
        }
        self.jsonEncoder = None
        self.log = logging.getLogger(type(self).__name__)

    def toSerializable(self, attributeDto: AttributeDto) -> Dict:
        try:
            attributeType = self.objTypeToAttributeType[type(attributeDto)]
        except KeyError as e:
            logging.info(f"Unable to match Attribute: {attributeDto} to AttributeType")
            raise ValueError("Unrecognized AttributeDto", e)
        return {"attributeId": attributeDto.attributeId,
                "attributeType": attributeType,
                "title": attributeDto.title,
                "modelId": attributeDto.modelId,
                "attributeMetadata": [self.jsonEncoder.default(meta) for meta in
                                      attributeDto.metadata] if attributeDto.metadata else None,
                "updatedAt": attributeDto.updatedAt
                }
