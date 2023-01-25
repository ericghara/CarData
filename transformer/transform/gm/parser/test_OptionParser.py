import logging
from typing import Optional, Dict
from unittest import TestCase

from parameterized import parameterized

from common.domain.dto.AttributeDto import Option
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.transform.gm.parser.LoggingTools import LoggingTools
from transformer.transform.gm.parser.OptionParser import OptionParser


class TestOptionParser(TestCase):

    def setUp(self) -> None:
        loggingTools = LoggingTools(logging.getLogger(name=type(self).__name__))
        self.parser = OptionParser(loggingTools=loggingTools)

    @parameterized.expand([("exterior", "Exterior", "one part name"),
                           ("exterior.wheels", "Exterior - Wheels", "two part name"),
                           (None, "Miscellaneous", "null categoryId")
                           ])
    def test__createCategoryName(self, categoryId: Optional[str], expectedName: str, testIdentifier: str):
        foundName = self.parser._createCategoryName(categoryId)
        self.assertEqual(expectedName, foundName, testIdentifier)

    @parameterized.expand([
        ({"description": "Wheel Locks", "msrp": 95}, Option(title="Wheel Locks", metadata=[
            AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=95, unit=MetadataUnit.DOLLARS),
            AttributeMetadata(metadataType=MetadataType.COMMON_CATEGORY, value="Test")]),
         "Title and price present"),
        ({"description": "Wheel Locks", "msrp": None}, Option(title="Wheel Locks", metadata=[
            AttributeMetadata(metadataType=MetadataType.COMMON_CATEGORY, value="Test")]),
         "Title present, price null"),
        ({"description": "Wheel Locks"}, Option(title="Wheel Locks", metadata=[
            AttributeMetadata(metadataType=MetadataType.COMMON_CATEGORY, value="Test")]),
         "Title present, price no key"),
        ({"description": None}, None, "Title null, price no key"),
        ({}, None, "Empty Option Dict")
    ])
    def test__parseOptionDict(self, optionDict: Dict, expectedOption: Optional[Option], testIdentifier: str):
        categoryName, modelIdentifier = "Test", "Test-Model"
        foundOption = self.parser._parseOptionDict(optionDict=optionDict, categoryName=categoryName,
                                                   modelIdentifier=modelIdentifier)
        self.assertEqual(expectedOption, foundOption, testIdentifier)
        if expectedOption:
            expectedOption._assertStrictEq(foundOption)

    def test_parseEmptyDataDict(self):
        foundOptions = self.parser.parse({})
        self.assertEqual(list(), foundOptions)

    def test_parseOptionsKeyNull(self):
        dataDict = {"config": {"OPTIONS": None}}
        foundOptions = self.parser.parse(dataDict)
        self.assertEqual(list(), foundOptions)

    def test__parseMultipleCategoriesAndOptions(self):
        dataDict = {"config":
                        {"OPTIONS":
                             {"EXTERIOR":
                                  {"exterior.wheels":
                                       [{"description": "5 Spoke"}],
                                   "exterior.options":
                                       [{"description": "Wheel Locks"},
                                        {"description": "Power Sunroof"}]
                                   },
                              "INTERIOR":
                                  {"interior.radio":
                                       [{"description": "Infotainment"},
                                        {"No Parsable data": True}]},
                              }}}
        expectedOptions = [
            Option(title="5 Spoke", metadata=[
                AttributeMetadata(metadataType=MetadataType.COMMON_CATEGORY, value="Exterior - Wheels")]),
            Option(title="Wheel Locks", metadata=[
                AttributeMetadata(metadataType=MetadataType.COMMON_CATEGORY, value="Exterior - Options")]),
            Option(title="Power Sunroof", metadata=[
                AttributeMetadata(metadataType=MetadataType.COMMON_CATEGORY, value="Exterior - Options")]),
            Option(title="Infotainment", metadata=[
                AttributeMetadata(metadataType=MetadataType.COMMON_CATEGORY, value="Interior - Radio")
            ])]
        foundOptions = self.parser.parse(dataDict)
        self.assertEqual(expectedOptions, foundOptions, "loose equality")
        optionsByTitle = lambda options: {option.title: option for option in options}
        expectedOptionsByTitle = optionsByTitle(expectedOptions)
        foundOptionsByTitle = optionsByTitle(foundOptions)
        for title, expectedOption in expectedOptionsByTitle.items():
            foundOption = foundOptionsByTitle.get(title)
            expectedOption._assertStrictEq(foundOption)
