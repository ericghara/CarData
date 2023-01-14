import logging
from typing import Optional
from unittest import TestCase

from parameterized import parameterized

from transformer.common.dto.AttributeMetadata import AttributeMetadata
from transformer.common.dto.AttributeDto import BodyStyle
from transformer.common.enum.MetadataType import MetadataType
from transformer.common.enum.MetadataUnit import MetadataUnit
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser.BodyStyleParser import BodyStyleParser


class TestBodyStyleParser(TestCase):

    def setUp(self) -> None:
        loggingTools = LoggingTools(logging.getLogger())
        self.bodyStyleParser = BodyStyleParser(loggingTools)

    def test__parseModelAllAttributes(self):
        modelAllAttributes = {
            'bed': {'title': "5-ft. Bed"},
            'cab': {'title': "Double Cab"},
            'attributes':
                {"seating": {"value": "5"},
                 "msrp": {"value": "$47,185"}
                 }
        }
        foundBodyStyle = self.bodyStyleParser._parseModel(modelAllAttributes)
        expectedBodyStyle = BodyStyle(title="Double Cab 5-ft. Bed", metadata=[
            AttributeMetadata(metadataType=MetadataType.BODY_STYLE_BED, value="5-ft. Bed"),
            AttributeMetadata(metadataType=MetadataType.BODY_STYLE_CAB, value="Double Cab"),
            AttributeMetadata(metadataType=MetadataType.BODY_STYLE_SEATING, value=5, unit=MetadataUnit.PASSENGERS),
            AttributeMetadata(metadataType=MetadataType.COMMON_BASE_MSRP, value=47_185, unit=MetadataUnit.DOLLARS)
        ])
        expectedBodyStyle._assertStrictEq(foundBodyStyle)

    def test__parseModelNullAttributes(self):
        modelNullAttributes = {
            'bed': {'title': None},
            'cab': {'title': None},
            'attributes':
                {"seating": {"value": None},
                 "msrp": {"value": None}
                 }
        }
        foundBodyStyle = self.bodyStyleParser._parseModel(modelNullAttributes)
        expectedBodyStyle = BodyStyle(title="Standard")
        expectedBodyStyle._assertStrictEq(foundBodyStyle)

    def test__parseEmptyModel(self):
        emptyModel = {
        }
        foundBodyStyle = self.bodyStyleParser._parseModel(emptyModel)
        expectedBodyStyle = BodyStyle(title="Standard")
        expectedBodyStyle._assertStrictEq(foundBodyStyle)

    @parameterized.expand([("Cab", "Bed", "Cab Bed"),
                           ("Cab", None, "Cab"),
                           ("Bed", None, "Bed"),
                           (None, None, "Standard")])
    def test__createTitle(self, cabVal: Optional[str], bedVal: Optional[str], expectedTitle: str):
        modelDynamicAttributes = {
            'bed': {'title': bedVal},
            'cab': {'title': cabVal}
        }
        foundTitle = self.bodyStyleParser._parseModel(modelDynamicAttributes)
        expectedTitle = BodyStyle(title=expectedTitle)
        # can use __eq__ here b/c we are not testing AttributeMetadata (that's for other tests)
        self.assertEqual(expectedTitle, foundTitle)

    def test__parseIgnoresEmptyModelData(self):
        jsonData = {"model": [
            {
                'bed': {'title': "5-ft. Bed"},
                'cab': {'title': "Double Cab"},
                'attributes':
                    {"seating": {"value": "5"},
                     "msrp": {"value": "$47,185"}
                     }
            },
            {}
        ]}
        foundBodyStyles = self.bodyStyleParser.parse(jsonData)
        expectedBodyStyles = [BodyStyle(title="Double Cab 5-ft. Bed", metadata=[
            AttributeMetadata(metadataType=MetadataType.BODY_STYLE_BED, value="5-ft. Bed"),
            AttributeMetadata(metadataType=MetadataType.BODY_STYLE_CAB, value="Double Cab"),
            AttributeMetadata(metadataType=MetadataType.BODY_STYLE_SEATING, value=5, unit=MetadataUnit.PASSENGERS),
            AttributeMetadata(metadataType=MetadataType.COMMON_BASE_MSRP, value=47_185, unit=MetadataUnit.DOLLARS)
        ]),
                              BodyStyle(title="Standard")]
        self.assertEqual(set(expectedBodyStyles),
                         set(foundBodyStyles))  # non-strict equality, AttributeMetadata tested elsewhere

    def test__parseKeepsLowestPriceOnDuplicate(self):
        jsonData = {"model": [
            {'attributes': {"msrp": {"value": "$47,185"}}},
            {'attributes': {"msrp": {"value": "$46,900"}}}
        ]}
        foundBodyStyles = list(self.bodyStyleParser.parse(jsonData))
        expectedBodyStyles = [BodyStyle(title="Standard",
                                       metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_BASE_MSRP,
                                                                   value=46_900, unit=MetadataUnit.DOLLARS)])]
        self.assertEqual(expectedBodyStyles, foundBodyStyles)
        expectedBodyStyles[0]._assertStrictEq(foundBodyStyles[0])
