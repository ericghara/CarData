from extractor.scraper.ModelInfoScraper import ModelInfoScraper
from extractor.scraper.common.fetchModelData import ModelFetchDto, fetchModels
from persister.persistModelData import persistModels
from repository.Entities import Brand
from extractor.scraper.common.HttpClient import httpClient
from datetime import date
from typing import *


class LexusScraper(ModelInfoScraper):
    URL_PREFIX = 'https://www.lexus.com/config/pub'

    # Note this is essentially the same as ToyotaScraper aside from _getModelName function
    # A decision was made to keep the code bases separate.  Their websites and formats could
    # drift apart in the future...

    def __init__(self, **kwargs):
        super().__init__(brand=Brand(name='Lexus'), kwargs=kwargs)

    def _getModelName(self, modelCode: str) -> str:
        # returns str if match and replacement made
        def stripAndReplace(matchSuffix: str, replaceSuffix: str) -> Optional[str]:
            nonlocal modelCode
            if modelCode.endswith(matchSuffix):
                return modelCode[:-1 * len(matchSuffix)] + replaceSuffix
            return None

        if len(modelCode) == 2:
            return modelCode
        matchToReplace = {'PHEV': ' PHEV', 'CV': ' Convertable', 'h': ' Hybrid', 'F': ' F', 'C': ' C'}
        for matchSuffix, replaceSuffix in matchToReplace.items():
            if (potentialName := stripAndReplace(matchSuffix, replaceSuffix)):
                return potentialName
        raise ValueError('Unable to convert the model code to a name.  Lexus possibly changed naming scheme.')

    # url to fetch data for a specific model
    # ex: https://www.lexus.com/config/pub/static/uifm/LEX/NATIONAL/EN/ebd9b27e2cb2f5e2bce935c82b4d4f23c8b83eb1/
    #           2023/IS/8579e8c9a2d17551ffd83b9016595bab206bd9fd/content.json
    def _createModelDataURL(self, subPath: str) -> str:
        if not subPath:
            raise ValueError('Received an empty or null subPath')
        return f'{self.URL_PREFIX}{subPath}/content.json'

    def _fetchModelList(self, modelYear: 'date') -> List[Dict]:
        super()._validateModelYear(modelYear)
        if (year := modelYear.year) < 2014:
            raise ValueError('year must be > 2014')
        targetURL = f'{self.URL_PREFIX}/nocache/uifm/LEX/NATIONAL/EN/{year}/bootstrap.json'
        # returns a list of models
        # example:
        # [{"featureModel":"NXh","path":"/static/uifm/LEX/NATIONAL/EN/*LONG*PATH*","archived":"false"}, ... ]
        return httpClient.getRequest(targetURL).json()

    def _parseModelList(self, modelListJson: List['Dict']) -> Dict[str, 'ModelFetchDto']:
        fetchDtoByName = dict()
        for model in modelListJson:
            modelCode = model.get('featureModel', "")
            if not modelCode:
                raise KeyError(
                    f"Model code could not be parsed.  Likely Lexus's response format has changed")
            modelName = self._getModelName(modelCode)
            subPath = model.get("path", "")
            fullPath = self._createModelDataURL(subPath)
            if modelName in fetchDtoByName:
                self.log.warning(f'Duplicate model: {modelName}, in model year!')
            fetchDtoByName[modelName] = ModelFetchDto(modelCode=modelCode, modelName=modelName, path=fullPath)
        return fetchDtoByName

    def _fetchModelYear(self, modelYear: 'date') -> dict[str, dict]:
        modelListJson = self._fetchModelList(modelYear)
        nameToModelInfo = self._parseModelList(modelListJson)
        return {modelName: httpClient.getRequest(modelInfo.path).json() for modelName, modelInfo in
                nameToModelInfo.items()}

    def persistModelYear(self, modelYear: 'date') -> None:
        modelListJson = self._fetchModelList(modelYear)
        modelFetchDtosByName = self._parseModelList(modelListJson)
        modelDtosAndJsonDataByName = fetchModels(modelFetchDtosByName=modelFetchDtosByName, brandId=self.brand.brand_id,
                                                 modelYear=modelYear)
        persistModels(modelDtos=modelDtosAndJsonDataByName.modelDtos,
                      jsonDataByName=modelDtosAndJsonDataByName.jsonDataByName)
