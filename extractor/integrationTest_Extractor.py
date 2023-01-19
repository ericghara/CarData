import datetime
from unittest import TestCase, mock
from unittest.mock import MagicMock

from common.domain.dto.modelDto import Model as ModelDto
from common.repository.Entities import Manufacturer, Brand
from common.repository.SessionFactory import sessionFactory
from common.repository.test_common import DbContainer
from common.service.persistence.BrandService import brandService
from common.service.persistence.ManufacturerService import manufacturerService
from common.service.persistence.ModelService import modelService
from extractor.Extractor import Extractor
from extractor.scraper.common.fetchModelData import ModelDtosAndJsonDataByName
from extractor.scraper.gm.ChevroletScraper import ChevroletScraper


class Test(TestCase):
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
        with sessionFactory.newSession() as session:
            # manufacturer
            gmManufacturer = Manufacturer(official_name='General Motors Company', common_name='GM')
            session.add(gmManufacturer)
            session.flush()
            self.manufacturerId = gmManufacturer.manufacturer_id
            session.commit()
        # Not required but ensures no fetches occur
        self.patcherHttpClient = mock.patch('extractor.scraper.gm.GmScraper.httpClient.getRequest',
                                            side_effect=RuntimeError("GmScraper tried to fetch!") )
        self.patcherHttpClient.start()
        self.scraper = ChevroletScraper(noInit=True)

    def tearDown(self) -> None:
        self.container.deleteAll()
        for patch in self.patcherHttpClient,:
            patch.stop()

    def test__createOrFetchBrandCreatesBrand(self):
        extractor = Extractor(scraper=self.scraper, noPersist=False)
        with sessionFactory.newSession() as session:
            foundBrand = brandService.getBrandByName(brandName="Chevrolet", session=session)
            self.assertEqual(self.manufacturerId, foundBrand.manufacturer.manufacturer_id)
            self.assertEqual(extractor.brandId, foundBrand.brand_id)

    def test__createOrFetchBrandFetchesBrand(self):
        with sessionFactory.newSession() as session:
            gmManufacturer = manufacturerService.getManufacturerById(manufacurerId=self.manufacturerId, session=session)
            chevroletBrand = Brand(name="Chevrolet")
            gmManufacturer.brands.append(chevroletBrand)
            session.commit()
            expectedBrandId = chevroletBrand.brand_id
        extractor = Extractor(scraper=self.scraper, noPersist=False)
        self.assertEqual(expectedBrandId, extractor.brandId)

    def test__createOrFetchBrandRaisesOnWrongManufacturer(self):
        with sessionFactory.newSession() as session:
            toyotaManufacturer = Manufacturer(official_name="toyota Motor Company", common_name='Toyota')
            session.add(toyotaManufacturer)
            chevroletBrand = Brand(name="Chevrolet")
            toyotaManufacturer.brands.append(chevroletBrand)
            session.commit()
        shouldRaise = lambda: Extractor(scraper=self.scraper, noPersist=False)
        self.assertRaises(ValueError, shouldRaise)

    def test__createOrFetchBrandRaisesOnNoManufacturer(self):
        with sessionFactory.newSession() as session:
            manufacturerService.deleteAllManufacturers(session)
            session.commit()
        shouldRaise = lambda: Extractor(scraper=self.scraper, noPersist=False)
        self.assertRaises(ValueError, shouldRaise)

    def test_extractPersist(self):
        extractor = Extractor(self.scraper)
        modelYear = datetime.date(2023, 1, 1)
        modelDtos = [ModelDto(name='Camaro', model_year=modelYear),
                     ModelDto(name='Corvette Stingray', model_year=modelYear)]
        jsonDataByName = {"Camaro": {"name": "Camaro"}, "Corvette Stingray": {"name": "Corvette Stingray"}}
        modelDtosAndJsonData = ModelDtosAndJsonDataByName(modelDtos=modelDtos, jsonDataByName=jsonDataByName)
        # Monkey patch
        self.scraper.fetchModelYear = MagicMock(return_value=modelDtosAndJsonData)
        extractor.extract(modelYear)
        with sessionFactory.newSession() as session:
            models = modelService.getModelYear(brandName='Chevrolet', manufacturerCommon='GM', modelYear=modelYear,
                                               session=session)
            self.assertEqual({'Camaro', 'Corvette Stingray'}, {model.name for model in models}, "Unexpected models found")
            for model in models:
                self.assertEqual(1, len(model.raw_data),
                                 "Unexpected number of raw_data records per model")  # assert 1 record per model
                self.assertEqual(model.name, model.raw_data[0].raw_data["name"])  # assert expected json data
