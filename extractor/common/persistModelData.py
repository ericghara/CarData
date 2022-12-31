import json
from typing import List, Dict

from repository.Entities import RawData
from repository.SessionFactory import sessionFactory
from repository.dto import Model as ModelDto
from service.ModelService import modelService
from service.RawDataService import rawDataService


def persistModels(modelDtos: List[ModelDto], jsonDataByName: Dict[str, Dict]) -> None:
    if not modelDtos or not jsonDataByName:
        raise ValueError("Received a null or empty input")
    diff = {model.name for model in modelDtos}.symmetric_difference(jsonDataByName.keys())
    if diff:
        raise ValueError(f"Missing model <-> jsonData relationship for modelName(s): {diff}")
    with sessionFactory.newSession() as session:
        session.begin()
        for modelEntity in modelService.upsert(modelDtos, session):
            jsonData = jsonDataByName[modelEntity.name]
            rawDataService.insert(RawData(raw_data=jsonData, model_id=modelEntity.model_id), session=session)
        session.commit()
