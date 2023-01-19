import datetime
import uuid
from unittest import TestCase

from common.repository.Entities import RawData
from common.repository.SessionFactory import sessionFactory
from common.repository.test_common.DbContainer import DbContainer
from common.service.persistence.ModelService import modelService
from common.service.persistence.RawDataService import rawDataService


class TestRawDataService(TestCase):
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
        self.container.insetTestRecords()

    def tearDown(self) -> None:
        self.container.deleteAll()

    def test__getModel(self):
        with sessionFactory.newSession() as session:
            camry2023 = rawDataService._getModel(
                brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023, 1, 1), session=session)
        self.assertTrue(camry2023)

    def test__getModelRaisesWhenNoRecord(self):
        with sessionFactory.newSession() as session:
            raises = lambda: rawDataService._getModel(
                brandName='Toyota', modelName='NotCamry', modelYear=datetime.date(2023, 1, 1), session=session)
            self.assertRaises(ValueError, raises)

    def test_getMostRecentlyCreatedDataBy(self):
        with sessionFactory.newSession() as session:
            session.begin()
            data = {'id': str(uuid.uuid4())}
            rawDataService.insertDataBy(
                data=data, brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023, 1, 1), session=session)
            session.commit()
            newestRecord = rawDataService.getMostRecentlyCreated(brandName='Toyota', modelName='Camry',
                                                                 modelYear=datetime.date(2023, 1, 1), session=session)
            self.assertEqual(data['id'], newestRecord.raw_data['id'])

    def test_getByDataId(self):
        with sessionFactory.newSession() as session:
            session.begin()
            camry2023 = rawDataService._getModel(
                brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023, 1, 1), session=session)
            expected = RawData(raw_data={}, model=camry2023, model_id=uuid.uuid4())
            rawDataService.insert(rawData=expected, session=session)
            session.commit()
            found = rawDataService.getByDataId(dataId=expected.data_id, session=session)
            self.assertEqual(expected, found)

    def test_insertDataBy(self):
        with sessionFactory.newSession() as session:
            toInsert = {'id': str(uuid.uuid4())}
            rawDataService.insertDataBy(
                data=toInsert, brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023, 1, 1),
                session=session)
            newestRecord = rawDataService.getMostRecentlyCreated(brandName='Toyota', modelName='Camry',
                                                                 modelYear=datetime.date(2023, 1, 1), session=session)
            session.commit()
            self.assertEqual(toInsert['id'], newestRecord.raw_data['id'])

    def test_insertRefModelId(self):
        with sessionFactory.newSession() as session:
            model = modelService.getMostRecentModel(brandName='Toyota', modelName='Camry', session=session)
            toInsert = RawData(raw_data={}, model_id=model.model_id)
            rawDataService.insert(toInsert, session)
            session.commit()
            fetched = rawDataService.getMostRecentlyCreated(brandName='Toyota', modelName=model.name,
                                                            modelYear=model.model_year, session=session)
            self.assertEqual(toInsert, fetched)

    def test_insertRefModel(self):
        with sessionFactory.newSession() as session:
            model = modelService.getMostRecentModel(brandName='Toyota', modelName='Camry', session=session)
            toInsert = RawData(raw_data={}, model=model)
            rawDataService.insert(toInsert, session)
            session.commit()
            fetched = rawDataService.getMostRecentlyCreated(brandName='Toyota', modelName=model.name,
                                                            modelYear=model.model_year, session=session)
            self.assertEqual(toInsert, fetched)

    def test_getDataFor(self):
        with sessionFactory.newSession() as session:
            rawData = rawDataService.getDataFor(
                brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023, 1, 1), session=session)
            for dataRecord in rawData:
                # should only return 1 record
                self.assertEqual(2023, dataRecord.raw_data['year'])

    def test_deleteAllButMostRecent(self):
        with sessionFactory.newSession() as session:
            session.begin()  # w/o separate transaction for insert there's a statement visibility issue
            data = {'forTest': True}
            rawDataService.insertDataBy(
                data=data, brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023, 1, 1),
                session=session)
            session.commit()
            newestRecord = rawDataService.getMostRecentlyCreated(brandName='Toyota', modelName='Camry',
                                                                 modelYear=datetime.date(2023, 1, 1), session=session)
            rawDataService.deleteAllButMostRecent(brandName='Toyota', modelName='Camry',
                                                  modelYear=datetime.date(2023, 1, 1), session=session)
            camry2023Data = rawDataService.getDataFor(
                brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023, 1, 1), session=session)
            for record in camry2023Data:
                self.assertEqual(newestRecord.data_id, record.data_id)
            session.commit()

    def test_deleteAllButMostRecentRaisesWhenNoRecord(self):
        with sessionFactory.newSession() as session:
            raises = lambda: rawDataService.deleteAllButMostRecent(brandName='Toyota', modelName='Camry',
                                                                   modelYear=datetime.date(2080, 1, 1), session=session)
            self.assertRaises(ValueError, raises)
