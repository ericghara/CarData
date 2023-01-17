import logging
from unittest import TestCase

from common.domain.dto.AttributeDto import ExteriorColor
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser.ExteriorColorParser import ExteriorColorParser


class TestExteriorColorParser(TestCase):

    def setUp(self) -> None:
        loggingTools = LoggingTools(logging.getLogger())
        self.exteriorColorParser = ExteriorColorParser(loggingTools)

    def test__parseModelSingleColorTitleAndPrice(self):
        modelJson = {"exteriorcolor": [{"title": "Solar Shift", "price": "$0.00"}]}
        foundColors = list(self.exteriorColorParser._parseModel(modelJson))
        expectedColors = [ExteriorColor(title="Solar Shift",
                                        metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_MSRP,
                                                                    value=0, unit=MetadataUnit.DOLLARS)])]
        self.assertEqual(expectedColors, foundColors)
        expectedColors[0]._assertStrictEq(foundColors[0])

    def test__parseModelSingleColorTitleAndNullPrice(self):
        modelJson = {"exteriorcolor": [{"title": "Solar Shift", "price": None}]}
        foundColors = list(self.exteriorColorParser._parseModel(modelJson))
        expectedColors = [ExteriorColor(title="Solar Shift")]
        self.assertEqual(expectedColors, foundColors)
        expectedColors[0]._assertStrictEq(foundColors[0])

    def test__parseModelSingleColorNullTitleAndNullPrice(self):
        modelJson = {"exteriorcolor": [{"title": None, "price": None}]}
        foundColorsIter = self.exteriorColorParser._parseModel(modelJson)
        self.assertRaises(StopIteration, lambda: next(foundColorsIter))

    def test__parseModelMultipleColors(self):
        modelJson = {"exteriorcolor": [{"title": "Solar Shift"},
                                       {"title": "Ice Cap"}]}
        foundColors = set(self.exteriorColorParser._parseModel(modelJson))
        expectedColors = {ExteriorColor(title="Solar Shift"),
                          ExteriorColor(title="Ice Cap")}
        self.assertEqual(expectedColors, foundColors)  # __eq__ used, strict proven by other tests

    def test__parseMultipleModelsDuplicateColors(self):
        jsonData = {"model": [{"exteriorcolor": [{"title": "Solar Shift"}]},
                              {"exteriorcolor": [{"title": "Solar Shift"}]}]}
        foundColors = self.exteriorColorParser.parse(jsonData)
        expectedColors = [ExteriorColor(title="Solar Shift")]
        self.assertEqual(expectedColors, foundColors)
        expectedColors[0]._assertStrictEq(foundColors[0])

    def test__parseMultipleModelsMultipleColors(self):
        jsonData = {"model": [{"exteriorcolor": [{"title": "Solar Shift"}]},
                              {"exteriorcolor": [{"title": "Ice Cap"}]},
                              {}]}
        foundColors = set(self.exteriorColorParser.parse(jsonData))
        expectedColors = {ExteriorColor(title="Solar Shift"),
                          ExteriorColor(title="Ice Cap")}
        self.assertEqual(expectedColors, foundColors)  # __eq__ used, strict proven by other tests

    def test__parseMultipleModelsSameKeepsHighestPrice(self):
        jsonData = {"model": [{"exteriorcolor": [{"title": "Solar Shift", "price" : "$100"}]},
                              {"exteriorcolor": [{"title": "Solar Shift", "price" : "$0.00"}]}
                              ]}
        foundColors = list(self.exteriorColorParser.parse(jsonData))
        expectedColors = [ExteriorColor(title="Solar Shift",
                                        metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_MSRP,
                                                                    value=100, unit=MetadataUnit.DOLLARS)])]
        self.assertEqual(expectedColors, foundColors)
        expectedColors[0]._assertStrictEq(foundColors[0])
