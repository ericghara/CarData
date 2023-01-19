import logging
from unittest import TestCase

from common.domain.dto.AttributeDto import Transmission
from transformer.transform.toyota.LoggingTools import LoggingTools
from transformer.transform.toyota.parser.TransmissionParser import TransmissionParser


class MyTestCase(TestCase):

    def setUp(self):
        self.loggingTools = LoggingTools(logging.getLogger())
        self.transmissionParser = TransmissionParser(self.loggingTools)

    def test_getTitleWhenTitleExists(self):
        model = {"transmission": {"title": "6MT"}}
        expected = "6MT"
        found = self.transmissionParser._getTitle(model)
        self.assertEqual(expected, found)

    def test_getTitleWhenTitleNotExists(self):
        model = {"transmission" : {} }
        expected = self.transmissionParser._getTitle(model)
        self.assertIsNone(expected)

    def test_parse(self):
        jsonData = {"model" : [{"transmission": {"title": "6MT"} }, {"transmission" : {} } ]}
        foundTransmissions = self.transmissionParser.parse(jsonData)
        expectedTransmissions = [Transmission(title="6MT")]
        self.assertEqual(expectedTransmissions, foundTransmissions)
        # __eq__ for AttributeDto does not compare metadata
        expectedTransmissions[0]._assertStrictEq(foundTransmissions[0])







