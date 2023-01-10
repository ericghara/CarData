from typing import Dict

from transformer.attribute_dto.AttributeDto import *
from transformer.transformers.AttributeParser import AttributeParser
from transformer.transformers.toyota.LoggingTools import LoggingTools


class DriveParser(AttributeParser):

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def parse(self, jsonData: Dict) -> List[Drive]:
        driveDtos = set()
        for modelJson in jsonData['model']:
            if driveDto := self._getDrive(modelJson):
                driveDtos.add(driveDto)
        return list(driveDtos)

    def _getDrive(self, modelJson: Dict) -> Optional[Drive]:
        try:
            title = modelJson['drive']['title']
        except KeyError as e:
            self.loggingTools.logTitleFailure(transformer=self.__class__, exception=e, modelJson=modelJson)
            return None
        if title:
            return Drive(title=title)
        return None
