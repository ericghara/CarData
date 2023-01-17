import re
from typing import Dict, List, Optional

from common.domain.dto.AttributeDto import BodyStyle
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.common.attribute_set.AttributeSet import AttributeSet
from transformer.common.attribute_set.metadata_updater.implementation.PriceUpdater import PriceUpdater
from transformer.transformers.AttributeParser import AttributeParser
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser import util


class BodyStyleParser(AttributeParser):

    def __init__(self, loggingTools: LoggingTools):
        self.loggingTools = loggingTools

    def parse(self, jsonData: Dict) -> List[BodyStyle]:
        bodyStyleDtos = AttributeSet(updater=PriceUpdater(metadataType=MetadataType.COMMON_BASE_MSRP, keepLowest=True))
        for modelJson in jsonData['model']:
            bodyStyleDto = self._parseModel(modelJson)
            if bodyStyleDto in bodyStyleDtos:
                self.loggingTools.logDuplicateAttributeDto(parser=self.__class__, attributeDto=bodyStyleDto)
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
        if not re.search("bed", bed, re.IGNORECASE):
            # Toyota is inconsistent, sometimes bed title is "5-ft." others "5-ft. Bed"
            bed = f"{bed.strip()} Bed"
        return AttributeMetadata(metadataType=metadataType, value=util.removeBracketed(bed) )

    def _getCab(self, modelJson: Dict) -> Optional[AttributeMetadata]:
        metadataType = MetadataType.BODY_STYLE_CAB
        try:
            cab = modelJson['cab']['title']
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        if not cab:
            return None
        return AttributeMetadata(metadataType=metadataType, value=util.removeBracketed(cab) )

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
        metadataType = MetadataType.COMMON_BASE_MSRP
        try:
            msrpStr = modelJson['attributes']['msrp']['value']  # ex "$101,500"
        except KeyError as e:
            self.loggingTools.logMetadataFailure(metadataType=metadataType, exception=e, modelJson=modelJson)
            return None
        if not msrpStr:
            return None
        msrp = util.priceStrToInt(msrpStr)
        return AttributeMetadata(metadataType=metadataType, value=msrp, unit=MetadataUnit.DOLLARS)
