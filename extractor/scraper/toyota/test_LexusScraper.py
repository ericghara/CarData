from unittest import TestCase, mock
from unittest.mock import MagicMock

from parameterized import parameterized
from requests import Response

from extractor.scraper.common.fetchModelData import ModelFetchDto
from extractor.scraper.toyota.LexusScraper import LexusScraper


class TestLexusScraper(TestCase):

    def setUp(self) -> None:
        self.httpClientResponseMock = Response()
        self.httpClientResponseMock.json = MagicMock(return_value={})
        self.patcherHttpClient = mock.patch('extractor.scraper.toyota.LexusScraper.httpClient.getRequest',
                                            return_value=self.httpClientResponseMock)
        self.httpClientMock = self.patcherHttpClient.start()
        self.scraper = LexusScraper()

    def tearDown(self) -> None:
        for mockObj in self.patcherHttpClient,:
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
        self.assertEqual(expectedModelName, self.scraper._getModelName(modelCode))

    def test_getModelNameRaisesUnrecognizedFormat(self):
        raises = lambda: self.scraper._getModelName('LCS')
        self.assertRaises(ValueError, raises)

    def test__parseModelList(self):
        modelListJson = [{'featureModel': 'LCCV', 'path': 'fakePath'}]
        expectedPath = "http://fake.com/content.json"
        expectedModelList = {
            'LC Convertable': ModelFetchDto(modelName='LC Convertable', modelCode='LCCV', path=expectedPath)}
        with mock.patch('extractor.scraper.toyota.test_LexusScraper.LexusScraper._createModelDataURL',
                        return_value=expectedPath):
            self.assertEqual(expectedModelList, self.scraper._parseModelList(modelListJson))

    def test__createModelData_url(self):
        self.scraper.URL_PREFIX = 'https://www.lexus.com/config/pub'
        subPath = '/static/uifm/LEX/NATIONAL/EN/ebd9b27e2cb2f5e2bce935c82b4d4f23c8b83eb1/2023/IS/8579e8c9a2d17551ffd83b9016595bab206bd9fd'
        expected = 'https://www.lexus.com/config/pub/static/uifm/LEX/NATIONAL/EN/ebd9b27e2cb2f5e2bce935c82b4d4f23c8b83eb1/2023/IS/8579e8c9a2d17551ffd83b9016595bab206bd9fd/content.json'
        self.assertEqual(expected, self.scraper._createModelDataURL(subPath))