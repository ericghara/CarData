from typing import Dict, List, Optional

from common.domain.dto.AttributeDto import BodyStyle
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from common.exception.IllegalStateError import IllegalStateError
from transformer.domain.attribute_set.AttributeSet import AttributeSet
from transformer.domain.attribute_set.metadata_updater.implementation.PriceUpdater import PriceUpdater
from transformer.transform.AttributeParser import AttributeParser
from transformer.transform.gm.parser.LoggingTools import LoggingTools


class BodyStyleParser(AttributeParser):
    """
    Note for GM: "Body Style" does not follow the GM definition of
    Body Style (which in this data model falls under ``Model``).  In
    the current data model ``Body Style`` = GM's "Body Type"
    """

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _getTitle(self, bodyStyleDict: Dict, modelIdentifier: str) -> Optional[str]:
        try:
            title = bodyStyleDict['formattedConfig']
            if not title:
                raise ValueError("Title was empty or None")
        except (KeyError, ValueError) as e:
            self.loggingTools.logTitleFailure(parser=type(self), modelIdentifier=modelIdentifier)
            title = None
        return title

    def _getBaseMsrp(self, bodyStyleDict: dict, modelIdentifier: str) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.COMMON_BASE_MSRP
        try:
            msrp = bodyStyleDict['lowestMSRPValue']
            if type(msrp) not in [int, float]:
                raise IllegalStateError(f"Unexpected data type for base MSRP: {type(msrp)}")
        except KeyError as e:
            self.loggingTools.logtAttributeFailure(parser=type(self), modelIdentifier=modelIdentifier,
                                                   metadataType=metadataType)
            return None
        except IllegalStateError as e:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier, exception=e)
            return None
        return AttributeMetadata(metadataType=metadataType, value=int(msrp), unit=MetadataUnit.DOLLARS)

    def _parseBodyStyle(self, bodyStyleDict: Dict, modelIdentifier: str) -> Optional[BodyStyle]:
        title = self._getTitle(bodyStyleDict=bodyStyleDict, modelIdentifier=modelIdentifier)
        baseMsrp = self._getBaseMsrp(bodyStyleDict=bodyStyleDict, modelIdentifier=modelIdentifier)
        if not title and not baseMsrp:
            return None
        metadata = None
        if not title:
            title = "Standard"
        if baseMsrp:
            metadata = [baseMsrp]
        return BodyStyle(title=title, metadata=metadata)

    def _getBodyStyles(self, dataDict: Dict, modelIdentifier: str) -> List[Dict]:
        try:
            bodyStyleDicts = dataDict['modelMatrix']['bodyTypes']
        except KeyError as e:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier, exception=e)
            bodyStyleDicts = None
        if bodyStyleDicts is None:
            return list()
        return bodyStyleDicts

    def parse(self, dataDict: Dict) -> List[BodyStyle]:
        modelIdentifier = self.loggingTools.getModelIdentifier(dataDict)
        bodyStyles = AttributeSet(updater=PriceUpdater(metadataType=MetadataType.COMMON_BASE_MSRP, keepLowest=True))
        for bodyStyleDict in self._getBodyStyles(dataDict=dataDict, modelIdentifier=modelIdentifier):
            if (bodyStyle := self._parseBodyStyle(bodyStyleDict=bodyStyleDict, modelIdentifier=modelIdentifier)):
                bodyStyles.add(bodyStyle)
        if not bodyStyles:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier,
                                                  exception=IllegalStateError("No BodyStyles Found."))
            standardBodyStyle = BodyStyle(title="Standard")
            bodyStyles.add(standardBodyStyle)
        return list(bodyStyles)
