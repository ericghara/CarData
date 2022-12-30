from unittest import TestCase, mock
from datetime import date
from unittest.mock import MagicMock, ANY, Mock

from parameterized import parameterized

from extractor.common.fetchModelData import ModelFetchDto
from extractor.gm.ChevroletScraper import ChevroletScraper
from repository.Entities import Brand, Manufacturer
from repository.SessionFactory import sessionFactory
from repository.test_common.DbContainer import DbContainer
from repository.test_common.mockSessionFactory import MockSessionFactory
from uuid import uuid4
from requests import Response

from service.ModelService import modelService
from service.RawDataService import rawDataService


class TestChevroletScraper(TestCase):

    def setUp(self) -> None:
        self.brand = Brand(brand_id=uuid4(), manufacturer_id=uuid4(), name='General Motors')
        self.sessionFactoryMock = MockSessionFactory()
        self.httpClientResponseMock = Response()
        self.httpClientResponseMock.json = MagicMock(return_value={})
        self.patcherHttpClient = mock.patch('extractor.gm.GmScraper.httpClient.getRequest',
                                            return_value=self.httpClientResponseMock)
        self.httpClientMock = self.patcherHttpClient.start()
        self.scraper = ChevroletScraper(noInit=True, noPersist=True)

    def tearDown(self) -> None:
        for mockObj in self.patcherHttpClient,:
            if mockObj:
                mockObj.stop()
        self.scraper = None

    def test__createAllModelFetchDtos(self):
        bodyStyles = ["corvette-z06"]
        self.scraper.bodyStyleToCarLine = {"corvette-z06": "corvette"}  # note: mutating scraper
        self.scraper.bodyStyleToName = {"corvette-z06": "Corvette Z06"}
        carLine = "corvette"
        bodyStyle = "corvette-z06"
        modelName = "Corvette Z06"
        modelYear = date(2022, 1, 1)
        expectedPath = "https://www.chevrolet.com/byo-vc/services/fullyConfigured/US/en/chevrolet/2023/corvette/corvette-z06?postalCode=94102&region=na"
        expectedMetaData = {"metadata": {"bodyStyle": bodyStyle, "carLine": carLine}}
        expected = {modelName : ModelFetchDto(modelName=modelName, modelCode=carLine, path=expectedPath,
                                  metadata=expectedMetaData)}
        self.assertEqual(expected, self.scraper._createModelFetchDtosByName(bodyStyles=bodyStyles, modelYear=modelYear))

    @parameterized.expand([ ("blazer", "Blazer"),
                            ('bolt-euv', 'Bolt EUV'),
                            ('bolt-ev', 'Bolt EV'),
                            ('camaro', 'Camaro'),
                            ('colorado', 'Colorado'),
                            ('corvette', 'Corvette Stingray'),
                            ('corvette-z06', 'Corvette Z06'),
                            ('equinox', 'Equinox'),
                            ('express-cargo', 'Express Cargo'),
                            ('express-passenger', 'Express Passenger'),
                            ('malibu', 'Malibu'),
                            ('silverado-1500', 'Silverado 1500'),
                            ('silverado-2500hd', 'Silverado 2500 HD'),
                            ('silverado-3500hd', 'Silverado 3500 HD'),
                            ('suburban-1500', 'Suburban'),
                            ('tahoe', 'Tahoe'),
                            ('trailblazer', 'Trailblazer'),
                            ('traverse', 'Traverse') ] )
    # this test cannot be run individually with pycharm (bug), must run whole class
    def test__getModelName(self, bodyStyle, expectedModelName):
        # the bodyStyles below are irregular and rely on a properly fetched bodyStyleToName map
        self.scraper.bodyStyleToName = {"corvette" : "Corvette Stingray", "suburban-1500" : "Suburban"}
        self.assertEqual(expectedModelName, self.scraper._getModelName(bodyStyle) )

class IntegrationTestChevroletScraper(TestCase):
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
            GmManufacturer = Manufacturer(official_name='General Motors Company', common_name='General Motors')
            session.add(GmManufacturer)
            chevroletBrand = Brand(name='Chevrolet', manufacturer=GmManufacturer)
            session.add(chevroletBrand)
            session.commit()
        self.httpClientResponseMock = Response()
        self.httpClientResponseMock.json = MagicMock(return_value={})
        patcher = mock.patch('extractor.common.fetchModelData.httpClient.getRequest',
                             return_value=self.httpClientResponseMock)
        self.httpClientMock = patcher.start()
        self.scraper = ChevroletScraper(noInit=True)

    def tearDown(self) -> None:
        self.container.deleteAll()
        self.httpClientMock.stop()

    def test_persist_model_year(self):
        modelYear = date(2023, 1, 1)
        # monkey patch for _fetchBodyStyles()
        self.scraper._fetchBodyStyles = MagicMock(return_value=['Corvette Stingray', 'Corvette Z06'])
        # monkey patch for _createModelFetchDtosByName()
        modelFetchDtosByName = {'Corvette Stingray': ModelFetchDto('Corvette Stingray', 'corvette', 'http://chevrolet.com/content.json' ),
                           'Corvette Z06': ModelFetchDto('Corvette Z06', 'corvette-z06', 'http://chevrolet.com/content.json' ) }
        self.scraper._createModelFetchDtosByName = MagicMock(return_value=modelFetchDtosByName)
        # Return value for fetched JSON data
        rawJson = {'Dummy_JSON': True}
        self.httpClientResponseMock.json = MagicMock(return_value=rawJson)
        self.scraper.persistModelYear(modelYear)
        with sessionFactory.newSession() as session:
            models = modelService.getModelYear(modelYear=modelYear, manufacturerCommon='Toyota', session=session,
                                               brandName=self.scraper.brand.name)
            for model in models:
                self.assertIn(model.name, self.scraper._fetchBodyStyles.return_value)
                self.assertEqual(rawJson, rawDataService.getMostRecentlyCreated(brandName=self.scraper.brand.name,
                                                                                modelName=model.name,
                                                                                modelYear=modelYear,
                                                                                session=session).raw_data)



