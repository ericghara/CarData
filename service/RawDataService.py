from sqlalchemy.orm import Session
from sqlalchemy import desc

from repository.Entities import RawData
from service.ModelService import modelService
from typing import *

class RawDataService:

    def __init__(self):
        pass

    def _getModel(self, brandName: str, modelName: str, modelYear: str, session: 'Session'):
        model = modelService.getModelByBrandNameModelNameModelYear(brandName=brandName, modelName=modelName,modelYear=modelYear, session=session)
        if not model:
            raise ValueError(f'No record found matching brand name: {brandName} model name: {modelName} modelYear: {modelYear}')
        return model

    def getMostRecentlyCreatedDataBy(self, brandName: str, modelName: str, modelYear: str, session: 'Session') -> 'RawData':
        model = self._getModel(brandName=brandName, modelName=modelName,modelYear=modelYear, session=session)
        return session.query(RawData).where(RawData.model==model).order_by(desc(RawData.created_at) ).first()

    def insertData(self, rawData: 'RawData', brandName: str, modelName: str, modelYear: str, session: 'Session') -> None:
        model = self._getModel(brandName=brandName, modelName=modelName, modelYear=modelYear, session=session)
        model.raw_data.append(rawData)

    def getDataFor(self, brandName: str, modelName: str, modelYear:str, session: 'Session') -> Iterator['RawData']:
        return self._getModel(brandName=brandName, modelName=modelName, modelYear=modelYear, session=session).raw_data

    def deleteAllButMostRecent(self, brandName: str, modelName: str, modelYear: str, session: 'Session') -> None:
        mostRecent = self.getMostRecentlyCreatedDataBy(brandName=brandName, modelName=modelName, modelYear=modelYear, session=session)
        toDel = session.query(RawData).where(RawData.model_id == mostRecent.model_id, RawData.data_id != mostRecent.data_id)
        session.delete(toDel)

rawDataService = RawDataService()

