import logging
from unittest import TestCase

from transformer.attribute_dto.AttributeDto import InteriorColor
from transformer.attribute_metadata.AttributeMetadata import AttributeMetadata
from transformer.attribute_metadata.MetadataType import MetadataType
from transformer.attribute_metadata.MetadataUnit import MetadataUnit
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

    def test__parseMultipleModelsDuplicateColors(self):
        jsonData = {"model": [{"interiorcolor": [{"title": "Black Ultrasuede"}]},
                              {"interiorcolor": [{"title": "Black Ultrasuede"}]}]}
        foundColors = self.interiorColorParser.parse(jsonData)
        expectedColors = [InteriorColor(title="Black Ultrasuede")]
        self.assertEqual(expectedColors, foundColors)
        expectedColors[0]._assertStrictEq(foundColors[0])

    def test__parseMultipleModelsMultipleColors(self):
        jsonData = {"model": [{"interiorcolor": [{"title": "Black Ultrasuede"}]},
                              {"interiorcolor": [{"title": "Genuine White Rhino Leather"}]},
                              {}]}
        foundColors = set(self.interiorColorParser.parse(jsonData))
        expectedColors = {InteriorColor(title="Black Ultrasuede"),
                          InteriorColor(title="Genuine White Rhino Leather")}
        self.assertEqual(expectedColors, foundColors)  # __eq__ used, strict proven by other tests
