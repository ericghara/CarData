import datetime
from unittest import TestCase
from extractor.common.fetchAndPersist import _addMetadata, _createUnsyncedModelDtos, ModelFetchDto
from repository.dto import Model as ModelDto


class Test(TestCase):

    def test__addMetadataAddsItems(self):
        jsonData = {"rawData" : "rawValue"}
        metadata = {"metaData" : "metaValue"}
        _addMetadata(jsonData=jsonData, metadata=metadata) # mutates jsonData
        expected = {"rawData" : "rawValue", "metaData" : "metaValue"}
        self.assertEqual(expected, jsonData)

    def test__addMetadataRaisesOnCollision(self):
        jsonData = {"collide": "rawValue"}
        metadata = {"collide": "metaValue"}
        self.assertRaises(KeyError, lambda: _addMetadata(jsonData=jsonData, metadata=metadata) )

    def test__createUnsyncedModelDtos(self):
        modelYear = datetime.date(2022,1,1)
        brandId = "ByteWagon"
        modelFetchDtosByName = {"CarName" : ModelFetchDto(modelName="CarModel", modelCode="car-model", path="http://www.ericgha.com")}
        expected = [ ModelDto(name="CarModel", model_year=modelYear, brand_id=brandId) ]
        self.assertEqual(expected, _createUnsyncedModelDtos(modelFetchDtosByName=modelFetchDtosByName, modelYear=modelYear, brandId=brandId) )