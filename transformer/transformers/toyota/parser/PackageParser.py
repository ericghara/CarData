from typing import Dict, Iterable

from transformer.common.dto import AttributeMetadata
from transformer.common.enum.MetadataType import MetadataType
from transformer.common.enum.MetadataUnit import MetadataUnit
from transformer.transformers.AttributeParser import AttributeParser
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser import util


class PackageParser(AttributeParser):

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def parse(self, jsonData: Dict) -> List[Package]:
        packages = set()
        for modelJson in jsonData['model']:
            for package in self._parseModel(modelJson):
                if not package:
                    continue
                if package in packages:
                    self.loggingTools.logDuplicateAttributeDto(
                        parser=self.__class__, attributeDto=package)
                else:
                    packages.add(package)
        return list(packages)

    def _parseModel(self, modelJson: Dict) -> Iterable[Package]:
        for packageJson in modelJson.get("packages", list()):
            if title := self._getTitle(packageJson=packageJson, modelJson=modelJson):
                metadata = list()
                if priceMetadata := self._getPrice(packageJson=packageJson, modelJson=modelJson):
                    metadata.append(priceMetadata)
                yield Package(title=title, metadata=metadata)

    def _getTitle(self, packageJson: Dict, modelJson: Dict) -> Optional[str]:
        # modelJson only used for debug message
        try:
            return packageJson['title']
        except KeyError as e:
            self.loggingTools.logDebug(parser=self.__class__, modelJson=modelJson,
                                       message="Failure to extract title")
            return None

    def _getPrice(self, packageJson: Dict, modelJson: Dict) -> Optional[AttributeMetadata]:
        # modelJson only used for debug message
        metadataType = MetadataType.COMMON_MSRP
        try:
            priceStr = packageJson['price']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e,
                                                 modelJson=modelJson)
            return None
        if not priceStr:
            return None
        price = util.priceStrToInt(priceStr)
        return AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=price, unit=MetadataUnit.DOLLARS)
