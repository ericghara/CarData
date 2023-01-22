import logging
from typing import List, Dict
from unittest import TestCase

from parameterized import parameterized

from common.domain.dto.AttributeDto import BodyStyle
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.transform.gm.parser.BodyStyleParser import BodyStyleParser
from transformer.transform.gm.parser.LoggingTools import LoggingTools


class TestBodyStyleParser(TestCase):

    def setUp(self) -> None:
        loggingTools = LoggingTools(logging.getLogger(name=type(self).__name__))
        self.parser = BodyStyleParser(loggingTools=loggingTools)

    @parameterized.expand([
        (
                {"modelMatrix": {"bodyTypes": [{"formattedConfig": "Body", "lowestMSRPValue": 30_000}]}},
                [BodyStyle(title="Body", metadata=[
                    AttributeMetadata(metadataType=MetadataType.COMMON_BASE_MSRP, value=30_000,
                                      unit=MetadataUnit.DOLLARS)])],
                "All Values present"
        ),
        (
                {"modelMatrix": {"bodyTypes": [{"formattedConfig": "Body", "lowestMSRPValue": None}]}},
                [BodyStyle(title="Body")],
                "MSRP null"
        ),
        (
                {"modelMatrix": {"bodyTypes": [{"formattedConfig": "Body", "lowestMSRPValue": "$100"}]}},
                [BodyStyle(title="Body")],
                "MSRP not a number"
        ),
        (
                {"modelMatrix": {"bodyTypes": [{"formattedConfig": "Body"}]}},
                [BodyStyle(title="Body")],
                "no msrp Key"
        ),
        (
                {"modelMatrix": {"bodyTypes": [{"formattedConfig": None, "lowestMSRPValue": None}]}},
                [BodyStyle(title="Standard")],
                "Title null"
        ),
        (
                {"modelMatrix": {"bodyTypes": [{}]}},
                [BodyStyle(title="Standard")],
                "title no Key"
        ),
        (
                {},
                [BodyStyle(title="Standard")],
                "Empty dataDict"
        )
    ])
    def test_parse(self, dataDict: Dict, expectedBodyStyles: List[BodyStyle], testIdentifier: str):
        foundBodyStyles = self.parser.parse(dataDict)
        self.assertEqual(expectedBodyStyles, foundBodyStyles, testIdentifier)
        # Only works for len(bodyStyles) <= 1
        for expectedBodyStyle, foundBodyStyle in zip(expectedBodyStyles, foundBodyStyles):
            expectedBodyStyle._assertStrictEq(foundBodyStyle)
