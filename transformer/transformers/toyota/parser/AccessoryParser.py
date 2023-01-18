from typing import Dict, Iterable, Optional, List

from common.domain.dto.AttributeDto import Accessory
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.domain.attribute_set.AttributeSet import AttributeSet
from transformer.domain.attribute_set.metadata_updater.implementation.PriceUpdater import PriceUpdater
from transformer.transformers.AttributeParser import AttributeParser
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser import util


class AccessoryParser(AttributeParser):

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _getTitle(self, accessoryJson: Dict, modelJson: Dict) -> Optional[str]:
        try:
            accessoryTitle = accessoryJson['title']
        except KeyError as e:
            self.loggingTools.logTitleFailure(parser=self.__class__, exception=e, modelJson=modelJson)
            return None
        if not accessoryTitle:
            return None
        return util.removeBracketed(accessoryTitle)

    def _getCategory(self, accessoryJson: Dict, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.ACCESSORY_CATEGORY
        try:
            category = accessoryJson['attributes']['group']['value']
        except KeyError as e:
            self.loggingTools.logTitleFailure(parser=self.__class__, exception=e, modelJson=modelJson)
            return None
        if not category:
            return None
        return AttributeMetadata(metadataType=metadataType, value=category)

    def _getPrice(self, accessoryJson: Dict, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.COMMON_MSRP
        try:
            priceStr = accessoryJson['price']
        except KeyError as e:
            self.loggingTools.logTitleFailure(parser=self.__class__, exception=e, modelJson=modelJson)
            return None
        if not priceStr:
            return None
        price = util.priceStrToInt(priceStr)
        return AttributeMetadata(metadataType=metadataType, value=price, unit=MetadataUnit.DOLLARS)

    def _parseModel(self, modelJson: Dict) -> Iterable[Accessory]:
        for accessoryJson in modelJson.get('accessories', list()):
            if title := self._getTitle(accessoryJson=accessoryJson, modelJson=modelJson):
                rawMetadata = [self._getPrice(accessoryJson=accessoryJson, modelJson=modelJson),
                               self._getCategory(accessoryJson=accessoryJson, modelJson=modelJson)]
                metadata = [metaAttribute for metaAttribute in rawMetadata if metaAttribute]
                yield Accessory(title=title, metadata=metadata if metadata else None)

    def parse(self, jsonData: Dict) -> List[Accessory]:
        accessoryDtos = AttributeSet(
            updater=PriceUpdater(metadataType=MetadataType.COMMON_MSRP, keepLowest=False))  # keeps the highest price
        for modelJson in jsonData['model']:
            for accessory in self._parseModel(modelJson):
                if accessory in accessoryDtos:
                    self.loggingTools.logDuplicateAttributeDto(parser=self.__class__, attributeDto=accessory)
                accessoryDtos.add(accessory)
        return list(accessoryDtos)
