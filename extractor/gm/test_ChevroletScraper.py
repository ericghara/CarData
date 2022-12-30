from unittest import TestCase, mock
from datetime import date
from unittest.mock import MagicMock, ANY, Mock

from parameterized import parameterized

from extractor.common.fetchModelData import ModelFetchDto
from extractor.gm.ChevroletScraper import ChevroletScraper
from repository.Entities import Brand
from repository.test_common.mockSessionFactory import MockSessionFactory
from uuid import uuid4
from requests import Response


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
        modelYear = date(2022, 1, 1)
        expectedPath = "https://www.chevrolet.com/byo-vc/services/fullyConfigured/US/en/chevrolet/2023/corvette/corvette-z06?postalCode=94102&region=na"
        expectedMetaData = {"metadata": {"bodyStyle": bodyStyle, "carLine": carLine}}
        expected = [ModelFetchDto(modelName="Corvette Z06", modelCode=carLine, path=expectedPath,
                                  metadata=expectedMetaData)]
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
