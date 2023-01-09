import logging
from datetime import date
from typing import List, Dict, Optional
from uuid import UUID

from extractor.scraper.ModelInfoScraper import ModelInfoScraper
from extractor.scraper.common.fetchModelData import ModelDtosAndJsonDataByName
from repository.Entities import RawData, Brand
from repository.SessionFactory import sessionFactory
from repository.dto import Model as ModelDto
from service.BrandService import brandService
from service.ManufacturerService import manufacturerService
from service.ModelService import modelService
from service.RawDataService import rawDataService


class Extractor:

    def __init__(self, scraper: ModelInfoScraper, **kwargs):
        self.log = logging.getLogger(self.__class__.__name__)
        self.scraper = scraper
        self.brandId = self._createOrFetchBrand(noPersist=kwargs.get("noPersist", False) )

    def _createOrFetchBrand(self, noPersist: bool) -> Optional[UUID]:
        if noPersist: # for testing
            return None
        manufacturerCommon = self.scraper.getManufacturerCommon()
        brandName = self.scraper.getBrandName()
        with sessionFactory.newSession() as session:
            fetchedBrand = brandService.getBrandByName(brandName=brandName, session=session)
            if not fetchedBrand:  # create brand
                self.log.info(
                    f"Creating brand {self.scraper.getBrandName()} for manufacturer {self.scraper.getManufacturerCommon()}")
                manufacturer = manufacturerService.getManufacturerByCommonName(commonName=manufacturerCommon, session=session)
                if not manufacturer:
                    raise ValueError(f"Common name {manufacturerCommon} does not match any manufacturers")
                fetchedBrand = Brand(name=brandName)
                manufacturer.brands.append(fetchedBrand)
                session.commit()
            elif (foundManufacturer := fetchedBrand.manufacturer.common_name) != manufacturerCommon:
                raise ValueError(
                    f"A record for Brand {brandName} exists, but the found manufacturer was {foundManufacturer} not {manufacturerCommon}")
            return fetchedBrand.brand_id

    def _persistModels(self, modelDtos: List[ModelDto], jsonDataByName: Dict[str, Dict]) -> None:
        if not modelDtos or not jsonDataByName:
            raise ValueError("Received a null or empty input")
        modelNames = set()
        for modelDto in modelDtos:
            modelNames.add(modelDto.name)
            modelDto.brand_id = self.brandId
        if (diff := modelNames.symmetric_difference(jsonDataByName.keys()) ):
            raise ValueError(f"Missing model <-> jsonData relationship for modelName(s): {diff}")
        with sessionFactory.newSession() as session:
            session.begin()
            for modelEntity in modelService.upsert(modelDtos, session):
                jsonData = jsonDataByName[modelEntity.name]
                rawDataService.insert(RawData(raw_data=jsonData, model_id=modelEntity.model_id), session=session)
            session.commit()

    def extract(self, modelYear: date, persist: bool = True) -> Optional[ModelDtosAndJsonDataByName]:
        """
        Use the ``ModelInfoScraper`` provided by the constructor to fetch model info from a provided time period
        (``modelYear``). The option to perform a *dry-run* without writing to the database is provided by the
        optional ``persist`` parameter
        :param modelYear: Date used to reprsent the model line, typically a model year so expected date is
        yyyy-1-1 but allows for atypical release cycles (i.e. semi-annually yyyy-6-1)
        :param persist: ``True`` (*default*) will write to DB and return ``None``, ``False`` will not write to DB
        and will return fetched data as ``ModelDtosAndJsonDataByName`` object
        :return: ``None`` or ``ModelDtosAndJsonDataByName`` *(see persist parameter)*
        """
        modelDtosAndJsonDataByName = self.scraper.fetchModelYear(modelYear)
        if not persist:
            return modelDtosAndJsonDataByName
        if not (modelDtos := modelDtosAndJsonDataByName.modelDtos):
            self.log.info(f"No models retrieved for brand: {self.scraper.getBrandName()} year {modelYear}")
        self._persistModels(modelDtos=modelDtos,
                            jsonDataByName=modelDtosAndJsonDataByName.jsonDataByName)
