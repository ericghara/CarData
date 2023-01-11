import logging
from unittest import TestCase

from transformer.attribute_dto.AttributeDto import Accessory
from transformer.attribute_metadata.AttributeMetadata import AttributeMetadata
from transformer.attribute_metadata.MetadataType import MetadataType
from transformer.attribute_metadata.MetadataUnit import MetadataUnit
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser.AccessoryParser import AccessoryParser


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

