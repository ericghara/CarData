import logging
from typing import List

from common.domain.converter.Converter import converter
from common.domain.dto.AttributeDto import AttributeDto
from common.domain.dto.RawDataDto import RawDataDto
from common.domain.entities import ModelAttribute
from common.exception.IllegalArgumentError import IllegalArgumentError
from common.exception.IllegalStateError import IllegalStateError
from common.repository.ModelRepository import modelRepository
from common.repository.SessionFactory import sessionFactory
from transformer.adapter.TransformDestination import TransformDestination


class RepositoryDestination(TransformDestination):

    def __init__(self, **kwargs):
        """
        :param kwargs: ``overwriteExisting``: ``bool`` - delete and replace existing ``ModelAttributes``
        or raise on existing model attributes.
        """
        self.log = logging.getLogger(type(self).__name__)
        self.overwriteExisting = kwargs.get("overwriteExisting", False)

    def accept(self, attributeDtos: List[AttributeDto], rawDataDto: RawDataDto) -> None:
        attributes = [converter.convert(obj=attributeDto, outputType=ModelAttribute) for attributeDto in attributeDtos]
        with sessionFactory.newSession() as session:
            model = modelRepository.getModelByModelId(modelId=rawDataDto.modelId, session=session)
            if not model:
                raise IllegalArgumentError(f"No model for {rawDataDto.modelId} exists")
            if model.model_attribute and not self.overwriteExisting:
                raise IllegalStateError(f"Attributes for {model} already exist")
            model.model_attribute = attributes
            session.commit()
