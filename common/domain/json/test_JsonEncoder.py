from datetime import datetime
from typing import Dict
from unittest import TestCase
from uuid import UUID

from nose_parameterized import parameterized

from common.domain.dto.AttributeDto import AttributeDto, BodyStyle
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.AttributeType import AttributeType
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from common.domain.json.JsonEncoder import jsonEncoder


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
