from unittest import TestCase

from common.domain.entities import Brand
from common.repository.BrandRepository import brandRepository
from common.repository.SessionFactory import sessionFactory
from common.repository.test_common.DbContainer import DbContainer


class TestBrandRepository(TestCase):

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

    def test__getManufacturerGets(self):
        with sessionFactory.newSession() as session:
            toyotaMan = brandRepository._getManufacturer('Toyota', session)
        self.assertTrue(toyotaMan)

    def test__getManufacturerThrowsWhenNoRecord(self):
        with sessionFactory.newSession() as session:
            self.assertRaises(ValueError,
                              lambda: brandRepository._getManufacturer('NotToyota', session))

    def test_get_brand_by_name_and_manufacturer(self):
        with sessionFactory.newSession() as session:
            lexusBrand = brandRepository.getBrandByNameAndManufacturer(manufacturerCommon='Toyota', brandName='Lexus', session=session)
        self.assertTrue(lexusBrand)
        self.assertEqual('Lexus', lexusBrand.name)


    def test_getBrandByName(self):
        with sessionFactory.newSession() as session:
            lexusBrand = brandRepository.getBrandByName(brandName='Lexus', session=session)
        self.assertTrue(lexusBrand)
        self.assertEqual('Lexus', lexusBrand.name)

    def test_insertBrand(self):
        with sessionFactory.newSession() as session:
            brandRepository.insertBrand(manufacturerCommon='Toyota', brand=Brand(name='Scion'), session=session)
            scionBrand = brandRepository.getBrandByNameAndManufacturer(manufacturerCommon='Toyota', brandName='Scion', session=session)
            session.commit()
        self.assertTrue(scionBrand)

    def test_deleteBrandByName(self):
        with sessionFactory.newSession() as session:
            brandRepository.deleteBrandByName('Toyota', session)
            session.commit()
            self.assertIs(None, brandRepository.getBrandByName('Toyota', session))


    def test_deleteBrandByNameRaisesWhenNoRecord(self):
        with sessionFactory.newSession() as session:
            self.assertRaises(ValueError, lambda: brandRepository.deleteBrandByName('NotToyota', session))



