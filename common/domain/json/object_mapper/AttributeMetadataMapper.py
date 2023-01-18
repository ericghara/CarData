from typing import Optional, Dict

from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from common.domain.json.object_mapper.ObjectMapper import ObjectMapper
from common.exception.JsonDecodeError import JsonDecodeError


class AttributeMetadataMapper(ObjectMapper):
    objectType = AttributeMetadata

    def _getMetadataType(self, jsonDict: Dict) -> MetadataType:
        try:
            metadataTypeStr = jsonDict["metadataType"]
            metadataType = MetadataType.__getitem__(metadataTypeStr)
            if metadataTypeStr is None:
                raise JsonDecodeError("Required Key 'metadataType' was null.")
        except KeyError as e:
            raise JsonDecodeError("Required Key 'metadataType' was absent, invalid.", e)
        return metadataType

    def _getUnit(self, jsonDict) -> Optional[MetadataUnit]:
        unitStr = jsonDict.get("unit")
        if unitStr is None:
            return None
        try:
            return MetadataUnit.__getitem__(unitStr)
        except KeyError as e:
            raise JsonDecodeError(f"Unable to convert {unitStr} to a MetadataUnit")

    def map(self, jsonDict: Dict) -> objectType:
        metadataType = self._getMetadataType(jsonDict)
        value = jsonDict.get("value")
        unit = self._getUnit(jsonDict)
        return AttributeMetadata(metadataType=metadataType, value=value, unit=unit)
