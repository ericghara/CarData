import logging
from typing import List

from common.domain.dto.AttributeDto import AttributeDto
from common.domain.dto.RawDataDto import RawDataDto
from transformer.transform.Transformer import Transformer
from transformer.transform.toyota.parser.LoggingTools import LoggingTools


class GmTransformer(Transformer):
    def __init__(self):
        super().__init__(manufacturerCommon='GM', brandNames=['Buick', 'Cadillac', 'Chevrolet', 'GMC'])
        self.log = logging.getLogger(self.__class__.__name__)
        self.loggingTools = LoggingTools(logger=self.log)
        self.parsers = []

    def transform(self, rawDataDto: RawDataDto) -> List[AttributeDto]:
        jsonData = rawDataDto.rawData
        self._assertValidJsonData(jsonData)
        attributes = list()
        for parser in self.parsers:
            try:
                attributes.extend(parser.parse(jsonData))
            except Exception as e:
                self.loggingTools.logParserFailure(transformer=type(self), parser=type(parser), exception=e)
        return attributes
