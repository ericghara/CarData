import logging
from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from typing import *

from extractor.common.HttpClient import httpClient
from repository.dto import Model as ModelDto

log = logging.getLogger()

ModelDtosAndJsonDataByName = namedtuple('ModelDtosAndJsonDataByName', ['modelDtos', 'jsonDataByName'])


@dataclass
class ModelFetchDto:

    modelName: str
    modelCode: str
    path: str
    metadata: Dict = None

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


def _fetchJsonData(modelFetchDto: ModelFetchDto) -> Optional[Dict]:
    try:
        return httpClient.getRequest(modelFetchDto.path).json()
    except RuntimeError as e:
        log.info(f"Unable to fetch {modelFetchDto.modelName}")
        log.debug(e.__cause__)
        return None


def fetchModels(modelFetchDtosByName: Dict[str, ModelFetchDto], brandId: str,
                modelYear: datetime.date) -> ModelDtosAndJsonDataByName:
    """
    This fetches all jsonData, logging any failures.  Models for which no JSON could be retrieved are filtered.
    The json data is returned as a dict by ModelName to maintain a relationship between the model and data
    :param modelFetchDtosByName:
    :param brandId:
    :param modelYear:
    :return:
    """
    models = list()
    jsonDataByName = dict()
    for modelName, fetchDto in modelFetchDtosByName.items():
        if (jsonData := _fetchJsonData(fetchDto)) is None:
            continue
        _addMetadata(jsonData=jsonData, metadata=fetchDto.metadata)
        models.append(
            _createUnsyncedModelDto(modelFetchDto=fetchDto, modelYear=modelYear, brandId=brandId))  # unsynced model dto
        jsonDataByName[modelName] = jsonData
    return ModelDtosAndJsonDataByName(modelDtos=models, jsonDataByName=jsonDataByName)
