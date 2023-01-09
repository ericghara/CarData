from typing import Dict

from transformer.attribute_dto.AttributeDto import *
from transformer.transformers.Toyota.LoggingTools import LoggingTools


class TransmissionParser:

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _getTitle(self, modelJson: Dict) -> Optional[str]:
        try:
            return modelJson['transmission']['title']
        except KeyError as e:
            self.loggingTools.logTitleFailure(transformer=self.__class__, exception=e, modelJson=modelJson)

    def parse(self, jsonData: Dict) -> List[AttributeDto]:
        transmissionAttributeDtos = set()
        for modelJson in jsonData['model']:
            if not (title := self._getTitle(modelJson)):
                continue
            transmissionAttributeDtos.add(AttributeDto(attributeType=AttributeType.TRANSMISSION, title=title))
        if not transmissionAttributeDtos:
            self.loggingTools.logNoAttributes(self.__class__)
        return list(transmissionAttributeDtos)