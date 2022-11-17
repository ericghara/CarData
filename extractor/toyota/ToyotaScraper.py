import datetime
import logging
from typing import *
from extractor.common.fetchAndPersist import fetchAndPersist, ModelFetchDto

from sqlalchemy.exc import NoResultFound

from extractor.ModelInfoScraper import ModelInfoScraper
from extractor.common.HttpClient import httpClient
from repository import SessionFactory
from repository.Entities import RawData, Model, Brand
from repository.SessionFactory import sessionFactory
from repository.dto import Model as ModelDto
from service.ModelService import modelService
from service.RawDataService import rawDataService


class ToyotaScraper(ModelInfoScraper):
    # Constructor
    #   - _getModelCodeToName
    # persistModelYear
    #  - _fetchModelList
    #       > _getModelName
    #       > modelService.upsert
    #       > _createModelDataUrl
    # _insertModeldata


    # Model codes that had to be manually matched
    MODEL_CODES = {'86': 'GR 86', 'chr': 'C-HR', 'supra': 'GR Supra', "yaris": "Yaris",
                   "yarishatchback": "Yaris Hatchback", "priusc": "Prius c",
                   'corollaim': 'Corolla iM', 'yarisia': 'Yaris iA', 'yarisliftback': 'Yaris Liftback',
                   'priusv': 'Prius v', 'priusplugin': 'Prius Plug-in', 'sequoiahybrid' : 'Sequoia Hybrid'}

    URL_PREFIX = 'https://www.toyota.com/config/pub'

    # kwargs:
    #   - noPersist: True/False
    #       for testing, don't check that provided brand is a valid db record
    def __init__(self, **kwargs):
        super().__init__(Brand(name='Toyota'), **kwargs)
        self.modelCodeToName = self._getModelCodeToName()

    # creates an (incomplete) mapping of model codes to names
    def _getModelCodeToName(self) -> dict:
        URL = 'https://www.toyota.com/service/tcom/series/en'
        rawCodeToName = httpClient.getRequest(URL).json()
        modelCodeToName = dict()
        for model in rawCodeToName:
            name = model['modelName']
            code = model['modelCode']
            modelCodeToName[code] = name
        return modelCodeToName

    def _getModelName(self, modelCode: str) -> str:
        try:
            modelName = self.modelCodeToName[modelCode]
            logging.debug(f"Found model code ({modelCode}) in modelCodeToName.")
        except KeyError:
            if modelCode in self.MODEL_CODES:
                modelName = self.MODEL_CODES[modelCode]
                logging.debug(f"Found model code ({modelCode}) in MODEL_CODES.")
            else:
                modelName = modelCode.capitalize()
                logging.info(f"Couldn't match model code: {modelCode} using {modelName}.")
        return modelName

    def _fetchModelList(self, modelYear: 'datetime.date') -> List[Dict]:
        super()._validateModelYear(modelYear)
        if (year := modelYear.year) < 2014:
            raise ValueError('year must be > 2014')
        targetURL = f'{self.URL_PREFIX}/nocache/uifm/TOY/NATIONAL/EN/{year}/bootstrap.json'
        # returns a list of models
        # example:
        # [{"featureModel":"corolla","path":"/static/uifm/TOY/NATIONAL/EN/*LONG*PATH*","archived":"false"}, ... ]
        return httpClient.getRequest(targetURL).json()

    def _parseModelList(self, modelListJson: List['Dict']) -> Dict[str, 'ModelFetchDto']:
        fetchDtoByName = dict()
        for model in modelListJson:
            modelCode = model.get('featureModel', "")
            if not modelCode:
                raise KeyError(
                    f"Model code could not be parsed.  Likely Toyota's response format has changed")
            modelName = self._getModelName(modelCode)
            subPath = model.get("path", "")
            fullPath = self._createModelDataURL(subPath)
            if modelName in fetchDtoByName:
                logging.warning(f'Duplicate model: {modelName}, in model year!')
            fetchDtoByName[modelName] = ModelFetchDto(modelCode=modelCode, modelName=modelName, path=fullPath)
        return fetchDtoByName

    # url to fetch data for a specific model
    # ex: https://www.toyota.com/config/pub/static/uifm/TOY/NATIONAL/EN
    #           /2a6c7dd95b5b81c1dda97a6b985eec703140fd4d/2022/priusprime/1813aacf15413225b2ee3129fe1c9770cbab8bdd/content.json
    def _createModelDataURL(self, subPath: str) -> str:
        if not subPath:
            raise ValueError('Received an empty or null subPath')
        return f'{self.URL_PREFIX}{subPath}/content.json'

    # Fetches raw data for a model year without persisting
    # For testing and to perform a general "dry run"
    # A map of the model name to raw data json is returned
    def _fetchModelYear(self, modelYear: 'datetime.date') -> dict[str, dict]:
        modelListJson = self._fetchModelList(modelYear)
        nameToModelInfo = self._parseModelList(modelListJson)
        return {modelName: httpClient.getRequest(modelInfo.path).json() for modelName, modelInfo in
                nameToModelInfo.items()}

    def persistModelYear(self, modelYear: 'datetime.date') -> None:
        modelListJson = self._fetchModelList(modelYear)
        modelFetchDtosByName = self._parseModelList(modelListJson)
        fetchAndPersist(modelFetchDtosByName=modelFetchDtosByName, brandId=self.brand.brand_id, modelYear=modelYear)




