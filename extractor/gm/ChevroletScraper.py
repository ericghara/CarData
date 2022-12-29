import logging
from typing import Iterable, List

from extractor.common.fetchAndPersist import ModelFetchDto
from extractor.gm.GmScraper import GmScraper
from datetime import date
from extractor.common.HttpClient import httpClient

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

    def _createAllModelFetchDtos(self, bodyStyles: Iterable[str], modelYear: date) -> List[ModelFetchDto]:
        if not bodyStyles:
            raise ValueError("Received an empty or null bodyStyles argument")
        dtos = list()
        for bodyStyle in bodyStyles:
            modelName = self._getModelName(bodyStyle)
            dtos.append(self._createModelFetchDto(bodyStyle=bodyStyle, modelName=modelName, modelYear=modelYear) )
        return dtos

    def _fetchModelYear(self, modelYear: date) -> dict[str, dict]:
        bodyStyles = self._fetchBodyStyles(modelYear)
        rawDataByModelName = dict()
        for modelFetchDto in self._createAllModelFetchDtos(bodyStyles=bodyStyles, modelYear=modelYear):
            try:
                rawDataByModelName[modelFetchDto.modelName] = httpClient.getRequest(modelFetchDto.path).json()
            except RuntimeError as e:
                self.log.info(f"Unable to fetch {modelFetchDto.modelName}", e.__cause__)
        return rawDataByModelName

    def persistModelYear(self, date: 'date') -> None:
        ## remember metadata
        bodyStyles = self._fetchBodyStyles(date)


