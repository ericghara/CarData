from datetime import date
from unittest import TestCase, mock
from unittest.mock import MagicMock, ANY, Mock
from uuid import uuid4

from requests import Response

from extractor.scraper.common.fetchModelData import ModelFetchDto
from extractor.scraper.gm.GmScraper import GmScraper, CarLineAndBodyStyle, BodyStyleAndName
from repository.Entities import Brand


class TestGmScraper(TestCase):

    def setUp(self) -> None:
        self.brand = Brand(brand_id=uuid4(), manufacturer_id=uuid4(), name='General Motors')
        self.httpClientResponseMock = Response()
        self.httpClientResponseMock.json = MagicMock(return_value={})
        self.patcherHttpClient = mock.patch('extractor.scraper.gm.GmScraper.httpClient.getRequest',
                                            return_value=self.httpClientResponseMock)
        self.httpClientMock = self.patcherHttpClient.start()
        self.scraper = GmScraper('Chevrolet', 'https://www.chevrolet.com', noInit=True, noPersist=True)

    def tearDown(self) -> None:
        for mockObj in self.patcherHttpClient,:
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
        with mock.patch('extractor.scraper.gm.GmScraper.date') as mockDate:
            mockDate.today.return_value = mockToday
            self.scraper._getBodyStyleToName()
        for year in (2022, 2023, 2021):
            self.httpClientMock.assert_any_call(
                f'https://www.chevrolet.com/bypass/pcf/vehicle-selector-service/v1/getVehicleInfo/chevrolet/us/b2c/en?requestType=models&year={year}',
                headers=ANY)

    def test__getModelCodeToNameCorrectlyParses(self):
        json = {'status': 200,
                'options': [{'code': 'blazer',
                             'title': 'Blazer'},
                            {'code': 'bolt-euv',
                             'title': 'Bolt EUV'}]}
        self.httpClientResponseMock.json = MagicMock(return_value=json)
        expected = {'blazer': 'Blazer', 'bolt-euv': 'Bolt EUV'}
        found = self.scraper._getBodyStyleToName()
        self.assertEqual(expected, found)

    def test__fetchBodyStylesRaisesWhenNoData(self):
        ERROR_MSG = "DummyError"
        with mock.patch('extractor.scraper.gm.GmScraper.httpClient.getRequest') as errorClient:
            errorClient.side_effect = ValueError(ERROR_MSG)
            # Unfortunately need to distinguish between httpClient throwing a ValueError and _fetchBodyStyles.  So we're
            # making sure our mock's error is being handled by the _fetchBodyStyles method by testing that ERROR_MSG isn't there
            self.assertRaisesRegex(ValueError, f"^((?!{ERROR_MSG}).)*$",
                                   lambda: self.scraper._fetchBodyStyles(date(2022, 1, 1)))

    def test__fetchBodyStylesReturnsExpected(self):
        self.scraper._fetchCarLinesAndBodyStyles = Mock(return_value=[CarLineAndBodyStyle("corvette", "corvette-z06")])
        self.scraper._fetchBodyStylesAndNames = Mock(return_value=[BodyStyleAndName("blazar", "Blazar")])
        # ensure both sources are used to create bodyStyle list (using a hacky monkey patch...)
        self.assertEqual({"blazar", "corvette-z06"}, set(self.scraper._fetchBodyStyles(date(2022, 1, 1))))

    def test__createModelDataPathFullyConfigured(self):
        expected = "https://www.chevrolet.com/byo-vc/services/fullyConfigured/US/en/chevrolet/2022/silverado/silverado-3500hd?postalCode=94102&region=na"
        found = self.scraper._createModelDataPath(carLine="silverado", bodyStyle="silverado-3500hd",
                                                  modelYear=date(2022, 1, 1), api='fullyConfigured')
        self.assertEqual(expected, found)

    def test__createModelDataPathDefault(self):
        expected = "https://www.chevrolet.com/byo-vc/api/v2/trim-matrix/en/US/chevrolet/silverado/2022/silverado-3500hd?postalCode=94102"
        found = self.scraper._createModelDataPath(carLine="silverado", bodyStyle="silverado-3500hd",
                                                  modelYear=date(2022, 1, 1) )
        self.assertEqual(expected, found)

    def test__createModelDataTrimMatrix(self):
        expected = "https://www.chevrolet.com/byo-vc/api/v2/trim-matrix/en/US/chevrolet/silverado/2022/silverado-3500hd?postalCode=94102"
        found = self.scraper._createModelDataPath(carLine="silverado", bodyStyle="silverado-3500hd",
                                                  modelYear=date(2022, 1, 1), api='trim-matrix' )
        self.assertEqual(expected, found)

    def test__createModelFetchDtoReturnsExpected(self):
        self.scraper.bodyStyleToCarLine = {"corvette-z06": "corvette"}  # note: mutating scraper
        carLine = "corvette"
        bodyStyle = "corvette-z06"
        modelYear = date(2022, 1, 1)
        expectedPath = "https://www.chevrolet.com/byo-vc/api/v2/trim-matrix/en/US/chevrolet/corvette/2022/corvette-z06?postalCode=94102"
        expectedMetaData = {"metadata": {"bodyStyle": bodyStyle, "carLine": carLine}}
        found = self.scraper._createModelFetchDto(bodyStyle=bodyStyle, modelName="Corvette Z06", modelYear=modelYear)
        expected = ModelFetchDto(modelName="Corvette Z06", modelCode=bodyStyle, path=expectedPath,
                                 metadata=expectedMetaData)
        self.assertEqual(expected, found)

    def test__createModelFetchDtoRaisesWhenBodyStyleMissing(self):
        self.scraper.bodyStyleToCarLine = {"notCorvette-z06": "notCorvette"}  # note: mutating scraper
        bodyStyle = "corvette-z06"
        modelYear = date(2022, 1, 1)
        raises = lambda: self.scraper._createModelFetchDto(bodyStyle=bodyStyle, modelName="Corvette Z06",
                                                           modelYear=modelYear)
        self.assertRaises(ValueError, raises)
