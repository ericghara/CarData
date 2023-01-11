from typing import Dict

from transformer.attribute_dto.AttributeDto import *
from transformer.attribute_metadata.AttributeMetadata import AttributeMetadata
from transformer.attribute_metadata.MetadataType import MetadataType
from transformer.attribute_metadata.MetadataUnit import MetadataUnit
from transformer.transformers.AttributeParser import AttributeParser
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser import util


class BodyStyleParser(AttributeParser):

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def parse(self, jsonData: Dict) -> List[BodyStyle]:
        bodyStyleDtos = set()
        for modelJson in jsonData['model']:
            bodyStyleDto = self._parseModel(modelJson)
            if bodyStyleDto in bodyStyleDtos:
                self.loggingTools.logDuplicateAttributeDto(transformer=self.__class__, attributeDto=bodyStyleDto)
            else:
                bodyStyleDtos.add(bodyStyleDto)
        if not bodyStyleDtos:
            self.loggingTools.logNoAttributes(self.__class__)
        return list(bodyStyleDtos)

    def _parseModel(self, modelJson: Dict) -> BodyStyle:
        metadata = list()
        for metadataFn in self._getMSRP, self._getSeating, self._getCab, self._getBed:
            if foundData := metadataFn(modelJson):
                metadata.append(foundData)
        title = self._createTitle(metadata)
        return BodyStyle(title=title, metadata=metadata)

    def _createTitle(self, attributeMetadata: List[AttributeMetadata]) -> str:
        """
        ``BodyStyle`` title is inferred from metadata.  toyota does not have the concept
        of ``BodyStyle`` that fits within the data model being used.
        :param attributeMetadata:
        :return:
        """
        titleByType = {metadata.metadataType: metadata.value for metadata in attributeMetadata}
        cab = titleByType.get(MetadataType.BODY_STYLE_CAB)
        bed = titleByType.get(MetadataType.BODY_STYLE_BED)
        return " ".join([part for part in [cab, bed] if part]) or "Standard"

    def _getBed(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.BODY_STYLE_BED
        try:
            bed = modelJson['bed']['title']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        if not bed:
            return None
        return AttributeMetadata(metadataType=metadataType, value=bed)

    def _getCab(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.BODY_STYLE_CAB
        try:
            cab = modelJson['cab']['title']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        if not cab:
            return None
        return AttributeMetadata(metadataType=metadataType, value=cab)

    def _getSeating(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.BODY_STYLE_SEATING
        try:
            seatingStr = modelJson['attributes']['seating']['value']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        if not seatingStr:
            return None
        seatingInt = util.digitsToInt(seatingStr)
        return AttributeMetadata(metadataType=metadataType, value=seatingInt, unit=MetadataUnit.PASSENGERS)

    def _getMSRP(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.BODY_STYLE_BASE_MSRP
        try:
            msrpStr = modelJson['attributes']['msrp']['value']  # ex "$101,500"
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        if not msrpStr:
            return None
        msrp = util.priceStrToInt(msrpStr)
        return AttributeMetadata(metadataType=metadataType, value=msrp, unit=MetadataUnit.DOLLARS)
