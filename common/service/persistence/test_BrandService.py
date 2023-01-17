from unittest import TestCase

from common.repository.Entities import Brand
from common.repository.SessionFactory import sessionFactory
from common.repository.test_common.DbContainer import DbContainer
from common.service.persistence.BrandService import brandService


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
            toyotaMan = brandService._getManufacturer('toyota', session)
        self.assertTrue(toyotaMan)

    def test__getManufacturerThrowsWhenNoRecord(self):
        with sessionFactory.newSession() as session:
            self.assertRaises(ValueError,
                              lambda: brandService._getManufacturer('NotToyota', session) )

    def test_get_brand_by_name_and_manufacturer(self):
        with sessionFactory.newSession() as session:
            lexusBrand = brandService.getBrandByNameAndManufacturer(manufacturerCommon='toyota', brandName='Lexus', session=session)
        self.assertTrue(lexusBrand)
        self.assertEqual('Lexus', lexusBrand.name)


    def test_getBrandByName(self):
        with sessionFactory.newSession() as session:
            lexusBrand = brandService.getBrandByName(brandName='Lexus', session=session)
        self.assertTrue(lexusBrand)
        self.assertEqual('Lexus', lexusBrand.name)

    def test_insertBrand(self):
        with sessionFactory.newSession() as session:
            brandService.insertBrand(manufacturerCommon='toyota', brand=Brand(name='Scion'), session=session)
            scionBrand = brandService.getBrandByNameAndManufacturer(manufacturerCommon='toyota', brandName='Scion', session=session)
            session.commit()
        self.assertTrue(scionBrand)

    def test_deleteBrandByName(self):
        with sessionFactory.newSession() as session:
            brandService.deleteBrandByName('toyota', session)
            session.commit()
            self.assertIs(None, brandService.getBrandByName('toyota', session))


    def test_deleteBrandByNameRaisesWhenNoRecord(self):
        with sessionFactory.newSession() as session:
            self.assertRaises(ValueError, lambda: brandService.deleteBrandByName('NotToyota', session) )



