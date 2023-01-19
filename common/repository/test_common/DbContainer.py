import datetime

from testcontainers.postgres import PostgresContainer

from common.domain.enum.AttributeType import AttributeType
from common.repository import Entities
from common.repository.Entities import Manufacturer, Brand, Model, RawData, ModelAttribute
from common.repository.SessionFactory import sessionFactory
from common.service.persistence.ManufacturerService import manufacturerService
from glbls import variables


class DbContainer:

    def __init__(self):
        self.postgresContainer = PostgresContainer("postgres:14.4")

    def start(self) -> None:
        self.postgresContainer.start()
        variables.POSTGRES_URI = self.postgresContainer.get_connection_url()
        variables.POSTGRES_USERNAME = self.postgresContainer.POSTGRES_PASSWORD
        variables.POSTGRES_PASSWORD = self.postgresContainer.POSTGRES_PASSWORD
        # removes stale past engine (ie bound to a shutdown container from another test class)
        sessionFactory.purgeEngine()

    def stop(self) -> None:
        sessionFactory.purgeEngine()
        self.postgresContainer.stop()

    def initTables(self) -> None:
        Entities.createAll()

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
            camry2023 = Model(name='Camry', model_year=datetime.date(2023, 1, 1), brand=toyotaBrand)
            camry2022 = Model(name='Camry', model_year=datetime.date(2022, 1, 1), brand=toyotaBrand)
            camry2021 = Model(name='Camry', model_year=datetime.date(2021, 1, 1), brand=toyotaBrand)
            supra2023 = Model(name='Supra', model_year=datetime.date(2023, 1, 1), brand=toyotaBrand)
            supra2022 = Model(name='Supra', model_year=datetime.date(2022, 1, 1), brand=toyotaBrand)
            session.add_all([camry2023, camry2022, camry2021, supra2023, supra2022])
            # raw data
            camry2023Data = RawData(model=camry2023, raw_data={'year': 2023, 'engine': ['V6', 'I4']})
            camry2022Data = RawData(model=camry2022, raw_data={'year': 2022, 'engine': ['V6', 'I4']})
            camry2021Data = RawData(model=camry2021, raw_data={'year': 2021, 'engine': ['V6', 'I4']})
            supra2023Data = RawData(model=supra2023, raw_data={'year': 2023, 'engine': ['I6', 'I4']})
            supra2022Data = RawData(model=supra2022, raw_data={'year': 2022, 'engine': ['I6', 'I4']})
            session.add_all([camry2023Data, camry2022Data, camry2021Data, supra2023Data, supra2022Data])
            # model_attribute
            camry2023Attribute0 = ModelAttribute(model=camry2023, attribute_type=AttributeType.GRADE, title="LE",
                                                 attribute_metadata={'starting_msrp': 26_220})
            camry2023Attribute1 = ModelAttribute(model=camry2023, attribute_type=AttributeType.GRADE, title="LE Hybrid",
                                                 attribute_metadata={'starting_msrp': 28_355})
            camry2023Attribute2 = ModelAttribute(model=camry2023, attribute_type=AttributeType.ENGINE,
                                                 title="2.5L 4-Cyl. Gas Engine",
                                                 attribute_metadata={'cylinders': 4})
            camry2023Attribute3 = ModelAttribute(model=camry2023, attribute_type=AttributeType.ENGINE,
                                                 title="2.5L 4-Cyl. Gas/Electric Hybrid Engine",
                                                 attribute_metadata={'cylinders': 4})
            camry2022Attribute0 = ModelAttribute(model=camry2022, attribute_type=AttributeType.GRADE, title="LE",
                                                 attribute_metadata={'starting_msrp': 26_120})
            session.add_all([camry2023Attribute0, camry2023Attribute1, camry2023Attribute2, camry2023Attribute3, camry2022Attribute0])
            session.commit()

    def deleteAll(self) -> None:
        with sessionFactory.newSession() as session:
            manufacturerService.deleteAllManufacturers(session)
            session.commit()
