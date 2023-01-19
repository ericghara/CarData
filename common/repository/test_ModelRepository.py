import datetime
from unittest import TestCase

from common.domain.dto.modelDto import Model as ModelDto
from common.repository.BrandRepository import brandRepository
from common.repository.ModelRepository import modelRepository
from common.repository.SessionFactory import sessionFactory
from common.repository.test_common.DbContainer import DbContainer


class TestModelRepository(TestCase):
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
            toyotaBrand = modelRepository._getBrand(manufacturerCommon='Toyota', brandName='Toyota', session=session)
        self.assertTrue(toyotaBrand)

    def test_getModelYear(self):
        with sessionFactory.newSession() as session:
            MY2023 = modelRepository.getModelYear(manufacturerCommon='Toyota',
                                                  brandName='Toyota', modelYear=datetime.date(2023, 1, 1), session=session)
        self.assertEqual(['Camry', 'Supra'], [model.name for model in MY2023])

    def test_getModelByBrandNameModelNameModelYear(self):
        with sessionFactory.newSession() as session:
            camry2023 = modelRepository.getModelByBrandNameModelNameModelYear(
                brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023, 1, 1), session=session)
        self.assertTrue(camry2023)

    def test_getModelByModelId(self):
        with sessionFactory.newSession() as session:
            expectedModel = modelRepository.getModelByBrandNameModelNameModelYear(
                brandName='Toyota', modelName='Camry', modelYear=datetime.date(2023, 1, 1), session=session)
            foundModel = modelRepository.getModelByModelId(expectedModel.model_id, session=session)
            session.flush()
            self.assertEqual(expectedModel, foundModel)

    def test_getMostRecentModel(self):
        with sessionFactory.newSession() as session:
            supra2023 = modelRepository.getMostRecentModel(brandName='Toyota', modelName='Supra', session=session)
        self.assertEqual(datetime.date(2023, 1, 1), supra2023.model_year)

    def test_get_modelsByBrandNameAndModelName(self):
        with sessionFactory.newSession() as session:
            toyotaModels = modelRepository.getModelsByBrandNameAndModelName(brandName='Toyota', modelName='Camry',
                                                                            session=session)
        self.assertEqual([2023, 2022, 2021], [model.model_year.year for model in toyotaModels])

    def test_deleteModelByBrandNameModelNameModelYear(self):
        with sessionFactory.newSession() as session:
            modelRepository.deleteModelByBrandNameModelNameModelYear(
                brandName='Toyota', modelName='Camry', modelYear=datetime.date(2021, 1, 1), session=session)
            nullModel = modelRepository.getModelByBrandNameModelNameModelYear(
                brandName='Toyota', modelName='Camry', modelYear=datetime.date(2021, 1, 1), session=session)
            session.commit()
        self.assertIs(None, nullModel)

    def test_deleteModelByBrandNameModelNameModelYearRaisesWhenNoRecord(self):
        with sessionFactory.newSession() as session:
            delete = lambda: modelRepository.deleteModelByBrandNameModelNameModelYear(
                brandName='Toyota', modelName='NotCamry', modelYear=datetime.date(2021, 1, 1), session=session)
            self.assertRaises(ValueError, delete)

    def test_upsert(self):
        with sessionFactory.newSession() as session:
            toyotaBrandId = brandRepository.getBrandByNameAndManufacturer(
                manufacturerCommon='Toyota', brandName='Toyota', session=session).brand_id
            toInsert = [ModelDto(name='Prius', model_year=datetime.date(2023, 1, 1), brand_id=toyotaBrandId),
                        ModelDto(name='Corolla', model_year=datetime.date(2023, 1, 1), brand_id=toyotaBrandId)]
            inserted = modelRepository.upsert(toInsert, session=session)
            self.assertEqual({'Prius', 'Corolla'}, {modelDto.name for modelDto in inserted})
            session.commit()

    def test_upsertWithDuplicates(self):
        with sessionFactory.newSession() as session:
            toyotaBrandId = brandRepository.getBrandByNameAndManufacturer(
                manufacturerCommon='Toyota', brandName='Toyota', session=session).brand_id
            toInsert = [ModelDto(name='Camry', model_year=datetime.date(2023, 1, 1), brand_id=toyotaBrandId),
                        ModelDto(name='Camry', model_year=datetime.date(2022, 1, 1), brand_id=toyotaBrandId)]
            inserted = modelRepository.upsert(toInsert, session=session)
            self.assertEqual({2022, 2023}, {modelDto.model_year.year for modelDto in inserted})
            session.commit()
