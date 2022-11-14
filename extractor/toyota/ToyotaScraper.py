import requests
import logging

from typing import *
from requests import Response
from sqlalchemy.exc import NoResultFound

from .. import ModelInfoScraper
from repository import SessionFactory
from repository import RawData, Model, Brand
from service import modelService


class ToyotaScraper(ModelInfoScraper):

    class ModelInfo:

        # Model codes that had to be manually matched
        MODEL_CODES = {'86':'GR 86','chr':'C-HR', 'supra':'GR Supra', "yaris" : "Yaris", "yarishatchback": "Yaris Hatchback", "priusc" : "Prius c",
                               'corollaim':'Corolla iM', 'yarisia' : 'Yaris iA', 'yarisliftback' : 'Yaris Liftback', 'priusv': 'Prius v', 'priusplugin' : 'Prius Plug-in' }

        URL_PREFIX = 'https://www.toyota.com/config/pub'

        def __init__(self, modelName: str, modelCode: str, path: str, isArchived: bool):
            self.modelName = modelName
            self.modelCode = modelCode
            self.path = path
            self.isArchived = isArchived

        def __repr__(self) -> str:
            return f'{self.modelName}, path: {self.path}, isArchived: {self.isArchived}'

    def __init__(self, brand: 'Brand'):
        super.__init__(brand)
        self.modelCodeToName = self._getModelCodeToName()

    # creates an (incomplete) mapping of model codes to names
    def _getModelCodeToName(self) -> dict:
        URL = 'https://www.toyota.com/service/tcom/series/en'
        rawCodeToName = self._getRequest(URL).json()
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


    # returns raw response text or throws if 4/5xx response
    def _getRequset(self, fullPath: str, **kwargs) -> Response:
        res = requests.get(fullPath, params=kwargs)
        if res.status_code >= 400:
            raise RuntimeError(f"received a {res.status_code} status code for: {fullPath}.")
        if not res.encoding:
            res.encoding = 'utf-8'
        return res

    def _fetchModelList(self, year: int) -> List[ModelInfo]:
        if self.modelYear < 2014:
            raise ValueError('year must be > 2014')
        targetURL = f'{self.URL_PREFIX}/nocache/uifm/TOY/NATIONAL/EN/{self.modelYear}/bootstrap.json'
        # returns a list of models
        # example:
        # [{"featureModel":"corolla","path":"/static/uifm/TOY/NATIONAL/EN/*LONG*PATH*","archived":"false"}, ... ]
        modelListRaw = self._getRequest(targetURL).json()
        modelRecords = list()
        for model in modelListRaw:
            modelCode = model.get('featureModel',"")
            isArchived = model.get('archived', None)
            if not modelCode or isArchived is None:
                raise KeyError(f"Model code and/or isArchived flag could not be parsed.  Likely Toyota's response format has changed")
            modelName = self._getModelName(modelCode)
            subPath = model.get("path", "")
            fullPath = self._createModelDataURL(subPath)
            modelRecords.append( self.ModelInfo(modelCode=modelCode, modelName=modelName, modelPath=fullPath, isArchived=isArchived  ) )

    # url to fetch data for a specific model
    # ex: https://www.toyota.com/config/pub/static/uifm/TOY/NATIONAL/EN
    #           /2a6c7dd95b5b81c1dda97a6b985eec703140fd4d/2022/priusprime/1813aacf15413225b2ee3129fe1c9770cbab8bdd/content.json
    def _createModelDataURL(self, subPath: str) -> str:
        if not subPath:
            raise ValueError('Received an empty or null subPath')
        return f'{self.URL_PREFIX}{subPath}/content.json'

    # create a dto
    def _insertModelData(self, model: Model, RawData: 'RawData') -> None:
        with SessionFactory.generate() as session:
            try:
                fetchedModel = modelService.getModelByBrandNameModelNameModelYear(
                    self.brand.name, model.name, model.model_year, session)
            except NoResultFound:





    # look into closing connection
    # revisit purpose of this is to NOT write to DB for prototyping
    def _fetchModelYear(self, date: 'date') -> List['RawData']:
        self.session.rollback()  # make sure this actually keeps data in RawData objects

    def persistModelYear(self, date: 'date') -> None:
        pass
