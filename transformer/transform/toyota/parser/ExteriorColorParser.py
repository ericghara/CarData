from typing import Dict, Iterable, Optional, List

from common.domain.dto.AttributeDto import ExteriorColor
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.domain.attribute_set.AttributeSet import AttributeSet
from transformer.domain.attribute_set.metadata_updater.implementation.PriceUpdater import PriceUpdater
from transformer.transform.AttributeParser import AttributeParser
from transformer.transform.toyota.parser.LoggingTools import LoggingTools
from transformer.transform.common import util


class ExteriorColorParser(AttributeParser):

    # Exterior and InteriorColorParsers are essentially the same

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
        price = util.priceToInt(priceStr)
        return AttributeMetadata(metadataType=metadataType, value=price, unit=MetadataUnit.DOLLARS)

    def _parseModel(self, modelJson: Dict) -> Iterable[ExteriorColor]:
        for colorJson in modelJson.get('exteriorcolor', list()):
            if title := self._getTitle(colorJson=colorJson, modelJson=modelJson):
                metadata = None
                if (priceMetadata := self._getPrice(colorJson=colorJson, modelJson=modelJson)):
                    metadata = [priceMetadata]
                yield ExteriorColor(title=title, metadata=metadata)

    def parse(self, jsonData: Dict) -> List[ExteriorColor]:
        exteriorDtos = AttributeSet(
            updater=PriceUpdater(metadataType=MetadataType.COMMON_MSRP, keepLowest=False))  # keeps highest MSRP
        for modelJson in jsonData['model']:
            for exteriorColor in self._parseModel(modelJson):
                if exteriorColor in exteriorDtos:
                    self.loggingTools.logDuplicateAttributeDto(parser=type(self), attributeDto=exteriorColor)
                exteriorDtos.add(exteriorColor)
        return list(exteriorDtos)
