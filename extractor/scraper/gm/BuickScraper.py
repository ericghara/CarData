from datetime import date
from typing import Iterable, Dict

from extractor.scraper.common.fetchModelData import ModelFetchDto, ModelDtosAndJsonDataByName, fetchModels
from extractor.scraper.gm.GmScraper import GmScraper


class BuickScraper(GmScraper):
    BRAND_NAME = "Buick"
    DOMAIN = "https://www.buick.com"

    def __init__(self, **kwargs):
        # kwargs: noInit True/False, for testing doesn't fetch anything to initialize
        super().__init__(brandName=self.BRAND_NAME, domain=self.DOMAIN, **kwargs)

    def _getModelName(self, bodyStyle: str):
        foundModel = self.bodyStyleToName.get(bodyStyle.lower())
        if not foundModel:
            #Uses '_' between words '-' between name and 'modifier" like encore-gx
            foundModel = bodyStyle.replace("_", " ").replace("-", " ").title()
            self.log.info(f"Unable to match {bodyStyle}.  Using {foundModel}")
        return foundModel

    def _createModelFetchDtosByName(self, bodyStyles: Iterable[str], modelYear: date) -> Dict[str, ModelFetchDto]:
        if not bodyStyles:
            raise ValueError("Received an empty or null bodyStyles argument")
        dtos = dict()
        for bodyStyle in bodyStyles:
            modelName = self._getModelName(bodyStyle)
            dtos[modelName] = self._createModelFetchDto(bodyStyle=bodyStyle, modelName=modelName, modelYear=modelYear)
        return dtos

    def fetchModelYear(self, modelYear: date) -> ModelDtosAndJsonDataByName:
        self._validateModelYear(modelYear)
        bodyStyles = self._fetchBodyStyles(modelYear)
        modelFetchDtosByName = self._createModelFetchDtosByName(bodyStyles=bodyStyles, modelYear=modelYear)
        return fetchModels(modelFetchDtosByName=modelFetchDtosByName,
                           modelYear=modelYear)