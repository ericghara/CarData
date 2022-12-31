import json
from datetime import datetime, date
from unittest import TestCase, mock
from unittest.mock import MagicMock
from uuid import uuid4

from parameterized import parameterized
from requests import Response

from extractor.common.fetchModelData import ModelFetchDto
from extractor.toyota.LexusScraper import LexusScraper
from repository.Entities import Brand, Manufacturer
from repository.SessionFactory import sessionFactory
from repository.test_common.DbContainer import DbContainer
from repository.test_common.mockSessionFactory import MockSessionFactory
from service.ModelService import modelService
from service.RawDataService import rawDataService


class TestLexusScraper(TestCase):

    def setUp(self) -> None:
        self.brand = Brand(brand_id=uuid4(), manufacturer_id=uuid4(), name='Lexus')
        self.sessionFactoryMock = MockSessionFactory()
        self.patcherSuperBrandService = mock.patch('extractor.ModelInfoScraper.brandService.getBrandByName', return_value=self.brand)
        self.superBrandServiceMock = self.patcherSuperBrandService.start()
        self.httpClientResponseMock = Response()
        self.httpClientResponseMock.json = MagicMock(return_value={})
        self.patcherHttpClient = mock.patch('extractor.toyota.LexusScraper.httpClient.getRequest',
                             return_value=self.httpClientResponseMock)
        self.httpClientMock = self.patcherHttpClient.start()
        self.scraper = LexusScraper()

    def tearDown(self) -> None:
        for mockObj in self.patcherSuperBrandService, self.patcherHttpClient:
            if mockObj:
                mockObj.stop()
        self.scraper = None

    @parameterized.expand([
        ('IS', 'IS'),
        ('NXh', 'NX Hybrid'),
        ('RCF', 'RC F'),
        ('ISC', 'IS C'),
        ('NXPHEV', 'NX PHEV'),
        ('LCCV', 'LC Convertable')
    ])
    def test__getModelName(self, modelCode, expectedModelName):
        self.assertEqual(expectedModelName, self.scraper._getModelName(modelCode) )

    def test_getModelNameRaisesUnrecognizedFormat(self):
        raises = lambda : self.scraper._getModelName('LCS')
        self.assertRaises(ValueError, raises)

    def test__parseModelList(self):
        modelListJson = [{'featureModel': 'LCCV', 'path': 'fakePath'}]
        expectedPath = "http://fake.com/content.json"
        expectedModelList = {
            'LC Convertable': ModelFetchDto(modelName='LC Convertable', modelCode='LCCV', path=expectedPath)}
        with mock.patch('extractor.toyota.test_LexusScraper.LexusScraper._createModelDataURL',
                        return_value=expectedPath):
            self.assertEqual(expectedModelList, self.scraper._parseModelList(modelListJson))

    def test__createModelData_url(self):
        self.scraper.URL_PREFIX = 'https://www.lexus.com/config/pub'
        subPath = '/static/uifm/LEX/NATIONAL/EN/ebd9b27e2cb2f5e2bce935c82b4d4f23c8b83eb1/2023/IS/8579e8c9a2d17551ffd83b9016595bab206bd9fd'
        expected = 'https://www.lexus.com/config/pub/static/uifm/LEX/NATIONAL/EN/ebd9b27e2cb2f5e2bce935c82b4d4f23c8b83eb1/2023/IS/8579e8c9a2d17551ffd83b9016595bab206bd9fd/content.json'
        self.assertEqual(expected, self.scraper._createModelDataURL(subPath))

class IntegrationTestToyotaScraper(TestCase):
    container = None

    @classmethod
    def setUpClass(cls):
        cls.container = DbContainer()
        cls.container.start()
        cls.container.initTables()

    @classmethod
    def tearDownClass(cls) -> None:
              cls.container.stop() 

    def setUp(self) -> None:
        with sessionFactory.newSession() as session:
            # manufacturer
            toyotaManufacturer = Manufacturer(official_name='Toyota Motor Company', common_name='Toyota')
            session.add(toyotaManufacturer)
            lexusBrand = Brand(name='Lexus', manufacturer=toyotaManufacturer)
            session.add(lexusBrand)
            session.commit()
        self.httpClientResponseMock = Response()
        self.httpClientResponseMock.json = MagicMock(return_value={})
        patcher = mock.patch('extractor.common.fetchModelData.httpClient.getRequest',
                             return_value=self.httpClientResponseMock)
        self.httpClientMock = patcher.start()
        self.scraper = LexusScraper()

    def tearDown(self) -> None:
        self.container.deleteAll()
        self.httpClientMock.stop()

    def test_persist_model_year(self):
        modelYear = date(2023, 1, 1)
        nameToModelInfo = {'LC Convertable': ModelFetchDto('LC Convertable', 'LCCV', 'http://lexus.com/content.json'),
                           'ES Hybrid': ModelFetchDto('ES Hybrid', 'ESh', 'http://lexus.com/content.json')}
        rawJson = {'Dummy_JSON': True}
        self.httpClientResponseMock.json = MagicMock(return_value=rawJson)
        with mock.patch('extractor.toyota.test_LexusScraper.LexusScraper._parseModelList',
                        return_value=nameToModelInfo):
            self.scraper.persistModelYear(modelYear)
        with sessionFactory.newSession() as session:
            models = modelService.getModelYear(modelYear=modelYear, manufacturerCommon='Toyota', session=session,
                                               brandName=self.scraper.brand.name)
            for model in models:
                self.assertIn(model.name, nameToModelInfo.keys())
                self.assertEqual(rawJson, rawDataService.getMostRecentlyCreated(brandName=self.scraper.brand.name,
                                                                                modelName=model.name,
                                                                                modelYear=modelYear,
                                                                                session=session).raw_data)