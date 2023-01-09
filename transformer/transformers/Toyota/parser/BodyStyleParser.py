from typing import Dict

from transformer.attribute_dto.AttributeDto import *
from transformer.attribute_metadata.AttributeMetadata import AttributeMetadata
from transformer.attribute_metadata.MetadataType import MetadataType
from transformer.transformers.Toyota.LoggingTools import LoggingTools
from transformer.transformers.Toyota.parser import util


class BodyStyleParser:

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def parse(self, jsonData: Dict) -> List[AttributeDto]:
        bodyStyleDtos = set()
        for modelJson in jsonData['model']:
            metadata = list()
            for metadataFn in self._getMSRP, self._getSeating, self._getCab, self._getBed:
                if foundData := metadataFn(modelJson):
                    metadata.append(foundData)
            title = self._createTitle(metadata)
            bodyStyleDto = BodyStyle(title=title, metadata=metadata)
            if not bodyStyleDtos.add(bodyStyleDto):
                self.loggingTools.logDuplicateAttributeDto(transformer=self.__class__, attributeDto=bodyStyleDto)
        if not bodyStyleDtos:
            self.loggingTools.logNoAttributes(self.__class__)
        return list(bodyStyleDtos)

    def _createTitle(self, attributeMetadata: List[AttributeMetadata]) -> str:
        """
        ``BodyStyle`` title is inferred from metadata.  Toyota does not have the concept
        of ``BodyStyle`` that fits within the data model being used.
        :param attributeMetadata:
        :return:
        """
        titleByType = {metadata.key: metadata.label for metadata in attributeMetadata}
        bed = titleByType.get(MetadataType.BODY_STYLE_BED.key)
        cab = titleByType.get(MetadataType.BODY_STYLE_CAB.key)
        if not bed and not cab:
            return "Standard"
        if bed and cab:
            return f"{cab} {bed}"
        return bed or cab

    def _getBed(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.BODY_STYLE_BED
        try:
            bed = f"{modelJson['bed']['title']} Bed"  # ex: f"{"8.1ft"} Bed"
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        return AttributeMetadata(metadataType=metadataType, value=bed)

    def _getCab(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.BODY_STYLE_CAB
        try:
            cab = modelJson['cab']['title']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        return AttributeMetadata(metadataType=metadataType, value=cab)

    def _getSeating(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.BODY_STYLE_SEATING
        try:
            seating = modelJson['attributes']['seating']['value']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        return AttributeMetadata(metadataType=metadataType, value=seating)

    def _getMSRP(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.BODY_STYLE_BASE_MSRP
        try:
            msrpStr = modelJson['attributes']['msrp']['value']  # ex "$101,500"
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        if msrpStr:
            msrp = util.priceStrToInt(msrpStr)
        return AttributeMetadata(metadataType=metadataType, value=msrp, units="$")