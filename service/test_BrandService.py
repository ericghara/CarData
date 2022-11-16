from unittest import TestCase

from repository.Entities import Brand
from repository.test_common.DbContainer import DbContainer
from repository.SessionFactory import sessionFactory
from service.BrandService import brandService


class TestBrandService(TestCase):

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
            toyotaMan = brandService._getManufacturer('Toyota', session)
        self.assertTrue(toyotaMan)

    def test__getManufacturerThrowsWhenNoRecord(self):
        with sessionFactory.newSession() as session:
            self.assertRaises(ValueError,
                              lambda: brandService._getManufacturer('NotToyota', session) )

    def test_get_brand_by_name_and_manufacturer(self):
        with sessionFactory.newSession() as session:
            lexusBrand = brandService.getBrandByNameAndManufacturer(manufacturerCommon='Toyota', brandName='Lexus', session=session)
        self.assertTrue(lexusBrand)
        self.assertEqual('Lexus', lexusBrand.name)


    def test_getBrandByName(self):
        with sessionFactory.newSession() as session:
            lexusBrand = brandService.getBrandByName(brandName='Lexus', session=session)
        self.assertTrue(lexusBrand)
        self.assertEqual('Lexus', lexusBrand.name)

    def test_insertBrand(self):
        with sessionFactory.newSession() as session:
            brandService.insertBrand(manufacturerCommon='Toyota', brand=Brand(name='Scion'), session=session)
            scionBrand = brandService.getBrandByNameAndManufacturer(manufacturerCommon='Toyota', brandName='Scion', session=session)
            session.commit()
        self.assertTrue(scionBrand)

    def test_deleteBrandByName(self):
        with sessionFactory.newSession() as session:
            brandService.deleteBrandByName('Toyota', session)
            session.commit()
            self.assertIs(None, brandService.getBrandByName('Toyota', session))


    def test_deleteBrandByNameRaisesWhenNoRecord(self):
        with sessionFactory.newSession() as session:
            self.assertRaises(ValueError, lambda: brandService.deleteBrandByName('NotToyota', session) )



