from datetime import date
from typing import *
from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.orm import Session

from common.domain.entities import RawData, Model
from common.repository.ModelRepository import modelRepository


class RawDataRepository:

    def __init__(self):
        pass

    def _getModel(self, brandName: str, modelName: str, modelYear: date, session: 'Session') -> Model:
        model = modelRepository.getModelByBrandNameModelNameModelYear(brandName=brandName, modelName=modelName, modelYear=modelYear, session=session)
        if not model:
            raise ValueError(f'No record found matching brand name: {brandName} model name: {modelName} modelYear: {modelYear}')
        return model

    def getMostRecentlyCreated(self, brandName: str, modelName: str, modelYear: date, session: 'Session') -> 'RawData':
        model = self._getModel(brandName=brandName, modelName=modelName,modelYear=modelYear, session=session)
        return session.query(RawData).where(RawData.model==model).order_by(desc(RawData.created_at) ).first()

    def getByDataId(self, dataId: UUID, session: 'Session') -> RawData:
        return session.query(RawData).where(RawData.data_id==dataId).first()

    def insertDataBy(self, data: Dict, brandName: str, modelName: str, modelYear: date, session: 'Session') -> None:
        model = self._getModel(brandName=brandName, modelName=modelName, modelYear=modelYear, session=session)
        model.raw_data.append(RawData(raw_data=data, model_id=model.model_id) )

    def insert(self, rawData: 'RawData', session : 'Session') -> None:
        if not rawData.model_id and not rawData.model:
            raise ValueError('A Model ID or a Model Entity must be provided.')
        session.add(rawData)

    def getDataFor(self, brandName: str, modelName: str, modelYear:date, session: 'Session') -> Iterator['RawData']:
        return self._getModel(brandName=brandName, modelName=modelName, modelYear=modelYear, session=session).raw_data

    def deleteAllButMostRecent(self, brandName: str, modelName: str, modelYear: date, session: 'Session') -> None:
        mostRecent = self.getMostRecentlyCreated(brandName=brandName, modelName=modelName, modelYear=modelYear,
                                                 session=session)
        if not mostRecent:
            raise ValueError(f'No raw data found for brand name: {brandName}, model name: {modelName}, model year: {str(modelYear)}')
        toDel = session.query(RawData).where(RawData.model_id == mostRecent.model_id, RawData.data_id != mostRecent.data_id)
        for record in toDel:
            session.delete(record)

rawDataRepository = RawDataRepository()

