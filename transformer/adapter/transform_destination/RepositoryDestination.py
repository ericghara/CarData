import logging
from typing import List

from common.domain.dto.AttributeDto import AttributeDto
from common.domain.dto.RawDataDto import RawDataDto
from common.repository.SessionFactory import sessionFactory
from common.service.persistence.ModelService import modelService
from transformer.adapter.TransformDestination import TransformDestination


class RepositoryDestination(TransformDestination):

    def __init__(self):
        self.log = logging.getLogger(type(self).__name__)

    def accept(self, attributes: List[AttributeDto], rawDataDto: RawDataDto) -> None:
        with sessionFactory.newSession() as session:
            modelService.getModelByModelId(modelId=rawDataDto.modelId, session=session)
