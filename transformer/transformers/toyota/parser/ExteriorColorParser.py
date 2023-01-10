from typing import Dict

from transformer.attribute_dto.AttributeDto import *
from transformer.attribute_metadata.AttributeMetadata import AttributeMetadata
from transformer.attribute_metadata.MetadataType import MetadataType
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser import util

class ExteriorColorParser:

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _getTitle(self, colorJson: Dict, modelJson: Dict) -> Optional[str]:
        try:
            colorTitle = colorJson['title']
        except KeyError as e:
            self.loggingTools.logTitleFailure(transformer=self.__class__, exception=e, modelJson=modelJson)
            return None
        return util.removeBracketed(colorTitle)

    def _getPrice(self, colorJson: Dict, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.COMMON_MSRP
        try:
            priceStr = colorJson['price']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return
        price = util.priceStrToInt(priceStr)
        return AttributeMetadata(metadataType=metadataType, value=price, units='$')


    def parse(self, jsonData: Dict) -> List[AttributeDto]:
        exteriorDtos = set()
        for modelJson in jsonData['model']:
            for colorJson in modelJson['exteriorcolor']:
                if title  := self._getTitle(colorJson=colorJson, modelJson=modelJson):
                    priceMetadata = self._getPrice(colorJson=colorJson, modelJson=modelJson)
                    exteriorDtos.add(ExteriorColor(title=title, metadata=priceMetadata))
        return list(exteriorDtos)
