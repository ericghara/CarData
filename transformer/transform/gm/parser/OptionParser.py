from typing import Dict, List, Optional

from common.domain.dto.AttributeDto import Option
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.domain.attribute_set.AttributeSet import AttributeSet
from transformer.domain.attribute_set.metadata_updater.implementation.PriceUpdater import PriceUpdater
from transformer.transform.AttributeParser import AttributeParser
from transformer.transform.common import util
from transformer.transform.gm.parser.LoggingTools import LoggingTools


class OptionParser(AttributeParser):

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _createCategoryName(self, categoryId: str) -> str:
        # example categoryId: exterior.safety
        if not categoryId or type(categoryId) is not str:
            return "Miscellaneous"
        return categoryId.replace('.', ' - ').title()

    def _getTitle(self, optionDict: Dict, modelIdentifier: str) -> Optional[str]:
        # 'description' values seem more customer readable than 'primaryName'
        if (title := optionDict.get('description', None)):
            return title
        self.loggingTools.logTitleFailure(parser=type(self), modelIdentifier=modelIdentifier)
        return None

    def _getPrice(self, optionDict: Dict, modelIdentifier: str) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.COMMON_MSRP
        rawPrice = optionDict.get('msrp', None)
        try:
            if rawPrice is None or (price := util.digitsToInt(rawPrice)) is None:
                raise ValueError(f"Un-parsable rawPrice: {rawPrice}")
        except ValueError as e:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier, exception=e)
            return None
        return AttributeMetadata(metadataType=metadataType, value=price, unit=MetadataUnit.DOLLARS)

    def _getCategory(self, categoryName: str) -> Optional[AttributeMetadata]:
        return AttributeMetadata(metadataType=MetadataType.COMMON_CATEGORY, value=categoryName)

    def _parseOptionDict(self, optionDict: Dict, categoryName: str, modelIdentifier: str) -> Optional[Option]:
        if not (title := self._getTitle(optionDict=optionDict, modelIdentifier=modelIdentifier)):
            return None
        # Although metadata should not be mutated, deciding to create new category object for
        # each attribute, even if they are in the same category
        metadata = [meta for meta in (self._getCategory(categoryName),
                                      self._getPrice(optionDict=optionDict, modelIdentifier=modelIdentifier))
                    if meta]
        return Option(title=title, metadata=metadata)

    def _getAllOptionsCategories(self, dataDict: Dict, modelIdentifier: str) -> Dict:
        try:
            optionsDict = dataDict['config']['OPTIONS']
            if not optionsDict:
                raise ValueError("Unable to retrieve OPTIONS")
        except (KeyError, ValueError) as e:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier, exception=e)
            return dict()
        categoriesDict = optionsDict.get("EXTERIOR") or dict()
        categoriesDict.update(optionsDict.get("INTERIOR") or dict())
        return categoriesDict

    def parse(self, dataDict: Dict) -> List[Option]:
        modelIdentifier = self.loggingTools.getModelIdentifier(dataDict)
        options = AttributeSet(updater=PriceUpdater(metadataType=MetadataType.COMMON_MSRP, keepLowest=False))
        categoryDict = self._getAllOptionsCategories(dataDict=dataDict, modelIdentifier=modelIdentifier)
        for categoryId, optionDicts in categoryDict.items():
            categoryName = self._createCategoryName(categoryId)
            for optionDict in optionDicts:
                if (option := self._parseOptionDict(optionDict=optionDict, categoryName=categoryName,
                                                    modelIdentifier=modelIdentifier)):
                    options.add(option)
        if not options:
            self.loggingTools.logNoAttributes(parser=type(self), modelIdentifier=modelIdentifier)
        return list(options)
