from typing import Dict, List, Optional

from common.domain.dto.AttributeDto import Drive
from transformer.transformers.AttributeParser import AttributeParser
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser import util


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
            self.loggingTools.logTitleFailure(parser=self.__class__, exception=e, modelJson=modelJson)
            return None
        if not title:
            return None
        return Drive(title=util.removeBracketed(title))
