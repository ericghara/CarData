from typing import Dict, List, Optional

from common.domain.dto.AttributeDto import Drive
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.domain.attribute_set.AttributeSet import AttributeSet
from transformer.domain.attribute_set.metadata_updater.implementation.PriceUpdater import PriceUpdater
from transformer.transform.AttributeParser import AttributeParser
from transformer.transform.common import util
from transformer.transform.gm.parser.LoggingTools import LoggingTools


class DriveParser(AttributeParser):
    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _getTitle(self, driveDict: Dict, modelIdentifier: str) -> Optional[str]:
        try:
            title = driveDict['id']
        except KeyError as e:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier, exception=e)
            title = None
        if not title:
            self.loggingTools.logTitleFailure(parser=type(self), modelIdentifier=modelIdentifier)
            return None
        return title

    def _getBaseMsrp(self, driveDict: Dict, modelIdentifier: str) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.COMMON_BASE_MSRP
        try:
            priceStr = driveDict['lowestMSRP']
        except KeyError as e:
            self.loggingTools.logtAttributeFailure(parser=type(self), modelIdentifier=modelIdentifier, metadataType=metadataType)
            return None
        try:
            price = util.priceToInt(priceStr)
        except (ValueError, AttributeError) as e:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier, exception=e)
            return None
        return AttributeMetadata(metadataType=metadataType, value=price, unit=MetadataUnit.DOLLARS)

    def _getDriveDicts(self, dataDict: Dict, modelIdentifier: str) -> List[Dict]:
        try:
            driveDicts = dataDict['modelMatrix']['driveTypes']
        except KeyError as e:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier, exception=e)
            driveDicts = None
        if driveDicts is None:
            return list()
        return driveDicts

    def _parseDrive(self, driveDict: Dict, modelIdentifier: str) -> Optional[Drive]:
        if not (title := self._getTitle(driveDict=driveDict, modelIdentifier=modelIdentifier)):
            return None
        metadata = None
        if (msrpMeta := self._getBaseMsrp(driveDict=driveDict, modelIdentifier=modelIdentifier)):
            metadata = [msrpMeta]
        return Drive(title=title, metadata=metadata)

    def parse(self, dataDict: Dict) -> List[Drive]:
        modelIdentifier = self.loggingTools.getModelIdentifier(dataDict)
        # Attribute set, probably isn't necessary here.  GM doesn't seem to duplicate data
        drives = AttributeSet(updater=PriceUpdater(metadataType=MetadataType.COMMON_BASE_MSRP, keepLowest=True))
        for driveDict in self._getDriveDicts(dataDict=dataDict, modelIdentifier=modelIdentifier):
            if (drive := self._parseDrive(driveDict=driveDict, modelIdentifier=modelIdentifier)):
                drives.add(drive)
        if not drives:
            self.loggingTools.logNoAttributes(parser=type(self), modelIdentifier=modelIdentifier)
        return list(drives)


