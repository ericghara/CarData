import logging
from typing import Dict, List, Optional
from unittest import TestCase

from parameterized import parameterized

from common.domain.dto.AttributeDto import AttributeDto, InteriorColor, ExteriorColor
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.transform.AttributeParser import AttributeParser
from transformer.transform.gm.parser.LoggingTools import LoggingTools
from transformer.transform.gm.parser.colorParsers import ColorParser, InteriorColorParser, ExteriorColorParser


class TestColorParser(TestCase):
    class DummyAttributeParser(AttributeParser):

        def parse(self, jsonData: Dict) -> List[AttributeDto]:
            return list()

    def setUp(self) -> None:
        loggingTools = LoggingTools(logger=logging.getLogger(type(self).__name__))
        attributeParser = self.DummyAttributeParser()
        self.colorParser = ColorParser(attributeType=InteriorColor, attributeParser=attributeParser,
                                       loggingTools=loggingTools)

    @parameterized.expand([({"msrp": 500, "primaryName": "Awesome Blue"},
                            InteriorColor(title="Awesome Blue",
                                          metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=500,
                                                                      unit=MetadataUnit.DOLLARS)]),
                            "Title and MSRP present"),
                           ({"msrp": None, "primaryName": "Awesome Blue"},
                            InteriorColor(title="Awesome Blue"),
                            "Title present and MSRP is null"),
                           ({"msrp": "abcdef", "primaryName": "Awesome Blue"},
                            InteriorColor(title="Awesome Blue"),
                            "Title present and MSRP is non-digit string"),
                           ({"primaryName": "Awesome Blue"}, InteriorColor(title="Awesome Blue"),
                            "Title present and MSRP key absent"),
                           ({"primaryName": None}, None, "Title None and MSRP key absent"),
                           ({}, None, "empty colorDict")
                           ])
    def test__parseColor(self, colorDict: Dict, expectedColor: Optional[InteriorColor], testIdentifier: str):
        foundColor = self.colorParser._parseColor(colorDict=colorDict, modelIdentifier="Test")
        self.assertEqual(expectedColor, foundColor)
        if expectedColor:
            expectedColor._assertStrictEq(foundColor)

    @parameterized.expand([
        ([{"items": [{"primaryName": "Awesome Blue"}]}], [InteriorColor(title="Awesome Blue")],
         "Single Category, Single Item"),
        ([{"items": [{"primaryName": "Awesome Blue"}, {"primaryName": "Rebellious Red"}]}],
         [InteriorColor(title="Awesome Blue"), InteriorColor(title="Rebellious Red")],
         "Single Category, Multiple Items"),
        ([{"items": [{"primaryName": "Awesome Blue"}]},
          {"items": [{"primaryName": "Rebellious Red"}]}],
         [InteriorColor(title="Awesome Blue"), InteriorColor(title="Rebellious Red")],
         "Multiple Categories, Single item in each"),
        ([{"items": []}], [], "Single Category, No Items"),
        ([{"items": None}], [], "Single Category, null items"),
        ([{}], [], "Single Category, empty itemsDict"),
        ([], [], "No categories")
    ])
    def test_getColors(self, categoryDicts: List[Dict], expectedColors: Optional[List[InteriorColor]],
                       testIdentifier: str):
        foundColors = self.colorParser.getColors(categoryDicts=categoryDicts, modelIdentifier="Test")
        self.assertEqual(expectedColors, foundColors, testIdentifier)
        colorsByTitleFn = lambda colorList: {color.title: color for color in colorList}
        expectedColorsByTitle = colorsByTitleFn(expectedColors)
        foundColorsByTitle = colorsByTitleFn(foundColors)
        for title, expectedColor in expectedColorsByTitle.items():
            foundColor = foundColorsByTitle.get(title, None)
            expectedColor._assertStrictEq(foundColor)


class TestInteriorColorParser(TestCase):

    def setUp(self) -> None:
        loggingTools = LoggingTools(logger=logging.getLogger(type(self).__name__))
        self.parser = InteriorColorParser(loggingTools=loggingTools)

    @parameterized.expand([
        ({"config":
              {"OPTIONS":
                   {"COLOR":
                        {"interior":
                             [{"items":
                                   [{"primaryName": "Jet Black/Graystone Leather"}]}]}}}},
         [InteriorColor(title="Jet Black/Graystone Leather")], "Interior color present"),
        ({"config":
              {"OPTIONS":
                   {"COLOR":
                        {"interior":
                             None}}}},
         [], "Interior is null"),
        ({"config":
              {"OPTIONS":
                   {"COLOR":
                        {}
                    }}},
         [], "Interior key is not present")
    ])
    def test_parse(self, dataDict: Dict, expectedColors: List[InteriorColor], testIdentifier: str):
        foundColors = self.parser.parse(dataDict=dataDict)
        self.assertEqual(expectedColors, foundColors, testIdentifier)
        colorsByTitleFn = lambda colorList: {color.title: color for color in colorList}
        expectedColorsByTitle = colorsByTitleFn(expectedColors)
        foundColorsByTitle = colorsByTitleFn(foundColors)
        for title, expectedColor in expectedColorsByTitle.items():
            foundColor = foundColorsByTitle.get(title, None)
            expectedColor._assertStrictEq(foundColor)

class TestExteriorColorParser(TestCase):

    def setUp(self) -> None:
        loggingTools = LoggingTools(logger=logging.getLogger(type(self).__name__))
        self.parser = ExteriorColorParser(loggingTools=loggingTools)

    @parameterized.expand([
        ({"config":
              {"OPTIONS":
                   {"COLOR":
                        {"exterior":
                             [{"items":
                                   [{"primaryName": "Awesome Blue"}]}]}}}},
         [ExteriorColor(title="Awesome Blue")], "Exterior color present"),
        ({"config":
              {"OPTIONS":
                   {"COLOR":
                        {"exterior":
                             None}}}},
         [], "Exterior is null"),
        ({"config":
              {"OPTIONS":
                   {"COLOR":
                        {}
                    }}},
         [], "Exterior key is not present")
    ])
    def test_parse(self, dataDict: Dict, expectedColors: List[ExteriorColor], testIdentifier: str):
        foundColors = self.parser.parse(dataDict=dataDict)
        self.assertEqual(expectedColors, foundColors, testIdentifier)
        colorsByTitleFn = lambda colorList: {color.title: color for color in colorList}
        expectedColorsByTitle = colorsByTitleFn(expectedColors)
        foundColorsByTitle = colorsByTitleFn(foundColors)
        for title, expectedColor in expectedColorsByTitle.items():
            foundColor = foundColorsByTitle.get(title, None)
            expectedColor._assertStrictEq(foundColor)