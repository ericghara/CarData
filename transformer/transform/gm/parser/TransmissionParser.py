from typing import Optional, Dict, List

from common.domain.dto.AttributeDto import Transmission
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.domain.attribute_set.AttributeSet import AttributeSet
from transformer.domain.attribute_set.metadata_updater.implementation.PriceUpdater import PriceUpdater
from transformer.transform.AttributeParser import AttributeParser
from transformer.transform.common import util
from transformer.transform.gm.parser.LoggingTools import LoggingTools


class TransmissionParser(AttributeParser):

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _getTitle(self, transmissionDict: Dict, modelIdentifier: str) -> Optional[str]:
        if (title := transmissionDict.get('primaryName', None)):
            return title
        self.loggingTools.logTitleFailure(parser=type(self), modelIdentifier=modelIdentifier)
        return None

    def _getPrice(self, transmissionDict: Dict, modelIdentifier: str) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.COMMON_MSRP
        rawPrice = transmissionDict.get('msrp', None)
        try:
            if rawPrice is None or (price := util.digitsToInt(rawPrice)) is None:
                raise ValueError(f"Un-parsable rawPrice: {rawPrice}")
        except ValueError as e:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier, exception=e)
            return None
        return AttributeMetadata(metadataType=metadataType, value=price, unit=MetadataUnit.DOLLARS)

    def _parseTransmission(self, transmissionDict: Dict, modelIdentifier: str) -> Optional[Transmission]:
        if not (title := self._getTitle(transmissionDict=transmissionDict, modelIdentifier=modelIdentifier)):
            return None
        metadata = None
        if (price := self._getPrice(transmissionDict=transmissionDict, modelIdentifier=modelIdentifier)):
            metadata = [price]
        return Transmission(title=title, metadata=metadata)

    def _getTransmissionDicts(self, dataDict: Dict, modelIdentifier: str) -> List[Dict]:
        try:
            transmissionDicts = dataDict['modelMatrix']['transmission']
            if type(transmissionDicts) is not list:
                raise TypeError(f"Expected list but found: {type(transmissionDicts)}")
        except (KeyError, TypeError) as e:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier, exception=e)
            return list()
        return transmissionDicts

    def parse(self, dataDict: Dict) -> List[Transmission]:
        modelIdentifier = self.loggingTools.getModelIdentifier(dataDict)
        transmissions = AttributeSet(updater=PriceUpdater(metadataType=MetadataType.COMMON_MSRP, keepLowest=False))
        for transmissionDict in self._getTransmissionDicts(dataDict=dataDict, modelIdentifier=modelIdentifier):
            if (transmission := self._parseTransmission(transmissionDict=transmissionDict, modelIdentifier=modelIdentifier)):
                transmissions.add(transmission)
        if not transmissions:
            self.loggingTools.logNoAttributes(parser=type(self), modelIdentifier=modelIdentifier)
        return list(transmissions)
