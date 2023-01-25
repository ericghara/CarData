import logging
from typing import Optional
from unittest import TestCase

from parameterized import parameterized

from common.domain.dto.AttributeDto import Engine
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.FuelType import FuelType
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.transform.toyota.parser.EngineParser import EngineParser
from transformer.transform.toyota.parser.LoggingTools import LoggingTools


class TestEngineParser(TestCase):

    def setUp(self):
        self.loggingTools = LoggingTools(logging.getLogger())
        self.engineParser = EngineParser(self.loggingTools)

    noTitle = {"engine": {}}
    noTitleEngine = None

    @parameterized.expand([("Battery Electric", FuelType.ELECTRIC.value, "Electric"),
                           ("Fuel Cell", FuelType.FUEL_CELL.value, "Fuel Cell"),
                           ("Gas", FuelType.GASOLINE.value, "Gasoline"),
                           ("Plug-in Hybrid", FuelType.PLUG_IN_HYBRID.value, "PHEV"),
                           ("Hybrid", FuelType.HYBRID.value, "Hybrid")])
    def test_getFuelTypeRecognizedTypes(self, fuelTypeStr: str, expectedFuelType: Optional[str], testIdentifier: str):
        modelJson = {'attributes':{'fueltype':{'value' : fuelTypeStr}}}
        foundMetadata = self.engineParser._getFuelType(modelJson)
        self.assertEqual(expectedFuelType, foundMetadata.value, testIdentifier)

    def test_getFuelTypeUnrecognizedType(self):
        modelJson = {'attributes': {'fueltype': {'value': "Nuclear Fussion"}}}
        self.assertIsNone(self.engineParser._getFuelType(modelJson))

    def test_parseModelNoTitle(self):
        found = self.engineParser._parseModel(self.noTitle)
        self.assertIsNone(found)

    onlyTitle = {"engine": {"title": "1ZZ-FE"}}
    onlyTitleEngine = Engine("1ZZ-FE")

    def test_parseModelOnlyTitle(self):
        found = self.engineParser._parseModel(self.onlyTitle)
        self.onlyTitleEngine._assertStrictEq(found)

    titleNoneMetadata = {"engine": {"title": "2JZ-GTE",
                                    "attributes": {
                                        "fueltype": {"value": None},
                                        "horsepower": {"value": None},
                                        "cylinders": {"value": None}
                                    }}}
    titleNoneMetadataEngine = Engine("2JZ-GTE")

    def test_parseModelTitleNoneMetadata(self):
        found = self.engineParser._parseModel(self.titleNoneMetadata)
        self.titleNoneMetadataEngine._assertStrictEq(found)

    titleFullMetadata = {"engine": {"title": "2AZ-FE"},
                         "attributes": {
                             "fueltype": {"value": "Gas"},
                             "horsepower": {"value": 145},
                             "cylinders": {"value": 4}
                         }}
    titleFullMetadataEngine = Engine(title="2AZ-FE", metadata=[
        AttributeMetadata(metadataType=MetadataType.ENGINE_FUEL_TYPE, value=FuelType.GASOLINE.value),
        AttributeMetadata(metadataType=MetadataType.ENGINE_HORSEPOWER, value=145, unit=MetadataUnit.HORSEPOWER),
        AttributeMetadata(metadataType=MetadataType.ENGINE_CYLINDERS, value=4)
    ])

    def test_parseModelTitleFullMetadata(self):
        found = self.engineParser._parseModel(self.titleFullMetadata)
        self.titleFullMetadataEngine._assertStrictEq(found)

    def test_parse(self):
        jsonData = {"model": [self.noTitle, self.onlyTitle, self.titleFullMetadata]}
        foundEngines = self.engineParser.parse(jsonData)
        self.assertEqual(2, len(foundEngines), "num engines found")
        expectedEnginesByTitle = {engine.title: engine for engine in
                                  [self.onlyTitleEngine, self.titleFullMetadataEngine]}
        for foundEngine in foundEngines:
            self.assertIsNotNone(expectedEngine := expectedEnginesByTitle.get(foundEngine.title),
                                 f"incorrect title {foundEngine}")
            expectedEngine._assertStrictEq(foundEngine)
