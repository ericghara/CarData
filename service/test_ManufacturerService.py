from unittest import TestCase
from repository.test_common.RepositorySetup import RepositorySetup
from ManufacturerService import manufacturerService
from repository.SessionFactory import sessionFactory


class TestManufacturerService(TestCase):
    res = None

    @classmethod
    def setUpClass(cls):
        cls.res = RepositorySetup()
        cls.res.start()
        cls.res.initTables()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.res.stop()

    def setUp(self) -> None:
        self.res.insetTestRecords()

    def tearDown(self) -> None:
        self.res.deleteAll()

    def test_get_manufacturer_by_common_name(self):
        with sessionFactory.newSession() as session:
            toyotaManufacturer = manufacturerService.getManufacturerByCommonName('Toyota', session)
        self.assertTrue(toyotaManufacturer)

    def test_get_all_manufacturers(self):
        with sessionFactory.newSession() as session:
            manufacturerCommonNames = [ manufacturer.common_name for manufacturer in manufacturerService.getAllManufacturers(session) ]
        self.assertEqual(['Toyota'], manufacturerCommonNames)

    def test_deleteAllManufacturers(self):
        with sessionFactory.newSession() as session:
            manufacturerService.deleteAllManufacturers(session)
            shouldBeNull = manufacturerService.getManufacturerByCommonName('Toyota', session)
            session.commit()
        self.assertIs(None, shouldBeNull)

    def test_delete_manufacturer_by_common_name(self):
        with sessionFactory.newSession() as session:
            manufacturerService.deleteManufacturerByCommonName('Toyota', session)
            shouldBeNull = manufacturerService.getManufacturerByCommonName('Toyota', session)
            session.commit()
        self.assertIs(None, shouldBeNull)

    def test_deleteManufacturerByCommonNameRaisesWhenNoRecord(self):
        with sessionFactory.newSession() as session:
            self.assertRaises(ValueError,
                              lambda: manufacturerService.deleteManufacturerByCommonName('NotToyota', session) )




