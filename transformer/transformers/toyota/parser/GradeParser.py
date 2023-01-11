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

    def _parseModel(self, modelJson: Dict) -> Grade:
        # Lexus: has no concept of "Standard" trim, instead the Standard model has no dealertrim
        # Toyota: the base/standard grade is usually (always?) the model name
        title = self._getGrade(modelJson) or self._getDealerTrim(modelJson) or "Standard"
        return Grade(title=title)

    def parse(self, jsonData: Dict) -> List[Grade]:
        gradeAttributeDtos = set()
        for modelJson in jsonData['model']:
            grade = self._parseModel(modelJson)
            if grade in gradeAttributeDtos:
                self.loggingTools.logDuplicateAttributeDto(transformer=type(self), attributeDto=grade)
            else:
                gradeAttributeDtos.add(grade)
        if not gradeAttributeDtos:
            self.loggingTools.logNoAttributes(self.__class__)
        return list(gradeAttributeDtos)