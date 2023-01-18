import uuid
from datetime import date

from sqlalchemy.orm import Session

from common.domain.dto.AttributeDto import *
from common.domain.json.JsonDecoder import jsonDecoder
from common.domain.json.JsonEncoder import jsonEncoder
from common.repository.Entities import ModelAttribute, Model
from common.service.persistence.ModelService import modelService


class ModelAttributeService:

    def __init__(self):
        pass

    # Consider a converter package in domain
    def _convertModelAttributeToModelDto(self, modelAttribute: ModelAttribute) -> AttributeDto:
        metadata = None
        mapper = jsonDecoder.getMappingFunction(AttributeMetadata)
        if modelAttribute.attribute_metadata:
            metadata = [mapper(rawMetadata) for rawMetadata in modelAttribute.attribute_metadata]
        try:
            constructor = attributeTypeToAttributeDto[modelAttribute.attribute_type]
        except KeyError as e:
            raise ValueError(f"attribute_type {modelAttribute.attribute_type} has an unknown AttributeDto mapping.")
        return constructor(title=modelAttribute.title, modelId=modelAttribute.model_id, metadata=metadata,
                           updatedAt=modelAttribute.updated_at)

    def _convertAttributeDtoToModelAttribute(self, attributeDto: AttributeDto) -> ModelAttribute:
        # while unnecessary for some parameters, jsonEncoder maps AttributeDto to attribute_type
        # and encodes the metadata
        attributeDict = jsonEncoder.default(attributeDto)
        return ModelAttribute(attribute_id=attributeDict['attributeId'], attribute_type=attributeDict['attributeType'],
                              title=attributeDict['title'], model_id=attributeDict['modelId'],
                              attribute_metadata=attributeDict['attributeMetadata'], updated_at=attributeDict['updatedAt'])

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

    def getAttributesByModelIdAndType(self, modelId: uuid, attributeType: AttributeType, session: Session) -> List[
        ModelAttribute]:
        return session.query(ModelAttribute).where(ModelAttribute.model_id == modelId,
                                                   ModelAttribute.attribute_type == attributeType)

    def getAttributesByAttributeId(self, attributeIds: List['uuid'], session: Session) -> List[ModelAttribute]:
        return session.query(ModelAttribute).where(ModelAttribute.attribute_id.in_(attributeIds))


modelAttributeService = ModelAttributeService()
