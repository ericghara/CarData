import datetime
from unittest import TestCase, mock
from unittest.mock import Mock, MagicMock
from uuid import uuid4

from requests import Response

from extractor.toyota.ToyotaScraper import ToyotaScraper
from repository.Entities import Brand


class TestToyotaScraper(TestCase):

    def setUp(self) -> None:
        self.scraper = None
        self.brand = Brand(brand_id=uuid4(), manufacturer_id=uuid4(), name='Toyota')
        self.superBrandServiceMock = None
        self.httpClientMock = None
        self.httpClientResponseMock = None
        patcher = mock.patch('extractor.ModelInfoScraper.brandService.getBrandByName', return_value=self.brand )
        self.superBrandServiceMock = patcher.start()
        self.httpClientResponseMock = Response()
        self.httpClientResponseMock.json = MagicMock(return_value = {} )
        patcher = mock.patch('extractor.toyota.ToyotaScraper.httpClient.getRequest', return_value=self.httpClientResponseMock )
        self.httpClientMock = patcher.start()
        self.scraper = ToyotaScraper()

    def tearDown(self) -> None:
        for mock in self.superBrandServiceMock, self.httpClientMock:
            if mock:
                mock.stop()
        self.scraper = None

    def test__getModelCodeToName(self):
        rawJson = [{'modelName' : 'GR Supra', 'modelCode' : 'supra', 'Unneeded Key' : 'Unneeded Value'}]
        expectedResponse = {'supra' : 'GR Supra'}
        self.httpClientResponseMock.json = MagicMock(return_value = rawJson)
        self.assertEqual(expectedResponse, self.scraper._getModelCodeToName() )

    def test__getModelNameFoundInModelCodeToName(self):
        self.scraper.modelCodeToName = {'supra' : 'GR Supra'}
        self.assertEqual('GR Supra', self.scraper._getModelName('supra') )

    def test__getModelNameFoundInMODEL_CODES(self):
        self.scraper.MODEL_CODES = {'86': 'GR 86'}
        self.assertEqual('GR 86', self.scraper._getModelName('86'))

    def test__getModelNameNotFound(self):
        self.scraper.MODEL_CODES = dict()
        # capitalizes each word
        self.assertEqual('Camry', self.scraper._getModelName('camry') )

    def test__fetch_model_list(self):
        self.fail()

    def test__parseModelList(self):
        modelListJson = [{'featureModel' : '86', 'archived' : True, 'path' : 'fakePath'}]
        self.scraper.MODEL_CODES = {'86': 'GR 86'}
        expectedPath = "http://fake.com/content.json"
        expectedModelList = {'GR 86' : ToyotaScraper.ModelInfo(modelName='GR 86', modelCode='86', path=expectedPath, isArchived=True) }
        with mock.patch('extractor.toyota.test_toyotaScraper.ToyotaScraper._createModelDataURL', return_value=expectedPath):
            self.assertEqual(expectedModelList, self.scraper._parseModelList(modelListJson) )


    def test__createModelData_url(self):
        self.scraper.URL_PREFIX = 'https://www.toyota.com/config/pub'
        subPath = '/static/uifm/TOY/NATIONAL/EN/2a6c7dd95b5b81c1dda97a6b985eec703140fd4d/2022/priusprime/1813aacf15413225b2ee3129fe1c9770cbab8bdd'
        expected = 'https://www.toyota.com/config/pub/static/uifm/TOY/NATIONAL/EN/2a6c7dd95b5b81c1dda97a6b985eec703140fd4d/2022/priusprime/1813aacf15413225b2ee3129fe1c9770cbab8bdd/content.json'
        self.assertEqual(expected, self.scraper._createModelDataURL(subPath) )

    def test__fetch_model_year(self):
        nameToModelInfo = {'GR 86': ToyotaScraper.ModelInfo('GR 86', '86', 'http://toyota.com/content.json', False),
                           'GR Supra': ToyotaScraper.ModelInfo('GR Supra', 'supra', 'http://toyota.com/content.json', False) }
        rawJson = {'Dummy_JSON' : True}
        expected = {'GR 86' : rawJson, 'GR Supra' : rawJson }
        with mock.patch('extractor.toyota.test_toyotaScraper.ToyotaScraper._parseModelList', return_value=nameToModelInfo):
            self.httpClientResponseMock.json = MagicMock(return_value=rawJson)
            found = self.scraper._fetchModelYear(datetime.date(2023,1,1) )
            self.assertEqual(expected, found)

    def test_persist_model_year(self):
        self.fail()
