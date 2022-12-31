from typing import Iterable, Dict

from extractor.scraper.common.fetchModelData import ModelFetchDto, fetchModels, ModelDtosAndJsonDataByName
from persister.persistModelData import persistModels
from extractor.scraper.gm.GmScraper import GmScraper
from datetime import date


class ChevroletScraper(GmScraper):

    BRAND_NAME = 'chevrolet'
    DOMAIN = 'https://www.chevrolet.com'

    def __init__(self, **kwargs):
        # kwargs: noInit True/False, for testing doesn't fetch anything to initialize
        # noPersist: does not look-up database entry for brand
        super().__init__(brandName=self.BRAND_NAME, domain=self.DOMAIN, **kwargs )

    def _getModelName(self, bodyStyle: str) -> str:
        if (foundModel := self.bodyStyleToName.get(bodyStyle.lower())):
            return foundModel
        # else branch really shouldn't be used much, it's just to provide some
        # fault tolerance.  Commercial vehicles like Express are the most likely
        # to not be found in bodyStyleToName
        else:
            nameElems = bodyStyle.split("-")
            suffix = []
            if nameElems[-1] in frozenset(["ev", "euv"]):
                suffix.append(nameElems.pop().upper())
            elif nameElems[-1].endswith("hd"): # for cases like silverado-2500hd
                nameElems[-1] = nameElems[-1][:-2]
                suffix.append("HD")
            nameElems = [elem.capitalize() for elem in nameElems]
            self.log.info(f"Could not locate {bodyStyle}. Using model name {bodyStyle}")
            return " ".join(nameElems+suffix)

    def _createModelFetchDtosByName(self, bodyStyles: Iterable[str], modelYear: date) -> Dict[str, ModelFetchDto]:
        if not bodyStyles:
            raise ValueError("Received an empty or null bodyStyles argument")
        dtos = dict()
        for bodyStyle in bodyStyles:
            modelName = self._getModelName(bodyStyle)
            dtos[modelName] = self._createModelFetchDto(bodyStyle=bodyStyle, modelName=modelName, modelYear=modelYear)
        return dtos

    def _fetchModelYear(self, modelYear: date) -> ModelDtosAndJsonDataByName:
        bodyStyles = self._fetchBodyStyles(modelYear)
        modelFetchDtosByName = self._createModelFetchDtosByName(bodyStyles=bodyStyles, modelYear=modelYear)
        return fetchModels(modelFetchDtosByName=modelFetchDtosByName, brandId=self.brand.brand_id,
                                                 modelYear=modelYear)

    def persistModelYear(self, modelYear: date) -> None:
        modelDtosAndJsonDataByName = self._fetchModelYear(modelYear)
        persistModels(modelDtos=modelDtosAndJsonDataByName.modelDtos,
                      jsonDataByName=modelDtosAndJsonDataByName.jsonDataByName)


