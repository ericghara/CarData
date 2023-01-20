from unittest import TestCase

from common.repository.ManufacturerRepository import manufacturerRepository
from common.repository.SessionFactory import sessionFactory
from common.repository.test_common.DbContainer import DbContainer


class TestManufacturerRepository(TestCase):
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

    def test_get_manufacturer_by_common_name(self):
        with sessionFactory.newSession() as session:
            toyotaManufacturer = manufacturerRepository.getManufacturerByCommonName('Toyota', session)
        self.assertTrue(toyotaManufacturer)

    def test_getManufacturerByManufacturerId(self):
        with sessionFactory.newSession() as session:
            expected = manufacturerRepository.getManufacturerByCommonName(commonName='Toyota', session=session)
            found = manufacturerRepository.getManufacturerById(manufacurerId=expected.manufacturer_id, session=session)
            self.assertEqual(found, expected)

    def test_get_all_manufacturers(self):
        with sessionFactory.newSession() as session:
            manufacturerCommonNames = [manufacturer.common_name for manufacturer in manufacturerRepository.getAllManufacturers(session)]
        self.assertEqual(['Toyota'], manufacturerCommonNames)

    def test_deleteAllManufacturers(self):
        with sessionFactory.newSession() as session:
            manufacturerRepository.deleteAllManufacturers(session)
            shouldBeNull = manufacturerRepository.getManufacturerByCommonName('Toyota', session)
            session.commit()
        self.assertIs(None, shouldBeNull)

    def test_delete_manufacturer_by_common_name(self):
        with sessionFactory.newSession() as session:
            manufacturerRepository.deleteManufacturerByCommonName('Toyota', session)
            shouldBeNull = manufacturerRepository.getManufacturerByCommonName('Toyota', session)
            session.commit()
        self.assertIs(None, shouldBeNull)

    def test_deleteManufacturerByCommonNameRaisesWhenNoRecord(self):
        with sessionFactory.newSession() as session:
            self.assertRaises(ValueError,
                              lambda: manufacturerRepository.deleteManufacturerByCommonName('NotToyota', session))





