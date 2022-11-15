import datetime

from testcontainers.postgres import PostgresContainer

import repository.Entities
from glbls import variables
from repository.Entities import Manufacturer, Brand, Model, RawData
from repository.SessionFactory import sessionFactory
from service.ManufacturerService import  manufacturerService


class DbContainer:

    def __init__(self):
        self.postgresContainer = PostgresContainer("postgres:14.4")

    def start(self) -> None:
        self.postgresContainer.start()
        variables.POSTGRES_URI = self.postgresContainer.get_connection_url()
        variables.POSTGRES_USERNAME = self.postgresContainer.POSTGRES_PASSWORD
        variables.POSTGRES_PASSWORD = self.postgresContainer.POSTGRES_PASSWORD
        # removes stale past engine (ie bound to shutdown container from another test class)
        sessionFactory.purgeEngine()

    def stop(self) -> None:
        self.postgresContainer.stop()

    def initTables(self) -> None:
        repository.Entities.createAll()

    def insetTestRecords(self) -> None:
        with sessionFactory.newSession() as session:
            # manufacturer
            toyotaManufacturer = Manufacturer(official_name='Toyota Motor Company', common_name='Toyota')
            session.add(toyotaManufacturer)
            # brands
            toyotaBrand = Brand(name='Toyota', manufacturer=toyotaManufacturer)
            lexusBrand = Brand(name='Lexus', manufacturer=toyotaManufacturer)
            session.add_all([toyotaBrand, lexusBrand])
            # models
            camry2023 = Model(name='Camry', model_year=datetime.date(2023,1,1), brand=toyotaBrand )
            camry2022 = Model(name='Camry', model_year=datetime.date(2022, 1, 1), brand=toyotaBrand)
            camry2021 = Model(name='Camry', model_year=datetime.date(2021, 1, 1), brand=toyotaBrand)
            supra2023 = Model(name='Supra', model_year=datetime.date(2023,1,1), brand=toyotaBrand )
            supra2022 = Model(name='Supra', model_year=datetime.date(2022, 1, 1), brand=toyotaBrand)
            session.add_all([camry2023, camry2022, camry2021, supra2023, supra2022])
            # raw data
            camry2023Data = RawData(model=camry2023, raw_data={'year': 2023, 'engine': ['V6','I4']})
            camry2022Data = RawData(model=camry2022, raw_data={'year': 2022, 'engine': ['V6', 'I4']})
            camry2021Data = RawData(model=camry2021, raw_data={'year': 2021, 'engine': ['V6', 'I4']})
            supra2023Data = RawData(model=supra2023, raw_data={'year': 2023, 'engine': ['I6', 'I4']})
            supra2022Data = RawData(model=supra2022, raw_data={'year': 2022, 'engine': ['I6', 'I4']})
            session.add_all([camry2023Data, camry2022Data, camry2021Data, supra2023Data, supra2022Data])
            session.commit()

    def deleteAll(self) -> None:
        with sessionFactory.newSession() as session:
            manufacturerService.deleteAllManufacturers(session)
            session.commit()

