from typing import Dict

from transformer.attribute_dto.AttributeDto import *
from transformer.attribute_metadata.AttributeMetadata import AttributeMetadata
from transformer.attribute_metadata.MetadataType import MetadataType
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser import util


class PackageParser:

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def parse(self, jsonData: Dict) -> List[AttributeDto]:
        packageDtos = set()
        for modelJson in jsonData['model']:
            for packageJson in modelJson.get("packages", list()):
                if title := self._getTitle(packageJson=packageJson, modelJson=modelJson):
                    metadata = list()
                    if priceMetadata := self._getPrice(packageJson=packageJson, modelJson=modelJson):
                        metadata.append(priceMetadata)
                    packageDto = Package(title=title, metadata=metadata)
                    if not packageDtos.add(packageDto):
                        self.loggingTools.logDuplicateAttributeDto(transformer=self.__class__, attributeDto=packageDto)
        return list(packageDtos)

    def _getTitle(self, packageJson: Dict, modelJson: Dict) -> Optional[str]:
        # modelJson only used for debug message
        try:
            return packageJson['package']['title']
        except KeyError as e:
            self.loggingTools.logDebug(transformer=self.__class__, modelJson=modelJson,
                                       message="Failure to extract title")
            return None

    def _getPrice(self, packageJson: Dict, modelJson: Dict) -> Optional[AttributeMetadata]:
        # modelJson only used for debug message
        metadataType = MetadataType.COMMON_MSRP
        try:
            priceStr = packageJson['package']['price']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e,
                                                 modelJson=modelJson)
            return None
        price = util.priceStrToInt(priceStr)
        return AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=price, units="$")
