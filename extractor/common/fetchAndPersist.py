from datetime import datetime

from extractor.common.HttpClient import httpClient
from repository.SessionFactory import sessionFactory
from repository.dto import Model as ModelDto
from repository.Entities import RawData, Model, Brand
from typing import *

from service.ModelService import modelService
from service.RawDataService import rawDataService


class ModelFetchDto:

    def __init__(self, modelName: str, modelCode: str, path: str):
        self.modelName = modelName
        self.modelCode = modelCode
        self.path = path

    def __repr__(self) -> str:
        return f'ModelInfo({self.modelName}, {self.modelCode}, {self.path})'

    def __eq__(self, other) -> bool:
        if type(self) is not type(other):
            return False
        return vars(self) == vars(other)

def fetchAndPersist(modelFetchDtosByName: Dict[str,ModelFetchDto], brandId: str, modelYear: datetime.date) -> None:
    modelDtos = list()
    for modelInfo in modelFetchDtosByName.values():
        modelDtos.append(
            ModelDto(name=modelInfo.modelName, model_year=modelYear, brand_id=brandId) )
    with sessionFactory.newSession() as session:
        session.begin()
        for syncedModelDto in modelService.upsert(modelDtos, session):
            modelInfo = modelFetchDtosByName.get(syncedModelDto.name)
            jsonData = httpClient.getRequest(modelInfo.path).json()
            rawDataService.insert(RawData(raw_data=jsonData, model_id=syncedModelDto.model_id), session=session)
        session.commit()





