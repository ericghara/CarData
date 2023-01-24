import logging
from typing import Dict, Optional, List
from unittest import TestCase

from nose_parameterized import parameterized

from common.domain.dto.AttributeDto import Transmission
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.transform.gm.parser.LoggingTools import LoggingTools
from transformer.transform.gm.parser.TransmissionParser import TransmissionParser


class TestTransmissionParser(TestCase):

    def setUp(self) -> None:
        loggingTools = LoggingTools(logging.getLogger(type(self).__name__))
        self.parser = TransmissionParser(loggingTools=loggingTools)

    @parameterized.expand([
        ({'primaryName': "10 Speed Automatic", 'msrp': 2_000}, Transmission(title="10 Speed Automatic", metadata=[
            AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=2_000, unit=MetadataUnit.DOLLARS)]),
         "Title and price present"),
        ({'primaryName': "10 Speed Automatic", 'msrp': None}, Transmission(title="10 Speed Automatic"),
         "Title present, price null"),
        ({'primaryName': "10 Speed Automatic", 'msrp': "adfadfsa"}, Transmission(title="10 Speed Automatic"),
         "Title present, price incorrect format"),
        ({'primaryName': "10 Speed Automatic"}, Transmission(title="10 Speed Automatic"),
         "Title present, no price key"),
        ({'primaryName': None}, None, "Title null"),
        ({}, None, "Empty transmissionDict")
    ])
    def test__parseTransmission(self, transmissionDict: Dict, expectedTransmission: Optional[Transmission],
                                testIdentifier: str):
        foundTransmission = self.parser._parseTransmission(transmissionDict=transmissionDict, modelIdentifier="test")
        self.assertEqual(expectedTransmission, foundTransmission, testIdentifier)
        if expectedTransmission:
            expectedTransmission._assertStrictEq(foundTransmission)

    @parameterized.expand([
        ({"modelMatrix": {"transmission": [{"primaryName": "10 Speed Automatic"}]}},
         [Transmission(title="10 Speed Automatic")], "single transmission"),
        ({"modelMatrix": {"transmission":
                              [{"primaryName": "10 Speed Automatic"},
                               {"primaryName": "6 Speed Manual"}]}},
         [Transmission(title="10 Speed Automatic"), Transmission(title="6 Speed Manual")], "two transmissions"),
        ({"modelMatrix": {"transmission": None}}, [], "PACKAGES is null"),
        ({}, [], "Empty dataDict")
    ])
    def test_Parser(self, dataDict: Dict, expectedTransmissions: List[Transmission], testIdentifier: str):
        foundTransmissions = self.parser.parse(dataDict)
        self.assertEqual(expectedTransmissions, foundTransmissions, testIdentifier)
        transmissionByTitleFn = lambda transmissions: {transmission.title: transmission for transmission in
                                                       transmissions}
        expectedTransmissionsByTitle = transmissionByTitleFn(expectedTransmissions)
        foundTransmissionsByTitle = transmissionByTitleFn(foundTransmissions)
        for title, expectedTransmission in expectedTransmissionsByTitle.items():
            foundTransmission = foundTransmissionsByTitle.get(title)
            expectedTransmission._assertStrictEq(foundTransmission)
