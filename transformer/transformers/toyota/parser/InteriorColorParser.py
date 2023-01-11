from typing import Dict, Iterable

from transformer.attribute_dto.AttributeDto import *
from transformer.attribute_metadata.AttributeMetadata import AttributeMetadata
from transformer.attribute_metadata.MetadataType import MetadataType
from transformer.attribute_metadata.MetadataUnit import MetadataUnit
from transformer.transformers.AttributeParser import AttributeParser
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser import util


class InteriorColorParser(AttributeParser):

    # Exterior and InteriorColorParsers are essentially the same

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _getTitle(self, colorJson: Dict, modelJson: Dict) -> Optional[str]:
        try:
            colorTitle = colorJson['title']
        except KeyError as e:
            self.loggingTools.logTitleFailure(transformer=self.__class__, exception=e, modelJson=modelJson)
            return None
        if not colorTitle:
            return None
        return util.removeBracketed(colorTitle)

    def _getPrice(self, colorJson: Dict, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.COMMON_MSRP
        try:
            priceStr = colorJson['price']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return
        if not priceStr:
            return None
        price = util.priceStrToInt(priceStr)
        return AttributeMetadata(metadataType=metadataType, value=price, unit=MetadataUnit.DOLLARS)

    def _parseModel(self, modelJson: Dict) -> Iterable[InteriorColor]:
        for colorJson in modelJson.get('interiorcolor', list()):
            if title := self._getTitle(colorJson=colorJson, modelJson=modelJson):
                metadata = None
                if (priceMetadata := self._getPrice(colorJson=colorJson, modelJson=modelJson)):
                    metadata = [priceMetadata]
                yield InteriorColor(title=title, metadata=metadata)

    def parse(self, jsonData: Dict) -> List[InteriorColor]:
        interiorDtos = set()
        for modelJson in jsonData['model']:
            for interiorColor in self._parseModel(modelJson):
                if interiorColor in interiorDtos:
                    self.loggingTools.logDuplicateAttributeDto(transformer=type(self), attributeDto=interiorColor)
                else:
                    interiorDtos.add(interiorColor)
        return list(interiorDtos)
