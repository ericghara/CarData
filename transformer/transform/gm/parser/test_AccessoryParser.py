import logging
from typing import Dict, Optional, List
from unittest import TestCase

from parameterized import parameterized

from common.domain.dto.AttributeDto import Accessory
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.transform.gm.parser.AccessoryParser import AccessoryParser
from transformer.transform.gm.parser.LoggingTools import LoggingTools


class TestAccessoryParser(TestCase):

    def setUp(self) -> None:
        loggingTools = LoggingTools(logging.getLogger(name=type(self).__name__))
        self.parser = AccessoryParser(loggingTools=loggingTools)

    completeAccessory = {'msrp': 170,
                         'primaryName': 'A Tool'}

    nullAccessory = {'msrp': None,
                     'primaryName': None}

    emptyAccessory = {}

    @parameterized.expand([(completeAccessory, 'A Tool'),
                           ({'msrp': 'a'}, None),
                           (nullAccessory, None),
                           (emptyAccessory, None)])
    def test__getTitle(self, accessoryDict: Dict, expectedTitle: Optional[str]):
        foundTitle = self.parser._getTitle(accessoryDict=accessoryDict, modelIdentifier="test")
        self.assertEqual(expectedTitle, foundTitle)

    @parameterized.expand([(completeAccessory, AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=170,
                                                                 unit=MetadataUnit.DOLLARS)), (nullAccessory, None),
                           (nullAccessory, None),
                           (emptyAccessory, None)])
    def test__getPrice(self, accessoryDict: Dict, expectedPrice: int):
        foundPrice = self.parser._getPrice(accessoryDict=accessoryDict, modelIdentifier="test")
        self.assertEqual(expectedPrice, foundPrice)

    completeAccessoriesDict = {'config': {'ACCESSORIES':
                                              {'Tools':
                                                   [{'msrp': 170,
                                                     'primaryName': 'A Tool'}]
                                               }
                                          }}

    nullAccessoriesDict = {'config': {'ACCESSORIES':
                                          {'Tools':
                                               [{'msrp': None,
                                                 'primaryName': None}]
                                           }
                                      }}

    @parameterized.expand([
        (completeAccessoriesDict, [Accessory(title='A Tool', metadata=[
            AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=170,
                              unit=MetadataUnit.DOLLARS),
            AttributeMetadata(metadataType=MetadataType.ACCESSORY_CATEGORY, value="Tools")])]),
        (nullAccessoriesDict, list()),
        ({}, list())])
    def test__parse(self, dataDict: Dict, expectedAccessories: List[Accessory]):
        foundAccessories = self.parser.parse(dataDict=dataDict)
        self.assertEqual(expectedAccessories, foundAccessories)
        # only works for found accessories of length <= 1!
        for expectedAccessory, foundAccessory in zip(expectedAccessories, foundAccessories):
            expectedAccessory._assertStrictEq(foundAccessory)
