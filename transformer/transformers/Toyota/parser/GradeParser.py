from typing import Dict

from transformer.attribute_dto.AttributeDto import *
from transformer.transformers.Toyota.LoggingTools import LoggingTools


class GradeParser:

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _getTitle(self, modelJson: Dict) -> Optional[str]:
        try:
            return modelJson['grade']['attributes']['title']['value']
        except KeyError as e:
            self.loggingTools.logTitleFailure(transformer=self.__class__, exception=e, modelJson=modelJson)

    def parse(self, jsonData: Dict) -> List[AttributeDto]:
        gradeAttributeDtos = set()
        for modelJson in jsonData['model']:
            if not (title := self._getTitle(modelJson)):
                continue
            gradeAttributeDtos.add(AttributeDto(attributeType=AttributeType.GRADE, title=title))
        if not gradeAttributeDtos:
            self.loggingTools.logNoAttributes(self.__class__)
        return list(gradeAttributeDtos)