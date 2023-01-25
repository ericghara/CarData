import logging
from typing import List, Dict
from unittest import TestCase

from parameterized import parameterized

from common.domain.dto.AttributeDto import Drive
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.transform.gm.parser.DriveParser import DriveParser
from transformer.transform.gm.parser.LoggingTools import LoggingTools


class TestDriveParser(TestCase):

    def setUp(self) -> None:
        loggingTools = LoggingTools(logging.getLogger(name=type(self).__name__))
        self.parser = DriveParser(loggingTools=loggingTools)

    @parameterized.expand([({'modelMatrix': {'driveTypes': [{'id': '2WD', 'lowestMSRP': "$30,000"}]}},
                            [Drive(title='2WD', metadata=[
                                AttributeMetadata(metadataType=MetadataType.COMMON_BASE_MSRP, value=30_000,
                                                  unit=MetadataUnit.DOLLARS)])],
                            "All Values present"),
                           ({'modelMatrix': {'driveTypes': [{'id': '2WD', 'lowestMSRP': None}]}},
                            [Drive(title='2WD')],
                            "OK title, 'lowestMSRP' None"),
                           ({'modelMatrix': {'driveTypes': [{'id': '2WD', 'lowestMSRP': ""}]}},
                            [Drive(title='2WD')],
                            "OK title, 'lowestMSRP' Empty"),
                           ({'modelMatrix': {'driveTypes': [{'id': '2WD'}]}},
                            [Drive(title='2WD')],
                            "OK title, 'lowestMSRP' key not present"),
                           ({'modelMatrix': {'driveTypes': [{'id': None}]}},
                            [],
                            "Title is None"),
                           ({'modelMatrix': {'driveTypes': [{}]}},
                            [],
                            "driveDict is empty"),
                           ({'modelMatrix': {}},
                            [],
                            "modelMatrix is empty")
                           ])
    def test_driveParserSingle(self, dataDict: Dict, expectedDrives: List[Drive], testIdentifier: str):
        foundDrives = self.parser.parse(dataDict)
        self.assertEqual(expectedDrives, foundDrives, testIdentifier)
        # Only works for len(drives) <= 1
        for expectedDrive, foundDrive in zip(expectedDrives, foundDrives):
            expectedDrive._assertStrictEq(foundDrive)
