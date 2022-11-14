from unittest import TestCase

from testcontainers.postgres import PostgresContainer

from glbls import variables
from repository.SessionFactory import sessionFactory
from repository.Entities import entities
import repository.Entities as Entities
from service.ManufacturerService import manufacturerService


class TestModelService(TestCase):
    postgresContainer = None

    @classmethod
    def setUpClass(cls):
        cls.postgresContainer = PostgresContainer("postgres:14.4")
        cls.postgresContainer.start()
        variables.POSTGRES_URI = cls.postgresContainer.get_connection_url()
        variables.POSTGRES_USERNAME = cls.postgresContainer.POSTGRES_PASSWORD
        variables.POSTGRES_PASSWORD = cls.postgresContainer.POSTGRES_PASSWORD
        print(variables.POSTGRES_URI)
        Entities.createAll()
        entities.mapTables()
        with sessionFactory.newSession() as session:
            toyotaManufacturer = entities.Manufacturer(official_name='Toyota Moto Co', common_name='Toyota')
            manufacturerService.insertManufacturer(toyotaManufacturer, session)
            toyotaBrand = entities.Brand(name='Toyota')
            lexusBrand = entities.Brand(name='Lexus')
            toyotaManufacturer.brands.extend([toyotaBrand, lexusBrand])
            session.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.postgresContainer.stop()

    def test__get_brand(self):
        self.fail()

    def test_get_model_year(self):
        self.fail()

    def test_get_model_by_brand_name_model_name_model_year(self):
        self.fail()

    def test_get_most_recent_model(self):
        self.fail()

    def test_get_models_by_brand_name_and_model_name(self):
        self.fail()

    def test_delete_model_by_brand_name_model_name_model_year(self):
        self.fail()

    def test_upsert(self):
        self.fail()
