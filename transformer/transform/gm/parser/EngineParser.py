import re
from typing import List, Dict, Optional

from common.domain.dto.AttributeDto import Drive, Engine
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.domain.attribute_set.AttributeSet import AttributeSet
from transformer.domain.attribute_set.metadata_updater.implementation.PriceUpdater import PriceUpdater
from transformer.transform.AttributeParser import AttributeParser
from transformer.transform.common import util
from transformer.transform.gm.parser.LoggingTools import LoggingTools
from common.domain.enum.FuelType import FuelType


class EngineParser(AttributeParser):
    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def _getTitle(self, engineDict: Dict, modelIdentifier: str) -> Optional[str]:
        # shortCFD preferred over primaryName, as primaryName has sparse information for electric vehicles
        if not (title := engineDict.get("shortCFD", None)):
            self.loggingTools.logTitleFailure(parser=type(self), modelIdentifier=modelIdentifier)
            return None
        return title

    def _getPower(self, engineDict: Dict, modelIdentifier: str) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.ENGINE_HORSEPOWER
        for engineDetails in engineDict.get("extendedCFD", ""), engineDict.get("longCFD", ""):
            # hp can be listed in 2 locations (inconsistent)
            if (hpResult := re.search(pattern="(\d+(\.\d)?)\s?hp", string=engineDetails, flags=re.IGNORECASE)):
                hpInt = util.numStrToInt(hpResult.group(1))
                return AttributeMetadata(metadataType=metadataType, value=hpInt, unit=MetadataUnit.HORSEPOWER)
        self.loggingTools.logtAttributeFailure(parser=type(self), metadataType=metadataType,
                                               modelIdentifier=modelIdentifier)
        return None

    def _getFuelType(self, engineDict: Dict, modelIdentifier: str) -> Optional[AttributeMetadata]:
        # use displacement (#L or #.#L) as identifier for internal combustion engine
        engineName = engineDict.get("primaryName") or ""
        if re.search(pattern="\d(\.\d)?L", string=engineName):
            if re.search(pattern="diesel", string=engineName, flags=re.IGNORECASE):
                fuelType = FuelType.DIESEL.value
            else:
                fuelType = FuelType.GASOLINE.value
        elif re.search(pattern="electric", string=engineDict.get("description") or "", flags=re.IGNORECASE):
            fuelType = FuelType.ELECTRIC.value
        # no hybrid, GM has none currently (1-2023)
        else:
            self.loggingTools.logtAttributeFailure(parser=type(self), modelIdentifier=modelIdentifier,
                                                   metadataType=MetadataType.ENGINE_FUEL_TYPE)
            return None
        return AttributeMetadata(metadataType=MetadataType.ENGINE_FUEL_TYPE, value=fuelType)

    def _getPrice(self, engineDict: Dict, modelIdentifier: str) -> Optional[AttributeMetadata]:
        rawMsrp = engineDict.get('msrp', None)
        try:
            if rawMsrp is None or (msrp := util.digitsToInt(rawMsrp)) is None:
                raise ValueError(f"MSRP value is un-parsable: {rawMsrp}")
        except (ValueError, AttributeError) as e:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier, exception=e)
            return None
        return AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=msrp, unit=MetadataUnit.DOLLARS)

    def _getEngineDicts(self, dataDict: Dict, modelIdentifier: str) -> List[Dict]:
        try:
            engineDicts = dataDict['modelMatrix']['engine']
        except KeyError as e:
            self.loggingTools.logUnexpectedSchema(parser=type(self), modelIdentifier=modelIdentifier, exception=e)
            engineDicts = None
        if engineDicts is None:
            return list()
        return engineDicts

    def _getEngineAttributes(self, engineDict: Dict, modelIdentifier: str) -> Optional[Engine]:
        if not (title := self._getTitle(engineDict=engineDict, modelIdentifier=modelIdentifier)):
            return None
        metadata = list()
        for metaFn in self._getFuelType, self._getPower, self._getPrice:
            if (attributeMetadata := metaFn(engineDict=engineDict, modelIdentifier=modelIdentifier)):
                metadata.append(attributeMetadata)
        if not metadata:
            metadata = None
        return Engine(title=title, metadata=metadata)

    def parse(self, dataDict: Dict) -> List[Drive]:
        modelIdentifier = self.loggingTools.getModelIdentifier(dataDict)
        # Attribute set, probably isn't necessary here.  GM doesn't seem to duplicate data
        engines = AttributeSet(updater=PriceUpdater(metadataType=MetadataType.COMMON_MSRP, keepLowest=False))
        for engineDict in self._getEngineDicts(dataDict=dataDict, modelIdentifier=modelIdentifier):
            if (engine := self._getEngineAttributes(engineDict=engineDict, modelIdentifier=modelIdentifier)):
                engines.add(engine)
        if not engines:
            self.loggingTools.logNoAttributes(parser=type(self), modelIdentifier=modelIdentifier)
        return list(engines)
