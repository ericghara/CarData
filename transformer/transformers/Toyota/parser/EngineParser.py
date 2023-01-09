from typing import Dict

from transformer.attribute_dto.AttributeDto import *
from transformer.attribute_metadata.AttributeMetadata import AttributeMetadata
from transformer.attribute_metadata.MetadataType import MetadataType
from transformer.transformers.Toyota.LoggingTools import LoggingTools


class EngineParser:

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def parse(self, jsonData: Dict) -> List[AttributeDto]:
        engineAttributeDtos = set()
        for modelJson in jsonData['model']:
            if not (title := self._getTitle(modelJson)):
                continue
            engineMetadata = list()
            for attributeMetadata in self._getCylinders(modelJson), self._getFuelType(
                    modelJson), self._getHorsepower(modelJson):
                if attributeMetadata:
                    engineMetadata.append(attributeMetadata)
            engineAttributeDtos.add(
                AttributeDto(attributeType=AttributeType.ENGINE, title=title, metadata=attributeMetadata))
        if not engineAttributeDtos:
            self.loggingTools.logNoAttributes(self.__class__)
        return list(engineAttributeDtos)

    def _getTitle(self, modelJson: Dict) -> str:
        try:
            return modelJson['engine']['title']
        except KeyError as e:
            self.loggingTools.logTitleFailure(transformer=self.__class__, exception=e, modelJson=modelJson)

    def _getCylinders(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.ENGINE_CYLINDERS
        try:
            numCylinders = modelJson['attributes']['cylinders']['value']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        return AttributeMetadata(metadataType=metadataType, value=numCylinders)

    def _getFuelType(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.ENGINE_FUEL_TYPE
        try:
            fuelType = modelJson['attributes']['fueltype']['value']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        return AttributeMetadata(metadataType=metadataType, value=fuelType)

    def _getHorsepower(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.ENGINE_HORSEPOWER
        try:
            horsePower = modelJson['attributes']['horespower']['value']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        return AttributeMetadata(metadataType=metadataType, value=horsePower)