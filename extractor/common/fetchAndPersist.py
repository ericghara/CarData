import logging
from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime

from extractor.common.HttpClient import httpClient
from repository.SessionFactory import sessionFactory
from repository.dto import Model as ModelDto
from repository.Entities import RawData, Model, Brand
from typing import *

from service.ModelService import modelService
from service.RawDataService import rawDataService

ModelFetchDtoAndModelDto = namedtuple('ModelFetchDtoAndModelDto', ['modelFetchDto', 'modelDto'])
log = logging.getLogger()

@dataclass
class ModelFetchDto:

    def __init__(self, modelName: str, modelCode: str, path: str, metadata: Dict = None):
        self.modelName = modelName
        self.modelCode = modelCode
        self.metadata = metadata
        self.path = path

def _createUnsyncedModelDto(modelFetchDto: ModelFetchDto, modelYear: datetime.date, brandId: str) -> ModelDto:
    return ModelDto(name=modelFetchDto.modelName, model_year=modelYear, brand_id=brandId)

def _addMetadata(jsonData: Dict, metadata: Dict) -> None:
    """
    Mutates jsonData adding all keys from metadata into jsonData.  Similar to Dict.update() but
    raises on key conflict
    :param jsonData:
    :param metadata:
    :return:
    :raises: ValueError if a key conflict exists between jsonData and metaData (conflicts with null values ignored)
    """
    if not metadata:
        return
    for key, value in metadata.items():
        if value is not None and jsonData.get(key) is not None:
            raise KeyError(f"The jsonData already contains the key {key} with a non-null value")
        jsonData[key] = value

def _fetch(modelFetchDtosByName: Dict[str,ModelFetchDto], brandId: str, modelYear: datetime.date) -> List[ModelFetchDtoAndModelDto]:
    modelFetchAndModel = list()
    for modelName, fetchDto in modelFetchDtosByName.items():
        try:
            rawData = httpClient.getRequest(fetchDto.path).json()
        except RuntimeError as e:
            log.info(f"Unable to fetch {fetchDto.modelName}", e.__cause__)
            continue
        unsyncedModelDto = _createUnsyncedModelDto(modelFetchDto=fetchDto, modelYear=modelYear, brandId=brandId)


def fetchAndPersist(modelFetchDtosByName: Dict[str,ModelFetchDto], brandId: str, modelYear: datetime.date, **kwargs) -> Optional[List[ModelFetchDtoAndModelDto]]:
    """
    Fetches and persists model data.  Fetch parameterized by ``ModelFetchDto``.  ``brandId``, ``modelYear`` and ``modelName``
    (from ``ModelFetchDto``) used to populate ``Model`` entity.  Json fetched from ``path`` provided in ``ModelFetchDto``
    is merged with ``metadata`` from ``ModelFetchDto`` and persisted as ``RawData``
    to
    :param modelFetchDtosByName:
    :param brandId:
    :param modelYear:
    :param kwargs: ``noPersist`` : ``False`` persists to database, returns ``None``
                    ``noPersist`` : ``True`` does not persist to database returns ``List[ModelFetchDtoAndModelDto]``
    :return: ValueError if a key conflict exists between jsonData and metaData (conflicts with null values ignored)
    :raises:
    """
    modelDtos = _createUnsyncedModelDtos(modelFetchDtosByName=modelFetchDtosByName, modelYear=modelYear, brandId=brandId)
    with sessionFactory.newSession() as session:
        session.begin()
        for syncedModelDto in modelService.upsert(modelDtos, session):
            modelInfo = modelFetchDtosByName.get(syncedModelDto.name)
            jsonData = httpClient.getRequest(modelInfo.path).json()
            _addMetadata(jsonData=jsonData, metadata=modelInfo.metadata)
            rawDataService.insert(RawData(raw_data=jsonData, model_id=syncedModelDto.model_id), session=session)
        session.commit()





