import datetime
import uuid
from unittest import TestCase, mock
from unittest.mock import MagicMock

from requests import Response

from extractor.common.fetchModelData import _addMetadata, _createUnsyncedModelDto, ModelFetchDto, _fetchJsonData, \
    ModelDtosAndJsonDataByName, fetchModels
from repository.dto import Model as ModelDto, Model


class Test(TestCase):

    def setUp(self) -> None:
        self.httpClientResponseMock = Response()
        self.httpClientResponseMock.json = MagicMock(return_value={})
        self.patcherHttpClient = mock.patch('extractor.common.fetchModelData.httpClient.getRequest',
                                            return_value=self.httpClientResponseMock)
        self.httpClientMock = self.patcherHttpClient.start()

    def tearDown(self) -> None:
        for mockObj in self.patcherHttpClient,:
            if mockObj:
                mockObj.stop()

    def test__addMetadataAddsItems(self):
        jsonData = {"rawData": "rawValue"}
        metadata = {"metaData": "metaValue"}
        _addMetadata(jsonData=jsonData, metadata=metadata)  # mutates jsonData
        expected = {"rawData": "rawValue", "metaData": "metaValue"}
        self.assertEqual(expected, jsonData)

    def test__addMetadataRaisesOnCollision(self):
        jsonData = {"collide": "rawValue"}
        metadata = {"collide": "metaValue"}
        self.assertRaises(KeyError, lambda: _addMetadata(jsonData=jsonData, metadata=metadata))

    def test__createUnsyncedModelDto(self):
        modelYear = datetime.date(2022, 1, 1)
        brandId = str(uuid.uuid4())
        modelFetchDto = ModelFetchDto(modelName="CarModel", modelCode="car-model", path="http://www.ericgha.com")
        expected = ModelDto(name="CarModel", model_year=modelYear, brand_id=brandId)
        self.assertEqual(expected,
                         _createUnsyncedModelDto(modelFetchDto=modelFetchDto, modelYear=modelYear, brandId=brandId))

    def test__fetchJsonDataSuccess(self):
        expected = {"success": True}
        self.httpClientResponseMock.json.return_value = expected
        modelFetchDto = ModelFetchDto(modelName="CarModel", modelCode="car-model", path="http://www.ericgha.com")
        found = _fetchJsonData(modelFetchDto)
        self.assertEqual(expected, found)

    def test__fetchJsonDataFailure(self):
        self.httpClientResponseMock.json.side_effect = RuntimeError("DummyError")
        modelFetchDto = ModelFetchDto(modelName="CarModel", modelCode="car-model", path="http://www.ericgha.com")
        self.assertIsNone(_fetchJsonData(modelFetchDto))

    def test_fetchModelsSuccessfulFetch(self):
        json = {"success": True}
        metadata = {"metadata": True}
        self.httpClientResponseMock.json.return_value = json
        modelFetchDtosByName = {
            "ModelName": ModelFetchDto(modelName="ModelName", modelCode="car-model", path="http://www.ericgha.com",
                                       metadata=metadata)}
        modelYear = datetime.date(2022, 1, 1)
        brandId = str(uuid.uuid4())
        expected = ModelDtosAndJsonDataByName(
            modelDtos=[ModelDto(name="ModelName", model_year=modelYear, brand_id=brandId)],
            jsonDataByName={"ModelName": {k: v for k, v in [*json.items()] + [*metadata.items()]}})
        found = fetchModels(modelFetchDtosByName=modelFetchDtosByName, brandId=brandId, modelYear=modelYear)
        self.assertEqual(expected, found)

    def test_fetchModelsFetchFailure(self):
        self.httpClientResponseMock.json.side_effect = RuntimeError("DummyError")
        modelFetchDtosByName = {
            "ModelName": ModelFetchDto(modelName="CarModel", modelCode="car-model", path="http://www.ericgha.com")}
        modelYear = datetime.date(2022, 1, 1)
        brandId = str(uuid.uuid4())
        expected = ModelDtosAndJsonDataByName(modelDtos=list(), jsonDataByName=dict())
        found = fetchModels(modelFetchDtosByName=modelFetchDtosByName, brandId=brandId, modelYear=modelYear)
        self.assertEqual(expected, found)
