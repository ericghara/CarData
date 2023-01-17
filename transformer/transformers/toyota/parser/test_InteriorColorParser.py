import logging
from unittest import TestCase

from common.domain.dto.AttributeDto import InteriorColor
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser.InteriorColorParser import InteriorColorParser


class TestInteriorColorParser(TestCase):

    def setUp(self) -> None:
        loggingTools = LoggingTools(logging.getLogger())
        self.interiorColorParser = InteriorColorParser(loggingTools)

    def test__parseModelSingleColorTitleAndPrice(self):
        modelJson = {"interiorcolor": [{"title": "Black Ultrasuede", "price": "$0.00"}]}
        foundColors = list(self.interiorColorParser._parseModel(modelJson))
        expectedColors = [InteriorColor(title="Black Ultrasuede",
                                        metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_MSRP,
                                                                    value=0, unit=MetadataUnit.DOLLARS)])]
        self.assertEqual(expectedColors, foundColors)
        expectedColors[0]._assertStrictEq(foundColors[0])

    def test__parseModelSingleColorTitleAndNullPrice(self):
        modelJson = {"interiorcolor": [{"title": "Black Ultrasuede", "price": None}]}
        foundColors = list(self.interiorColorParser._parseModel(modelJson))
        expectedColors = [InteriorColor(title="Black Ultrasuede")]
        self.assertEqual(expectedColors, foundColors)
        expectedColors[0]._assertStrictEq(foundColors[0])

    def test__parseModelSingleColorNullTitleAndNullPrice(self):
        modelJson = {"interiorcolor": [{"title": None, "price": None}]}
        foundColorsIter = self.interiorColorParser._parseModel(modelJson)
        self.assertRaises(StopIteration, lambda: next(foundColorsIter))

    def test__parseModelMultipleColors(self):
        modelJson = {"interiorcolor": [{"title": "Black Ultrasuede"},
                                       {"title": "Genuine White Rhino Leather"}]}
        foundColors = set(self.interiorColorParser._parseModel(modelJson))
        expectedColors = {InteriorColor(title="Black Ultrasuede"),
                          InteriorColor(title="Genuine White Rhino Leather")}
        self.assertEqual(expectedColors, foundColors)  # __eq__ used, strict proven by other tests

    def test_parseMultipleModelsDuplicateColors(self):
        jsonData = {"model": [{"interiorcolor": [{"title": "Black Ultrasuede"}]},
                              {"interiorcolor": [{"title": "Black Ultrasuede"}]}]}
        foundColors = self.interiorColorParser.parse(jsonData)
        expectedColors = [InteriorColor(title="Black Ultrasuede")]
        self.assertEqual(expectedColors, foundColors)
        expectedColors[0]._assertStrictEq(foundColors[0])

    def test_parseMultipleModelsMultipleColors(self):
        jsonData = {"model": [{"interiorcolor": [{"title": "Black Ultrasuede"}]},
                              {"interiorcolor": [{"title": "Genuine White Rhino Leather"}]},
                              {}]}
        foundColors = set(self.interiorColorParser.parse(jsonData))
        expectedColors = {InteriorColor(title="Black Ultrasuede"),
                          InteriorColor(title="Genuine White Rhino Leather")}
        self.assertEqual(expectedColors, foundColors)  # __eq__ used, strict proven by other tests
        
    def test_parseMultipleModelsSameKeepsHighestPrice(self):
        jsonData = {"model": [{"interiorcolor": [{"title": "Black Ultrasuede", "price" : "$100"}]},
                              {"interiorcolor": [{"title": "Black Ultrasuede", "price" : "$0.00"}]}
                              ]}
        foundColors = list(self.interiorColorParser.parse(jsonData))
        expectedColors = [InteriorColor(title="Black Ultrasuede",
                                        metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_MSRP,
                                                                    value=100, unit=MetadataUnit.DOLLARS)])]
        self.assertEqual(expectedColors, foundColors)
        expectedColors[0]._assertStrictEq(foundColors[0])
