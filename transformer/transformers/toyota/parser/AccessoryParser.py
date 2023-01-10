from typing import Dict

from transformer.attribute_dto.AttributeDto import *
from transformer.attribute_metadata.AttributeMetadata import AttributeMetadata
from transformer.attribute_metadata.MetadataType import MetadataType
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser import util


class AccessoryParser:

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _getTitle(self, accessoryJson: Dict, modelJson: Dict) -> Optional[str]:
        try:
            accessoryTitle = accessoryJson['title']
        except KeyError as e:
            self.loggingTools.logTitleFailure(transformer=self.__class__, exception=e, modelJson=modelJson)
            return None
        return util.removeBracketed(accessoryTitle)

    def _getCategory(self, accessoryJson: Dict, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.ACCESSORY_CATEGORY
        try:
            categories = accessoryJson['group']
        except KeyError as e:
            self.loggingTools.logTitleFailure(transformer=self.__class__, exception=e, modelJson=modelJson)
            return None
        if not categories:
            return None
        return AttributeMetadata(metadataType=metadataType, value=categories[0])

    def _getPrice(self, accessoryJson: Dict, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.COMMON_MSRP
        try:
            priceStr = accessoryJson['price']
        except KeyError as e:
            self.loggingTools.logTitleFailure(transformer=self.__class__, exception=e, modelJson=modelJson)
            return None
        price = util.priceStrToInt(priceStr)
        return AttributeMetadata(metadataType=metadataType, value=price, units="$")

    def parse(self, jsonData: Dict) -> List[AttributeDto]:
        accessoryDtos = set()
        for modelJson in jsonData['model']:
            for accessoryJson in modelJson['accessories']:
                if title := self._getTitle(accessoryJson=accessoryJson, modelJson=modelJson):
                    rawMetadata = [self._getPrice(accessoryJson=accessoryJson, modelJson=modelJson),
                                   self._getCategory(accessoryJson=accessoryJson, modelJson=modelJson)]
                    metadata = [metaAttribute for metaAttribute in rawMetadata if metaAttribute is not None]
                    accessoryDtos.add(Accessory(title=title, metadata=metadata if metadata else None))
        return list(accessoryDtos)
