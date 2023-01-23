from typing import Type, Dict, List, Optional, Iterator

from common.domain.dto.AttributeDto import InteriorColor, AttributeDto, ExteriorColor
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.domain.attribute_set.AttributeSet import AttributeSet
from transformer.domain.attribute_set.metadata_updater.implementation.PriceUpdater import PriceUpdater
from transformer.transform.AttributeParser import AttributeParser
from transformer.transform.common import util
from transformer.transform.gm.parser.LoggingTools import LoggingTools


class ColorParser:

    def __init__(self, attributeType: Type, attributeParser: AttributeParser, loggingTools: LoggingTools):
        self.attributeConstructor = attributeType
        # used to associate logs from this ColorParser with the AttributeParser which is utilizing it
        self.attributeParser = type(attributeParser)
        self.loggingTools = loggingTools

    def _getTitle(self, colorDict: Dict, modelIdentifier: str) -> Optional[str]:
        title = colorDict.get("primaryName", None)
        if not title:
            self.loggingTools.logTitleFailure(parser=self.attributeParser, modelIdentifier=modelIdentifier)
            return None
        return title

    def _getPrice(self, colorDict: Dict, modelIdentifier: str) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.COMMON_MSRP
        price = colorDict.get("msrp", None)
        if price is None:
            self.loggingTools.logtAttributeFailure(parser=self.attributeParser, modelIdentifier=modelIdentifier,
                                                   metadataType=metadataType)
            return None
        # price should be an int, so this *should* be a no-op, but if that changes this is more robust
        try:
            priceInt = util.digitsToInt(price)
            if priceInt is None:
                raise ValueError(f"Un-parsable Price. {price}")
        except ValueError as e:
            self.loggingTools.logUnexpectedSchema(parser=self.attributeParser, modelIdentifier=modelIdentifier,
                                                  exception=e)
            return None
        return AttributeMetadata(metadataType=metadataType, value=priceInt, unit=MetadataUnit.DOLLARS)

    def _parseColor(self, colorDict: Dict, modelIdentifier: str) -> Optional[AttributeDto]:
        if (title := self._getTitle(colorDict=colorDict, modelIdentifier=modelIdentifier)):
            metadata = None
            if (priceMetadata := self._getPrice(colorDict=colorDict, modelIdentifier=modelIdentifier)):
                metadata = [priceMetadata]
            return self.attributeConstructor(title=title, metadata=metadata)

    def getColors(self, categoryDicts: List[Dict], modelIdentifier: str) -> List[AttributeDto]:
        colors = AttributeSet(updater=PriceUpdater(metadataType=MetadataType.COMMON_MSRP, keepLowest=False))
        for category in categoryDicts:
            colorDicts = category.get("items") or list()
            for colorDict in colorDicts:
                if (color := self._parseColor(colorDict=colorDict, modelIdentifier=modelIdentifier)):
                    colors.add(color)
        if not colors:
            self.loggingTools.logNoAttributes(parser=self.attributeParser, modelIdentifier=modelIdentifier)
        return list(colors)


class InteriorColorParser(AttributeParser):

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools
        self.colorParser = ColorParser(attributeType=InteriorColor, attributeParser=self, loggingTools=loggingTools)

    def _getInteriorColorCategories(self, dataDict: Dict, modelIdentifier: str) -> List[Dict]:
        try:
            colorCategories = dataDict['config']['OPTIONS']['COLOR']['interior']
        except KeyError as e:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier, exception=e)
            return list()
        return colorCategories or list()

    def parse(self, dataDict: Dict) -> List[InteriorColor]:
        modelIdentifier = self.loggingTools.getModelIdentifier(dataDict)
        categoryDicts = self._getInteriorColorCategories(dataDict=dataDict, modelIdentifier=modelIdentifier)
        return self.colorParser.getColors(categoryDicts=categoryDicts, modelIdentifier=modelIdentifier)


class ExteriorColorParser(AttributeParser):

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools
        self.colorParser = ColorParser(attributeType=ExteriorColor, attributeParser=self, loggingTools=loggingTools)

    def _getInteriorColorCategories(self, dataDict: Dict, modelIdentifier: str) -> List[Dict]:
        try:
            colorCategories = dataDict['config']['OPTIONS']['COLOR']['exterior']
        except KeyError as e:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier, exception=e)
            return list()
        return colorCategories or list()

    def parse(self, dataDict: Dict) -> List[InteriorColor]:
        modelIdentifier = self.loggingTools.getModelIdentifier(dataDict)
        categoryDicts = self._getInteriorColorCategories(dataDict=dataDict, modelIdentifier=modelIdentifier)
        return self.colorParser.getColors(categoryDicts=categoryDicts, modelIdentifier=modelIdentifier)
