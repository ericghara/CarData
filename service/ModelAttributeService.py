import uuid
from datetime import date
from typing import List

from sqlalchemy.orm import Session

from repository.DataTypes import AttributeType
from repository.Entities import ModelAttribute, Model
from service.ModelService import modelService


class ModelAttributeService:

    def __init__(self):
        pass

    def _getModel(self, brandName: str, modelName: str, modelYear: date, session: 'Session') -> Model:
        model = modelService.getModelByBrandNameModelNameModelYear(brandName=brandName, modelName=modelName,
                                                                   modelYear=modelYear, session=session)
        if not model:
            raise ValueError(
                f'No record found matching brand name: {brandName} model name: {modelName} modelYear: {modelYear}')
        return model

    def insert(self, modelAttribute: ModelAttribute, session: Session) -> None:
        if not modelAttribute.model_id and not modelAttribute.model:
            raise ValueError('A Model ID or a Model Entity must be provided')
        session.add(modelAttribute)

    def getAttributesFor(self, brandName: str, modelName: str, modelYear: date, session: Session) -> ModelAttribute:
        return self._getModel(brandName=brandName, modelName=modelName, modelYear=modelYear,
                              session=session).model_attribute

    def getAttributeByTypeAndTitle(self, attributeType: AttributeType, title: str, modelId: uuid,
                                   session: Session) -> ModelAttribute:
        query = session.query(ModelAttribute).where(ModelAttribute.model_id == modelId,
                                                   ModelAttribute.attribute_type == attributeType,
                                                   ModelAttribute.title == title)
        return query.first()

    def getAttributesByModelId(self, modelId: uuid, session: Session) -> List[ModelAttribute]:
        return session.query(ModelAttribute).where(ModelAttribute.model_id == modelId)

    def getAttributesByModelIdAndType(self, modelId: uuid, attributeType: AttributeType, session: Session) -> List[ModelAttribute]:
        return session.query(ModelAttribute).where(ModelAttribute.model_id == modelId, ModelAttribute.attribute_type == attributeType)

    def getAttributesByAttributeId(self, attributeIds: List['uuid'], session: Session) -> List[ModelAttribute]:
        return session.query(ModelAttribute).where(ModelAttribute.attribute_id.in_(attributeIds) )


modelAttributeService = ModelAttributeService()
