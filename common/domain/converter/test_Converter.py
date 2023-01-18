from datetime import datetime
from typing import Any, Type
from unittest import TestCase
from uuid import UUID

from parameterized import parameterized

from common.domain.converter.Converter import converter
from common.domain.dto.AttributeDto import Grade, Transmission, AttributeDto
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.AttributeType import AttributeType
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from common.exception.IllegalStateError import IllegalStateError
from common.repository.Entities import ModelAttribute


class TestConverter(TestCase):

    @parameterized.expand([(ModelAttribute(attribute_id=UUID('00000000-0000-0000-0000-000000000000'),
                                           attribute_type=AttributeType.TRANSMISSION, title='test',
                                           model_id=UUID('11111111-1111-1111-1111-111111111111'),
                                           attribute_metadata=None,
                                           updated_at=datetime.fromtimestamp(800025)),
                            Transmission(title="test", attributeId=UUID('00000000-0000-0000-0000-000000000000'),
                                         modelId=UUID('11111111-1111-1111-1111-111111111111'), metadata=None,
                                         updatedAt=datetime.fromtimestamp(800025))),
                           # Testcase with metadata
                           (ModelAttribute(title="title", attribute_type=AttributeType.GRADE, attribute_metadata=[
                               {"metadataType": "COMMON_MSRP", "value": "Test", "unit": "DOLLARS"}]),
                            Grade(title="title", metadata=[
                                AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value="Test",
                                                  unit=MetadataUnit.DOLLARS)]))
                           ])
    def test_convertModelAttributeToModelDto(self, modelAttribute: ModelAttribute, expected: AttributeDto):
        found = converter.convert(modelAttribute, AttributeDto)
        expected._assertStrictEq(found)

    @parameterized.expand([(Transmission(title="test", attributeId=UUID('00000000-0000-0000-0000-000000000000'),
                                         modelId=UUID('11111111-1111-1111-1111-111111111111'), metadata=None,
                                         updatedAt=datetime.fromtimestamp(800025)),
                            ModelAttribute(attribute_id=UUID('00000000-0000-0000-0000-000000000000'),
                                           attribute_type=AttributeType.TRANSMISSION, title='test',
                                           model_id=UUID('11111111-1111-1111-1111-111111111111'),
                                           attribute_metadata=None,
                                           updated_at=datetime.fromtimestamp(800025))
                            ),
                           # Testcase with metadata
                           (Grade(title="title", metadata=[
                               AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value="Test",
                                                 unit=MetadataUnit.DOLLARS)]),
                            ModelAttribute(attribute_id=None, attribute_type=AttributeType.GRADE, title="title",
                                           model_id=None,
                                           attribute_metadata=[
                                               {"metadataType": "COMMON_MSRP", "value": "Test", "unit": "DOLLARS"}],
                                           updated_at=None))
                           ])
    def test_convertAttributeDtoToModelAttribute(self, attributeDto: AttributeDto, expected: ModelAttribute):
        stripPrivate = lambda modelAttribute: {key: value for key, value in modelAttribute.__dict__.items() if
                                               not key.startswith("_")}
        found = converter.convert(attributeDto, ModelAttribute)
        self.assertEqual(stripPrivate(expected), stripPrivate(found))

    @parameterized.expand([("test", int),
                           (Grade(title="title"), int)])
    def test_ConvertRaisesOnUnknownTypeConversion(self, obj: Any, outputType: Type):
        self.assertRaises(IllegalStateError, lambda: converter.convert(obj=obj, outputType=outputType))


