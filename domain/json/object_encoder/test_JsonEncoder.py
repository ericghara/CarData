from datetime import datetime
from typing import Dict
from unittest import TestCase
from uuid import UUID

from nose_parameterized import parameterized

from domain.json.JsonEncoder import jsonEncoder
from repository.AttributeType import AttributeType
from transformer.common.dto.AttributeDto import AttributeDto, BodyStyle
from transformer.common.dto.AttributeMetadata import AttributeMetadata
from transformer.common.enum.MetadataType import MetadataType
from transformer.common.enum.MetadataUnit import MetadataUnit


class TestJsonEncoder(TestCase):

    def setUp(self):
        self.encoder = jsonEncoder

    @parameterized.expand(
        [(AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value="Test", unit=MetadataUnit.DOLLARS),
          {"metadataType": "COMMON_MSRP", "value": "Test", "unit": "DOLLARS"}),
         (AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value="Test"),
          {"metadataType": "COMMON_MSRP", "value": "Test", "unit": None})])
    def test_defaultConversionOfAttributeMetadata(self, attributeMetadata: AttributeMetadata, expected: Dict):
        foundDict = self.encoder.default(attributeMetadata)
        self.assertEqual(expected, foundDict)

    @parameterized.expand(
        [(BodyStyle(title="Standard",
                    metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value="Test")]),
          {"attributeId": None, "attributeType": AttributeType.BODY_STYLE, "title": "Standard", "modelId": None,
           "attributeMetadata": [{"metadataType": "COMMON_MSRP", "value": "Test", "unit": None}], "updatedAt": None}),

         (BodyStyle(title="Standard",
                    attributeId=UUID("00000000-0000-0000-0000-000000000000"),
                    modelId=UUID("11111111-1111-1111-1111-111111111111"),
                    metadata=None,
                    updatedAt=datetime.fromtimestamp(30256871)),
          {"attributeId": UUID("00000000-0000-0000-0000-000000000000"), "attributeType": AttributeType.BODY_STYLE,
           "title": "Standard", "modelId": UUID("11111111-1111-1111-1111-111111111111"),
           "attributeMetadata": None, "updatedAt": datetime.fromtimestamp(30256871)})
         ])
    def test_defaultConversionOfAttributeDto(self, attributeDto: AttributeDto, expected: Dict):
        foundDict = self.encoder.default(attributeDto)
        self.assertEqual(expected, foundDict)
