import datetime
from unittest import TestCase
from uuid import uuid4

from repository.test_common.DbContainer import DbContainer
from repository.SessionFactory import sessionFactory
from repository.Entities import Manufacturer, Brand
from requests import Response
from unittest.mock import MagicMock
from extractor.common.fetchAndPersist import ModelFetchDto, fetchAndPersist
import unittest.mock as mock

from service.ModelService import modelService


class Test(TestCase):
    container = None
    toyotaBrandId = str(uuid4())

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
            toyotaBrand = Brand(name='Toyota', brand_id=self.toyotaBrandId, manufacturer=toyotaManufacturer)
            session.add(toyotaBrand)
            session.commit()
        self.httpClientResponseMock = Response()
        self.httpClientResponseMock.json = MagicMock(return_value={})
        patcher = mock.patch('extractor.common.fetchAndPersist.httpClient.getRequest',
                             return_value=self.httpClientResponseMock)
        self.httpClientMock = patcher.start()

    def tearDown(self) -> None:
        self.container.deleteAll()
        self.httpClientMock.stop()

    def test_fetch_and_persist(self):
        modelYear = datetime.date(2023, 1, 1)
        modelFetchDtosByName = {"Camry": ModelFetchDto(modelName='Camry', modelCode="", path='Camry'),
                                "Supra": ModelFetchDto(modelName='Supra', modelCode="", path='Supra')}
        fetchAndPersist(modelFetchDtosByName=modelFetchDtosByName, brandId=self.toyotaBrandId, modelYear=modelYear)
        with sessionFactory.newSession() as session:
            models = modelService.getModelYear(brandName='Toyota', manufacturerCommon='Toyota', modelYear=modelYear, session=session)
            self.assertEqual({'Camry','Supra'}, {model.name for model in models}, "Unexpected models found" )
            for model in models:
                self.assertEqual(1, len(model.raw_data), "Unexpected number of raw_data records per model" )



