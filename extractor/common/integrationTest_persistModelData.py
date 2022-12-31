import datetime
from unittest import TestCase
from uuid import uuid4

from repository.test_common.DbContainer import DbContainer
from repository.SessionFactory import sessionFactory
from repository.Entities import Manufacturer, Brand
from requests import Response
from unittest.mock import MagicMock
from extractor.common.persistModelData import persistModels
from repository.dto import Model as ModelDto

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

    def tearDown(self) -> None:
        self.container.deleteAll()

    def test_persistModels(self):
        modelYear = datetime.date(2023, 1, 1)
        modelDtos = [ModelDto(name='Camry', model_year=modelYear, brand_id=self.toyotaBrandId),
                     ModelDto(name='Supra', model_year=modelYear, brand_id=self.toyotaBrandId)]
        jsonDataByName = {"Camry": {"name": "Camry"}, "Supra": {"name": "Supra"}}
        persistModels(modelDtos=modelDtos, jsonDataByName=jsonDataByName)
        with sessionFactory.newSession() as session:
            models = modelService.getModelYear(brandName='Toyota', manufacturerCommon='Toyota', modelYear=modelYear,
                                               session=session)
            self.assertEqual({'Camry', 'Supra'}, {model.name for model in models}, "Unexpected models found")
            for model in models:
                self.assertEqual(1, len(model.raw_data),
                                 "Unexpected number of raw_data records per model")  # assert 1 record per model
                self.assertEqual(model.name, model.raw_data[0].raw_data["name"])  # assert expected json data
