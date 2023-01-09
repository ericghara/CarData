from typing import Dict

from transformer.attribute_dto.AttributeDto import *
from transformer.attribute_metadata.AttributeMetadata import AttributeMetadata
from transformer.attribute_metadata.MetadataType import MetadataType
from transformer.transformers.Toyota.LoggingTools import LoggingTools


class DriveParser:

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def parse(self, jsonData: Dict) -> List[AttributeDto]:
        driveDtos = set()
        for modelJson in jsonData['model']:
            if title := self._getTitle(modelJson):
                driveDtos.add(Drive(title=title))
        return list(driveDtos)

    def _getTitle(self, modelJson: Dict) -> Optional[str]:
        try:
            return modelJson['drive']['title']
        except KeyError as e:
            self.loggingTools.logTitleFailure(transformer=self.__class__, exception=e, modelJson=modelJson)
            return None
