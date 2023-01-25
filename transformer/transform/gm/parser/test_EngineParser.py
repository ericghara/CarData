import logging
from typing import Optional, Dict
from unittest import TestCase

from parameterized import parameterized

from common.domain.dto.AttributeDto import Engine
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.FuelType import FuelType
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.transform.gm.parser.EngineParser import EngineParser
from transformer.transform.gm.parser.LoggingTools import LoggingTools


class TestEngineParser(TestCase):

    def setUp(self) -> None:
        loggingTools = LoggingTools(logger=logging.getLogger(type(self).__name__))
        self.parser = EngineParser(loggingTools)

    @parameterized.expand([
        ({"shortCFD": "Big Engine"}, "Big Engine", "Title present"),
        ({"shortCFD": None}, None, "Title null"),
        ({}, None, "Title no Key")
    ])
    def test__getTitle(self, engineDict: Dict, expectedTitle: Optional[str], testIdentifier: str):
        foundTitle = self.parser._getTitle(engineDict=engineDict, modelIdentifier="Test")
        self.assertEqual(expectedTitle, foundTitle, testIdentifier)

    @parameterized.expand([
        ({"extendedCFD": "features 300 hp. More features."},
         AttributeMetadata(metadataType=MetadataType.ENGINE_HORSEPOWER, value=300, unit=MetadataUnit.HORSEPOWER),
         "Hp present in extendedCFD"),
        ({"longCFD": "features 300.6 hp. More features."},
         AttributeMetadata(metadataType=MetadataType.ENGINE_HORSEPOWER, value=301, unit=MetadataUnit.HORSEPOWER),
         "Hp present in longCfd"),
        ({"longCFD": "features lots of hp. More features.", "extendedCFD": "features"}, None,
         "Hp not present in long or extendedCFD"),
        ({"longCFD": "features lots of hp. More features. 300hp."},
         AttributeMetadata(metadataType=MetadataType.ENGINE_HORSEPOWER, value=300, unit=MetadataUnit.HORSEPOWER),
         "Hp followed by period"),
        ({}, None, "longCFD extendedCFD keys not present")
    ])
    def test__getPower(self, engineDict: Dict, expectedPower: Optional[AttributeMetadata], testIdentifer: str):
        foundPower = self.parser._getPower(engineDict=engineDict, modelIdentifier="test")
        self.assertEqual(expectedPower, foundPower, testIdentifer)

    @parameterized.expand([({"primaryName": "Duramax 3.0L"}, FuelType.GASOLINE.value, "gas #.#L"),
                           ({"primaryName": "Duramax 3L"}, FuelType.GASOLINE.value, "gas #L"),
                           ({"primaryName": "Duramax 3L DiEsEl"}, FuelType.DIESEL.value, "diesel #L"),
                           ({"primaryName": "Engine, standard"}, None, "Neither gas, diesel nor electric"),
                           ({"primaryName": "Engine, standard", "description": "ElEcTrIc Drive."}, FuelType.ELECTRIC.value,
                            "Neither gas, diesel nor electric"),
                           ({"primaryName": None, "description": None}, None,
                            "Keys null"),
                           ({}, None, "No Keys")
                           ])
    def test__getFuelType(self, engineDict: Dict, expectedFuelValue: Optional[str], testIdentifier: str):
        expectedFuel = None
        if expectedFuelValue:
            expectedFuel = AttributeMetadata(metadataType=MetadataType.ENGINE_FUEL_TYPE, value=expectedFuelValue)
        foundFuel = self.parser._getFuelType(engineDict=engineDict, modelIdentifier="test")
        self.assertEqual(expectedFuel, foundFuel, testIdentifier)

    @parameterized.expand([({'msrp': 3_000}, 3000, "msrp present"),
                           ({'msrp': None}, None, "msrp null"),
                           ({}, None, "msrp no Key")])
    def test__getPrice(self, engineDict: Dict, expectedPriceValue: Optional[int], testIdentifier: str):
        expectedPrice = None
        if expectedPriceValue:
            expectedPrice = AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=expectedPriceValue,
                                              unit=MetadataUnit.DOLLARS)
        foundPrice = self.parser._getPrice(engineDict=engineDict, modelIdentifier="test")
        self.assertEqual(expectedPrice, foundPrice, testIdentifier)

    @parameterized.expand([
        ({"modelMatrix": {"engine": [{"shortCFD": "Big Engine"}]}}, [Engine(title="Big Engine")],
         "Title no Attributes"),
        ({"modelMatrix": {
            "engine": [{"shortCFD": "Big Engine", "msrp": 3000, "primaryName": "3.0L", "extendedCFD": "300 hp."}]}},
         [Engine(title="Big Engine",
                 metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=3_000,
                                             unit=MetadataUnit.DOLLARS),
                           AttributeMetadata(metadataType=MetadataType.ENGINE_FUEL_TYPE,
                                             value=FuelType.GASOLINE.value),
                           AttributeMetadata(metadataType=MetadataType.ENGINE_HORSEPOWER, value=300,
                                             unit=MetadataUnit.HORSEPOWER)
                           ])], "Title all attributes"),
        ({"modelMatrix": {"engine": [{"shortCFD": "Big Engine"}, {"shortCFD": "Little Engine"}]}},
         [Engine("Big Engine"), Engine("Little Engine")],
         "Two valid engines"),
        ({"modelMatrix": {"engine": [{}]}}, [], "one empty engine"),
        ({"modelMatrix": {"engine": None}}, [], "engine key, has null value"),
        ({"modelMatrix": {}}, [], "No Engine Key")
    ])
    def test_parseSingleEngine(self, dataDict: Dict, expectedEngines, testIdentifier: str):
        foundEngines = self.parser.parse(dataDict)
        self.assertEqual(len(expectedEngines), len(foundEngines), testIdentifier)
        # make test insensitive to order of engines
        enginesByTitle = lambda engines: {engine.title: engine for engine in engines}
        expectedEnginesByTitle = enginesByTitle(expectedEngines)
        foundEnginesByTitle = enginesByTitle(foundEngines)
        for title, expectedEngine in expectedEnginesByTitle.items():
            foundEngine = foundEnginesByTitle.get(title)
            expectedEngine._assertStrictEq(foundEngine)
