import datetime
from unittest import TestCase

from repository.SessionFactory import sessionFactory
from repository.test_common.DbContainer import DbContainer
from service.BrandService import brandService
from service.ModelService import modelService
from repository.dto import Model as ModelDto


class TestModelService(TestCase):
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

    def test__getBrand(self):
        with sessionFactory.newSession() as session:
            toyotaBrand = modelService._getBrand(manufacturerCommon='toyota', brandName='toyota', session=session)
        self.assertTrue(toyotaBrand)

    def test_getModelYear(self):
        with sessionFactory.newSession() as session:
            MY2023 = modelService.getModelYear(manufacturerCommon='toyota',
                                               brandName='toyota', modelYear=datetime.date(2023, 1, 1), session=session)
        self.assertEqual(['Camry', 'Supra'], [model.name for model in MY2023])

    def test_getModelByBrandNameModelNameModelYear(self):
        with sessionFactory.newSession() as session:
            camry2023 = modelService.getModelByBrandNameModelNameModelYear(
                brandName='toyota', modelName='Camry', modelYear=datetime.date(2023, 1, 1), session=session)
        self.assertTrue(camry2023)

    def test_getMostRecentModel(self):
        with sessionFactory.newSession() as session:
            supra2023 = modelService.getMostRecentModel(brandName='toyota', modelName='Supra', session=session)
        self.assertEqual(datetime.date(2023, 1, 1), supra2023.model_year)

    def test_get_modelsByBrandNameAndModelName(self):
        with sessionFactory.newSession() as session:
            toyotaModels = modelService.getModelsByBrandNameAndModelName(brandName='toyota', modelName='Camry',
                                                                         session=session)
        self.assertEqual([2023, 2022, 2021], [model.model_year.year for model in toyotaModels])

    def test_deleteModelByBrandNameModelNameModelYear(self):
        with sessionFactory.newSession() as session:
            modelService.deleteModelByBrandNameModelNameModelYear(
                brandName='toyota', modelName='Camry', modelYear=datetime.date(2021, 1, 1), session=session)
            nullModel = modelService.getModelByBrandNameModelNameModelYear(
                brandName='toyota', modelName='Camry', modelYear=datetime.date(2021, 1, 1), session=session)
            session.commit()
        self.assertIs(None, nullModel)

    def test_deleteModelByBrandNameModelNameModelYearRaisesWhenNoRecord(self):
        with sessionFactory.newSession() as session:
            delete = lambda: modelService.deleteModelByBrandNameModelNameModelYear(
                brandName='toyota', modelName='NotCamry', modelYear=datetime.date(2021, 1, 1), session=session)
            self.assertRaises(ValueError, delete)

    def test_upsert(self):
        with sessionFactory.newSession() as session:
            toyotaBrandId = brandService.getBrandByNameAndManufacturer(
                manufacturerCommon='toyota', brandName='toyota', session=session).brand_id
            toInsert = [ModelDto(name='Prius', model_year=datetime.date(2023, 1, 1), brand_id=toyotaBrandId),
                        ModelDto(name='Corolla', model_year=datetime.date(2023, 1, 1), brand_id=toyotaBrandId)]
            inserted = modelService.upsert(toInsert, session=session)
            self.assertEqual({'Prius', 'Corolla'}, {modelDto.name for modelDto in inserted})
            session.commit()

    def test_upsertWithDuplicates(self):
        with sessionFactory.newSession() as session:
            toyotaBrandId = brandService.getBrandByNameAndManufacturer(
                manufacturerCommon='toyota', brandName='toyota', session=session).brand_id
            toInsert = [ModelDto(name='Camry', model_year=datetime.date(2023, 1, 1), brand_id=toyotaBrandId),
                        ModelDto(name='Camry', model_year=datetime.date(2022, 1, 1), brand_id=toyotaBrandId)]
            inserted = modelService.upsert(toInsert, session=session)
            self.assertEqual({2022, 2023}, {modelDto.model_year.year for modelDto in inserted})
            session.commit()
