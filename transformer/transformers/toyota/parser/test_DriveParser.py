import logging
from unittest import TestCase

from transformer.common.attribute_dto import Drive
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser.DriveParser import DriveParser


class TestDriveParser(TestCase):

    def setUp(self) -> None:
        self.loggingTools = LoggingTools(logging.getLogger())
        self.driveParser = DriveParser(self.loggingTools)

    def test_getDriveHasTitle(self):
        modelJson = {"drive": {"title": "Rear-Wheel Drive"}}
        foundDrive = self.driveParser._getDrive(modelJson)
        expectedDrive = Drive(title="Rear-Wheel Drive")
        expectedDrive._assertStrictEq(foundDrive)

    def test_getDriveNoTitle(self):
        modelJson = {"drive": {"title": None}}
        foundDrive = self.driveParser._getDrive(modelJson)
        self.assertIsNone(foundDrive)

    def test_parse(self):
        jsonData = {"model": [{"drive": {"title": "4x2"}},
                              {"drive": {"title": "4x2"}},
                              {"drive": {"title": "4x4"}},
                              {"drive": {}}]}
        foundDriveDtos = self.driveParser.parse(jsonData)
        self.assertEqual(2, len(foundDriveDtos))
        expectedDriveDtosByTitle = {driveDto.title: driveDto for driveDto in
                                    (Drive(title="4x2"), Drive(title="4x4"))}
        for foundDriveDto in foundDriveDtos:
            foundDriveDto._assertStrictEq(expectedDriveDtosByTitle.get(foundDriveDto.title))
