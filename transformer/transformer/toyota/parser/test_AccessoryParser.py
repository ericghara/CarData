import logging
from unittest import TestCase

from common.domain.dto.AttributeDto import Accessory
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.transformer.toyota.LoggingTools import LoggingTools
from transformer.transformer.toyota.parser.AccessoryParser import AccessoryParser


class TestAccessoryParser(TestCase):

    def setUp(self):
        loggingTools = LoggingTools(logging.getLogger())
        self.accessoryParser = AccessoryParser(loggingTools)

    def test__parseModelTitlePriceCategory(self):
        modelJson = {"accessories": [
            {"title": "Touring Package",
             "price": "$2,540",
             "attributes": {"group": {"value": "Exterior"}}}]}
        foundAccessories = list(self.accessoryParser._parseModel(modelJson))
        expectedAccessories = [Accessory(title="Touring Package", metadata=[
            AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=2540, unit=MetadataUnit.DOLLARS),
            AttributeMetadata(metadataType=MetadataType.ACCESSORY_CATEGORY, value="Exterior")
        ])]
        self.assertEqual(expectedAccessories, foundAccessories)
        expectedAccessories[0]._assertStrictEq(foundAccessories[0])

    def test__parseModelTitleNullPriceNullCategory(self):
        modelJson = {"accessories": [
            {"title": "Touring Package",
             "price": None,
             "attributes": {"group": {"value": None}}}]}
        foundAccessories = list(self.accessoryParser._parseModel(modelJson))
        expectedAccessories = [Accessory(title="Touring Package")]
        self.assertEqual(expectedAccessories, foundAccessories)
        expectedAccessories[0]._assertStrictEq(foundAccessories[0])

    def test__parseModelAllNull(self):
        modelJson = {"accessories": [
            {"title": None,
             "price": None,
             "attributes": {"group": {"value": None}}}]}
        foundAccessoriesIter = self.accessoryParser._parseModel(modelJson)
        self.assertRaises(StopIteration, lambda: next(foundAccessoriesIter))

    def test__parseModelMultipleAccessories(self):
        modelJson = {"accessories": [
            {"title": "Touring Package"},
            {"title": "Cargo Net"}]}
        foundAccessories = set(self.accessoryParser._parseModel(modelJson))
        expectedAccessories = {Accessory(title="Touring Package"), Accessory(title="Cargo Net")}
        self.assertEqual(expectedAccessories, foundAccessories)  # loose __eq__ used, strictEq tested elsewhere

    def test__parseDuplicateAccessories(self):
        jsonData = {"model": [
            {"accessories": [{"title": "Touring Package"}]},
            {"accessories": [{"title": "Touring Package"}]}
        ]}
        foundAccessories = list(self.accessoryParser.parse(jsonData))
        expectedAccessories = [Accessory(title="Touring Package")]
        self.assertEqual(expectedAccessories, foundAccessories)

    def test__parseMultipleAccessories(self):
        jsonData = {"model": [
            {"accessories": [{"title": "Touring Package"}]},
            {"accessories": [{"title": "Cargo Net"}]},
            {"accessories": [{"title": None}]},
            {"accessories": [{}]},
            {"accessories": []},
            {}
        ]}
        foundAccessories = set(self.accessoryParser.parse(jsonData))
        expectedAccessories = {Accessory(title="Touring Package"), Accessory(title="Cargo Net")}
        self.assertEqual(expectedAccessories, foundAccessories)

    def test__parseModelDuplicatesKeepsHighestPrice(self):
        jsonData = {"model": [{"accessories": [
            {"title": "Cargo Net",
             "price": "$75.00"},
            {"title": "Cargo Net",
             "price": "$85.00"}]
        }]}
        foundAccessories = self.accessoryParser.parse(jsonData)
        expectedAccessories = [Accessory(title="Cargo Net", metadata=[
            AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=85, unit=MetadataUnit.DOLLARS)])]
        self.assertEqual(foundAccessories, expectedAccessories, "loose equality")
        foundAccessories[0]._assertStrictEq(expectedAccessories[0])
