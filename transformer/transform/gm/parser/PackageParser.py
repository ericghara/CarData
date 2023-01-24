from typing import Dict, List, Optional

from common.domain.dto.AttributeDto import Package
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.domain.attribute_set.AttributeSet import AttributeSet
from transformer.domain.attribute_set.metadata_updater.implementation.PriceUpdater import PriceUpdater
from transformer.transform.AttributeParser import AttributeParser
from transformer.transform.common import util
from transformer.transform.gm.parser.LoggingTools import LoggingTools


class PackageParser(AttributeParser):

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _getPackageDicts(self, dataDict: Dict, modelIdentifier: str) -> List[Dict]:
        try:
            packages = dataDict['config']['OPTIONS']['PACKAGES']['more']
            if type(packages) is not list:
                raise TypeError(f"Expected list but found: {type(packages)}")
        except (KeyError, TypeError) as e:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier, exception=e)
            return list()
        return packages

    def _getPrice(self, packageDict: Dict, modelIdentifier: str) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.COMMON_MSRP
        rawPrice = packageDict.get('msrp', None)
        try:
            if rawPrice is None or (price := util.digitsToInt(rawPrice)) is None:
                raise ValueError(f"Un-parsable rawPrice: {rawPrice}")
        except ValueError as e:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier, exception=e)
            return None
        return AttributeMetadata(metadataType=metadataType, value=price, unit=MetadataUnit.DOLLARS)

    def _getTitle(self, packageDict: Dict, modelIdentifier: str) -> Optional[str]:
        # 'description' more "Customer" readable than 'primaryName'
        if (title := packageDict.get('description', None)):
            return title
        self.loggingTools.logTitleFailure(parser=type(self), modelIdentifier=modelIdentifier)
        return None

    def _parsePackage(self, packageDict: Dict, modelIdentifier: str) -> Optional[Package]:
        if not (title := self._getTitle(packageDict=packageDict, modelIdentifier=modelIdentifier)):
            return None
        metadata = None
        if (price := self._getPrice(packageDict=packageDict, modelIdentifier=modelIdentifier)):
            metadata = [price]
        return Package(title=title, metadata=metadata)

    def parse(self, dataDict: Dict) -> List[Package]:
        modelIdentifier = self.loggingTools.getModelIdentifier(dataDict)
        packages = AttributeSet(updater=PriceUpdater(metadataType=MetadataType.COMMON_MSRP, keepLowest=False))
        for packageDict in self._getPackageDicts(dataDict=dataDict, modelIdentifier=modelIdentifier):
            if (package := self._parsePackage(packageDict=packageDict, modelIdentifier=modelIdentifier)):
                packages.add(package)
        return list(packages)
