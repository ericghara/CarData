from typing import Dict, Iterable, Optional, List

from common.domain.dto.AttributeDto import InteriorColor
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.domain.attribute_set.AttributeSet import AttributeSet
from transformer.domain.attribute_set.metadata_updater.implementation.PriceUpdater import PriceUpdater
from transformer.transformer.AttributeParser import AttributeParser
from transformer.transformer.toyota.LoggingTools import LoggingTools
from transformer.transformer.toyota.parser import util


class InteriorColorParser(AttributeParser):

    # Interior and InteriorColorParsers are essentially the same

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _getTitle(self, colorJson: Dict, modelJson: Dict) -> Optional[str]:
        try:
            colorTitle = colorJson['title']
        except KeyError as e:
            self.loggingTools.logTitleFailure(parser=self.__class__, exception=e, modelJson=modelJson)
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
        interiorDtos = AttributeSet(
            updater=PriceUpdater(metadataType=MetadataType.COMMON_MSRP, keepLowest=False))  # keeps highest MSRP
        for modelJson in jsonData['model']:
            for interiorColor in self._parseModel(modelJson):
                if interiorColor in interiorDtos:
                    self.loggingTools.logDuplicateAttributeDto(parser=type(self), attributeDto=interiorColor)
                interiorDtos.add(interiorColor)
        return list(interiorDtos)
