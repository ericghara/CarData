from typing import Dict, List, Optional

from common.domain.dto.AttributeDto import Engine
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.transform.AttributeParser import AttributeParser
from transformer.transform.toyota.parser.LoggingTools import LoggingTools
from transformer.transform.common import util


class EngineParser(AttributeParser):

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def parse(self, jsonData: Dict) -> List[Engine]:
        engineAttributeDtos = set()
        for modelJson in jsonData['model']:
            if engine := self._parseModel(modelJson):
                if engine in engineAttributeDtos:
                    self.loggingTools.logDuplicateAttributeDto(parser=type(self), attributeDto=engine)
                else:
                    engineAttributeDtos.add(engine)
        if not engineAttributeDtos:
            self.loggingTools.logNoAttributes(self.__class__)
        return list(engineAttributeDtos)

    def _parseModel(self, modelJson: Dict) -> Optional[Engine]:
        if not (title := self._getTitle(modelJson)):
            return None
        engineMetadata = list()
        for attributeMetadata in self._getCylinders(modelJson), self._getFuelType(
                modelJson), self._getHorsepower(modelJson):
            if attributeMetadata:
                engineMetadata.append(attributeMetadata)
        return Engine(title=title, metadata=engineMetadata if engineMetadata else None)

    def _getTitle(self, modelJson: Dict) -> Optional[str]:
        try:
            title = modelJson['engine']['title']
        except KeyError as e:
            self.loggingTools.logTitleFailure(parser=self.__class__, exception=e, modelJson=modelJson)
            return None
        if not title:
            return None
        return util.removeBracketed(title)

    def _getCylinders(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.ENGINE_CYLINDERS
        try:
            numCylindersStr = modelJson['attributes']['cylinders']['value']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        if numCylindersStr is None:
            return None
        numCylinders = util.digitsToInt(numCylindersStr)
        return AttributeMetadata(metadataType=metadataType, value=numCylinders)

    def _getFuelType(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.ENGINE_FUEL_TYPE
        try:
            fuelType = modelJson['attributes']['fueltype']['value']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        if fuelType is None:
            return None
        return AttributeMetadata(metadataType=metadataType, value=fuelType)

    def _getHorsepower(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.ENGINE_HORSEPOWER
        try:
            horsePowerStr = modelJson['attributes']['horsepower']['value']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        if horsePowerStr is None:
            return None
        horsePower = util.digitsToInt(horsePowerStr)
        return AttributeMetadata(metadataType=metadataType, value=horsePower, unit=MetadataUnit.HORSEPOWER)