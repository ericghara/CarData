from typing import Dict

from transformer.attribute_dto.AttributeDto import *
from transformer.transformers.AttributeParser import AttributeParser
from transformer.transformers.toyota.LoggingTools import LoggingTools


class GradeParser(AttributeParser):

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _getGrade(self, modelJson: Dict) -> Optional[str]:
        # More common for Toyota
        try:
            return modelJson['grade']['attributes']['title']['value']
        except KeyError as e:
            self.loggingTools.logTitleFailure(transformer=self.__class__, exception=e, modelJson=modelJson)
        return None

    def _getDealerTrim(self, modelJson: Dict) -> Optional[str]:
        # more common for Lexus
        try:
            return modelJson['attributes']['dealertrim']['value']
        except KeyError as e:
            self.loggingTools.logTitleFailure(transformer=self.__class__, exception=e, modelJson=modelJson)
        return None

    def _getTitle(self, modelJson: Dict) -> Optional[str]:
        # Lexus: has no concept of "Standard" trim, instead the Standard model has no dealertrim
        # Toyota: the base/standard grade is usually (always?) the model name
        return self._getGrade(modelJson) or self._getDealerTrim(modelJson) or "Standard"

    def parse(self, jsonData: Dict) -> List[Grade]:
        gradeAttributeDtos = set()
        for modelJson in jsonData['model']:
            if not (title := self._getTitle(modelJson)):
                continue
            gradeAttributeDtos.add(Grade(title=title))
        if not gradeAttributeDtos:
            self.loggingTools.logNoAttributes(self.__class__)
        return list(gradeAttributeDtos)