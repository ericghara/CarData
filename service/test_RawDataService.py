import datetime
from unittest import TestCase

from repository.Entities import RawData
from repository.SessionFactory import sessionFactory
from repository.test_common.DbContainer import DbContainer
from service.RawDataService import rawDataService



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
                brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023,1,1), session=session)
        self.assertTrue(camry2023)

    def test__getModelRaisesWhenNoRecord(self):
        with sessionFactory.newSession() as session:
            raises = lambda: rawDataService._getModel(
                brandName='Toyota', modelName='NotCamry', modelYear=datetime.date(2023,1,1), session=session)
            self.assertRaises(ValueError, raises)

    def test_getMostRecentlyCreatedDataBy(self):
        with sessionFactory.newSession() as session:
            session.begin()
            toInsert = RawData(raw_data={'forTest':True})
            rawDataService.insertData(
                rawData=toInsert, brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023,1,1), session=session)
            session.commit()
            newestRecord = rawDataService.getMostRecentlyCreatedDataBy(
                brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023,1,1), session=session )
            self.assertEqual(toInsert.data_id, newestRecord.data_id)

    def test_insertData(self):
        with sessionFactory.newSession() as session:
            toInsert = RawData(raw_data={'forTest': True})
            rawDataService.insertData(
                rawData=toInsert, brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023, 1, 1),
                session=session)
            newestRecord = rawDataService.getMostRecentlyCreatedDataBy(
                brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023, 1, 1), session=session)
            session.commit()
            self.assertEqual(toInsert.data_id, newestRecord.data_id)

    def test_getDataFor(self):
        with sessionFactory.newSession() as session:
            rawData = rawDataService.getDataFor(
                brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023, 1, 1), session=session)
            for dataRecord in rawData:
                # should only return 1 record
                self.assertEqual(2023, dataRecord.raw_data['year'])

    def test_deleteAllButMostRecent(self):
        with sessionFactory.newSession() as session:
            session.begin() # w/o separate transaction for insert there's a statement visibility issue
            toInsert = RawData(raw_data={'forTest': True})
            rawDataService.insertData(
                rawData=toInsert, brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023, 1, 1),
                session=session)
            session.commit()
            newestRecord = rawDataService.getMostRecentlyCreatedDataBy(
                brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023, 1, 1), session=session)
            rawDataService.deleteAllButMostRecent(brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023,1,1), session=session )
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



