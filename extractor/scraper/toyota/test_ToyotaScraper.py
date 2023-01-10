from unittest import TestCase, mock
from unittest.mock import MagicMock
from uuid import uuid4

from requests import Response

from extractor.scraper.common.fetchModelData import ModelFetchDto
from extractor.scraper.toyota.ToyotaScraper import ToyotaScraper
from repository.Entities import Brand
from repository.test_common.mockSessionFactory import MockSessionFactory


class TestToyotaScraper(TestCase):

    def setUp(self) -> None:
        self.brand = Brand(brand_id=uuid4(), manufacturer_id=uuid4(), name='toyota')
        self.sessionFactoryMock = MockSessionFactory()
        self.httpClientResponseMock = Response()
        self.httpClientResponseMock.json = MagicMock(return_value={})
        self.patcherHttpClient = mock.patch('extractor.scraper.toyota.ToyotaScraper.httpClient.getRequest',
                             return_value=self.httpClientResponseMock)
        self.httpClientMock = self.patcherHttpClient.start()
        self.scraper = ToyotaScraper()

    def tearDown(self) -> None:
        for mockObj in self.patcherHttpClient,:
            if mockObj:
                mockObj.stop()
        self.scraper = None

    def test__getModelCodeToName(self):
        rawJson = [{'modelName': 'GR Supra', 'modelCode': 'supra', 'Unneeded Key': 'Unneeded Value'}]
        expectedResponse = {'supra': 'GR Supra'}
        self.httpClientResponseMock.json = MagicMock(return_value=rawJson)
        self.assertEqual(expectedResponse, self.scraper._getModelCodeToName())

    def test__getModelNameFoundInModelCodeToName(self):
        self.scraper.modelCodeToName = {'supra': 'GR Supra'}
        self.assertEqual('GR Supra', self.scraper._getModelName('supra'))

    def test__getModelNameFoundInMODEL_CODES(self):
        self.scraper.MODEL_CODES = {'86': 'GR 86'}
        self.assertEqual('GR 86', self.scraper._getModelName('86'))

    def test__getModelNameNotFound(self):
        self.scraper.MODEL_CODES = dict()
        # capitalizes each word
        self.assertEqual('Camry', self.scraper._getModelName('camry'))

    def test__parseModelList(self):
        modelListJson = [{'featureModel': '86', 'path': 'fakePath'}]
        self.scraper.MODEL_CODES = {'86': 'GR 86'}
        expectedPath = "http://fake.com/content.json"
        expectedModelList = {
            'GR 86': ModelFetchDto(modelName='GR 86', modelCode='86', path=expectedPath)}
        with mock.patch('extractor.scraper.toyota.test_ToyotaScraper.ToyotaScraper._createModelDataURL',
                        return_value=expectedPath):
            self.assertEqual(expectedModelList, self.scraper._parseModelList(modelListJson))

    def test__createModelData_url(self):
        self.scraper.URL_PREFIX = 'https://www.toyota.com/config/pub'
        subPath = '/static/uifm/TOY/NATIONAL/EN/2a6c7dd95b5b81c1dda97a6b985eec703140fd4d/2022/priusprime/1813aacf15413225b2ee3129fe1c9770cbab8bdd'
        expected = 'https://www.toyota.com/config/pub/static/uifm/TOY/NATIONAL/EN/2a6c7dd95b5b81c1dda97a6b985eec703140fd4d/2022/priusprime/1813aacf15413225b2ee3129fe1c9770cbab8bdd/content.json'
        self.assertEqual(expected, self.scraper._createModelDataURL(subPath))
