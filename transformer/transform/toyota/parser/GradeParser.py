from typing import Dict, Optional, List

from common.domain.dto.AttributeDto import Grade
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.domain.attribute_set.AttributeSet import AttributeSet
from transformer.domain.attribute_set.metadata_updater.implementation.PriceUpdater import PriceUpdater
from transformer.transform.AttributeParser import AttributeParser
from transformer.transform.toyota.LoggingTools import LoggingTools
from transformer.transform.toyota.parser import util


class GradeParser(AttributeParser):

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def parse(self, jsonData: Dict) -> List[Grade]:
        gradeAttributeDtos = AttributeSet(updater=PriceUpdater(metadataType=MetadataType.COMMON_BASE_MSRP, keepLowest=True))
        for modelJson in jsonData['model']:
            grade = self._parseModel(modelJson)
            if grade in gradeAttributeDtos:
                self.loggingTools.logDuplicateAttributeDto(parser=type(self), attributeDto=grade)
            gradeAttributeDtos.add(grade)
        if not gradeAttributeDtos:
            self.loggingTools.logNoAttributes(self.__class__)
        return list(gradeAttributeDtos)

    def _getGrade(self, modelJson: Dict) -> Optional[str]:
        # More domain for Toyota
        try:
            return modelJson['grade']['attributes']['title']['value']
        except KeyError as e:
            self.loggingTools.logTitleFailure(parser=self.__class__, exception=e, modelJson=modelJson)
        return None

    def _getDealerTrim(self, modelJson: Dict) -> Optional[str]:
        # more domain for Lexus
        try:
            return modelJson['attributes']['dealertrim']['value']
        except KeyError as e:
            self.loggingTools.logTitleFailure(parser=self.__class__, exception=e, modelJson=modelJson)
        return None

    def _parseModel(self, modelJson: Dict) -> Grade:
        # Lexus: has no concept of "Standard" trim, instead the Standard model has no dealertrim
        # Toyota: the base/standard grade is usually (always?) the model name
        title = self._getGrade(modelJson) or self._getDealerTrim(modelJson) or "Standard"
        title = util.removeBracketed(title)
        optionalMSRP = self._getMSRP(modelJson)
        return Grade(title=title, metadata=[optionalMSRP] if optionalMSRP else None)

    def _getMSRP(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.COMMON_BASE_MSRP
        try:
            msrpStr = modelJson['attributes']['msrp']['value']  # ex "$101,500"
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        if not msrpStr:
            return None
        msrp = util.priceStrToInt(msrpStr)
        return AttributeMetadata(metadataType=metadataType, value=msrp, unit=MetadataUnit.DOLLARS)

