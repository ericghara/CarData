from typing import Dict, Optional, List

from common.domain.dto.AttributeDto import Transmission
from transformer.transform.AttributeParser import AttributeParser
from transformer.transform.toyota.parser.LoggingTools import LoggingTools
from transformer.transform.common import util


class TransmissionParser(AttributeParser):

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _getTitle(self, modelJson: Dict) -> Optional[str]:
        try:
            title = modelJson['transmission']['title']
        except KeyError as e:
            self.loggingTools.logTitleFailure(parser=self.__class__, exception=e, modelJson=modelJson)
            return None
        if not title:
            return None
        return util.removeBracketed(title)

    def parse(self, jsonData: Dict) -> List[Transmission]:
        transmissionAttributeDtos = set()
        for modelJson in jsonData['model']:
            if not (title := self._getTitle(modelJson)):
                continue
            if (transmission := Transmission(title=title)) in transmissionAttributeDtos:
                self.loggingTools.logDuplicateAttributeDto(parser=type(self), attributeDto=transmission)
            else:
                transmissionAttributeDtos.add(transmission)
        if not transmissionAttributeDtos:
            self.loggingTools.logNoAttributes(self.__class__)
        return list(transmissionAttributeDtos)
