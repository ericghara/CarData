import logging
from typing import List

from common.domain.dto.AttributeDto import AttributeDto
from common.domain.dto.RawDataDto import RawDataDto
from common.exception.IllegalArgumentError import IllegalArgumentError
from common.exception.IllegalStateError import IllegalStateError
from common.repository.SessionFactory import sessionFactory
from common.service.persistence.ModelService import modelService
from transformer.adapter.TransformDestination import TransformDestination


class RepositoryDestination(TransformDestination):

    def __init__(self, **kwargs):
        """
        :param kwargs: ``overwriteExisting``: ``bool`` - delete and replace existing ``ModelAttributes``
        or raise on existing model attributes.
        """
        self.log = logging.getLogger(type(self).__name__)
        self.overwriteExisting = kwargs.get("overwriteExisting", False)

    def accept(self, attributes: List[AttributeDto], rawDataDto: RawDataDto) -> None:
        with sessionFactory.newSession() as session:
            model = modelService.getModelByModelId(modelId=rawDataDto.modelId, session=session)
            if not model:
                raise IllegalArgumentError(f"No model for {rawDataDto.modelId} exists")
            if model.model_attribute:
                if self.overwriteExisting:
                    model.model_attribute.clear()
                else:
                    raise IllegalStateError(f"Attributes for {model} already exist")



