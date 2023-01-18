import json
from unittest import TestCase

from parameterized import parameterized

from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from common.domain.json.JsonDecoder import jsonDecoder
from common.exception.JsonDecodeError import JsonDecodeError


class TestJsonDecoder(TestCase):

    def setUp(self):
        self.decoder = jsonDecoder

    @parameterized.expand([
        ('{"metadataType": "COMMON_MSRP", "value": "Test", "unit": "DOLLARS"}',
         AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value="Test", unit=MetadataUnit.DOLLARS)),
        ('{"metadataType": "COMMON_MSRP", "value": "Test", "unit": null}',
         AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value="Test"))
    ])
    def test_AttributeMetadataMappingValid(self, rawJson: str, expected: AttributeMetadata):
        mapper = self.decoder.getMappingFunction(AttributeMetadata)
        foundMetadata = json.loads(rawJson, object_hook=mapper)
        self.assertEqual(expected, foundMetadata)

    @parameterized.expand(['{"metadataType": "COMMON_MSRP", "value": "Test", "unit": "FAKE_UNIT"}',
                           '{"metadataType": "FAKE_TYPE", "value": "Test", "unit": null}',
                           '{"metadataType": null, "value": "Test", "unit": null}',
                           '{"value": "Test", "unit": null}'])
    def test_AttributeMetadataMappingRaises(self, rawJson: str):
        mapper = self.decoder.getMappingFunction(AttributeMetadata)
        self.assertRaises(JsonDecodeError, lambda: json.loads(rawJson, object_hook=mapper))

    def test_getMappingFunctionRaisesOnNoMapping(self):
        self.assertRaises(ValueError, lambda: self.decoder.getMappingFunction(str) )
