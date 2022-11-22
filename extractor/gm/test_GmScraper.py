from datetime import date
from unittest import TestCase, mock
from unittest.mock import MagicMock, ANY
from uuid import uuid4

from requests import Response

from extractor.gm.GmScraper import GmScraper
from repository.Entities import Brand
from repository.test_common.mockSessionFactory import MockSessionFactory


class TestGmScraper(TestCase):

    def setUp(self) -> None:
        self.brand = Brand(brand_id=uuid4(), manufacturer_id=uuid4(), name='General Motors')
        self.sessionFactoryMock = MockSessionFactory()
        self.patcherSuperBrandService = mock.patch('extractor.ModelInfoScraper.brandService.getBrandByName',
                                                   return_value=self.brand)
        self.superBrandServiceMock = self.patcherSuperBrandService.start()
        self.httpClientResponseMock = Response()
        self.httpClientResponseMock.json = MagicMock(return_value={})
        self.patcherHttpClient = mock.patch('extractor.gm.GmScraper.httpClient.getRequest',
                                            return_value=self.httpClientResponseMock)
        self.httpClientMock = self.patcherHttpClient.start()
        self.scraper = GmScraper('chevrolet', 'https://www.chevrolet.com', noInit=True)

    def tearDown(self) -> None:
        for mockObj in self.patcherSuperBrandService, self.patcherHttpClient:
            if mockObj:
                mockObj.stop()
        self.scraper = None

    def test__getBodyStyleToCarlineCorrectlyParses(self):
        json = {'2019': {'trax': {'trax': {}}},
                '2018': {'express': {'express-passenger': {},
                                     'express-cargo': {}},
                         'corvette': {'corvette-grandsport': {},
                                      'corvette-z06': {},
                                      'corvette': {}}
                         }}
        self.httpClientResponseMock.json = MagicMock(return_value=json)
        expected = {'trax': 'trax', 'express-passenger': 'express', 'express-cargo': 'express',
                    'corvette-grandsport': 'corvette', 'corvette-z06': 'corvette', 'corvette': 'corvette'}
        found = self.scraper._getBodyStyleToCarLine()
        self.assertEqual(expected, found)

    def test__getBodyStyleToCarLineCorrectURL(self):
        json = {'2019': {}}
        self.httpClientResponseMock.json = MagicMock(return_value=json)
        self.scraper._getBodyStyleToCarLine()
        expectedURL = 'https://www.chevrolet.com/apps/atomic/shoppingLinks.brand=chevrolet.country=US.region=na.language=en.json'
        self.httpClientMock.assert_called_with(expectedURL)

    def test__getModelCodeToNameCorrectURL(self):
        mockToday = date(2022, 1, 1)
        with mock.patch('extractor.gm.GmScraper.date') as mockDate:
            mockDate.today.return_value = mockToday
            self.scraper._getModelCodeToName()
        for year in (2022,2023,2021):
            self.httpClientMock.assert_any_call(f'https://www.chevrolet.com/bypass/pcf/vehicle-selector-service/v1/getVehicleInfo/chevrolet/us/b2c/en?requestType=models&year={year}', headers=ANY)

    def test__getModelCodeToNameCorrectlyParses(self):
        json = {'status': 200,
                'options': [{'code': 'blazer',
                             'title': 'Blazer'},
                            {'code': 'bolt-euv',
                             'title': 'Bolt EUV'}]}
        self.httpClientResponseMock.json = MagicMock(return_value=json)
        expected = {'blazer': 'Blazer', 'bolt-euv': 'Bolt EUV'}
        found = self.scraper._getModelCodeToName()
        self.assertEqual(expected, found)
