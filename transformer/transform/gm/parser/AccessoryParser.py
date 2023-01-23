from typing import Dict, Optional, List

from common.domain.dto.AttributeDto import Accessory
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from common.exception.IllegalStateError import IllegalStateError
from transformer.domain.attribute_set.AttributeSet import AttributeSet
from transformer.domain.attribute_set.metadata_updater.implementation.PriceUpdater import PriceUpdater
from transformer.transform.AttributeParser import AttributeParser
from transformer.transform.gm.parser.LoggingTools import LoggingTools


class AccessoryParser(AttributeParser):

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _getTitle(self, accessoryDict: Dict, modelIdentifier: str) -> Optional[str]:
        try:
            accessoryTitle = accessoryDict['primaryName']
        except KeyError as e:
            self.loggingTools.logTitleFailure(parser=type(self), modelIdentifier=modelIdentifier)
            return None
        if not accessoryTitle:
            return None
        return accessoryTitle

    def _createCategoryMetadata(self, categoryStr: str) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.ACCESSORY_CATEGORY
        return AttributeMetadata(metadataType=metadataType, value=categoryStr)

    def _getPrice(self, accessoryDict: Dict, modelIdentifier: str) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.COMMON_MSRP
        try:
            # raw msrp *should* be int, but enforcing that
            rawPrice = accessoryDict['msrp']
            if type(rawPrice) not in {int, float}:
                raise IllegalStateError("Unrecognized price value.")
        except (KeyError, IllegalStateError) as e:
            self.loggingTools.logtAttributeFailure(parser=type(self), modelIdentifier=modelIdentifier,
                                                   metadataType=metadataType)
            return None
        price = int(rawPrice)
        return AttributeMetadata(metadataType=metadataType, value=price, unit=MetadataUnit.DOLLARS)

    def _getAccessoriesJson(self, dataDict: dict, modelIdentifier: str) -> Dict:
        try:
            return dataDict['config']['ACCESSORIES']
        except KeyError:
            self.loggingTools.logNoAttributes(parser=type(self), modelIdentifier=modelIdentifier)
            return dict()

    def _parseAccessory(self, accessoryDict: Dict, categoryStr: str, modelIdentifier: str) -> Optional[Accessory]:
        title = self._getTitle(accessoryDict=accessoryDict, modelIdentifier=modelIdentifier)
        if not title:
            return None
        metadata = list()
        metadata.append(self._createCategoryMetadata(categoryStr=categoryStr))
        if (priceMetadata := self._getPrice(accessoryDict=accessoryDict, modelIdentifier=modelIdentifier)):
            metadata.append(priceMetadata)
        return Accessory(title=title, metadata=metadata)

    def parse(self, dataDict: Dict) -> List[Accessory]:
        modelIdentifier = self.loggingTools.getModelIdentifier(dataDict)
        # There should not be duplicates, requiring a set, but using one out of an abundance of caution
        accessoryDtos = AttributeSet(updater=PriceUpdater(metadataType=MetadataType.COMMON_MSRP, keepLowest=False))
        for accessoryCategory, accessoryList in self._getAccessoriesJson(dataDict=dataDict,
                                                                         modelIdentifier=modelIdentifier).items():
            for accessoryDict in accessoryList:
                # decided to make a new AttributeMetadata(MetadataType.ACCESSORY_CATEGORY... for each accessory
                # clients shouldn't mutate the AttributeMetadata...but that can't be guaranteed in python
                accessoryDto = self._parseAccessory(accessoryDict=accessoryDict, categoryStr=accessoryCategory,
                                     modelIdentifier=modelIdentifier)
                if accessoryDto:
                    accessoryDtos.add(accessoryDto)
        return list(accessoryDtos)
