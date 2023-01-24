import logging
from typing import List

from common.domain.dto.AttributeDto import AttributeDto
from common.domain.dto.RawDataDto import RawDataDto
from transformer.transform.Transformer import Transformer
from transformer.transform.gm.parser.AccessoryParser import AccessoryParser
from transformer.transform.gm.parser.BodyStyleParser import BodyStyleParser
from transformer.transform.gm.parser.DriveParser import DriveParser
from transformer.transform.gm.parser.EngineParser import EngineParser
from transformer.transform.gm.parser.OptionParser import OptionParser
from transformer.transform.gm.parser.PackageParser import PackageParser
from transformer.transform.gm.parser.TransmissionParser import TransmissionParser
from transformer.transform.gm.parser.colorParsers import InteriorColorParser, ExteriorColorParser
from transformer.transform.gm.parser.LoggingTools import LoggingTools


class GmTransformer(Transformer):
    def __init__(self):
        super().__init__(manufacturerCommon='GM', brandNames=['Buick', 'Cadillac', 'Chevrolet', 'GMC'])
        self.log = logging.getLogger(self.__class__.__name__)
        self.loggingTools = LoggingTools(logger=self.log)
        parserConstructors = [AccessoryParser, BodyStyleParser, InteriorColorParser,
                        ExteriorColorParser, DriveParser, EngineParser,
                        OptionParser, PackageParser, TransmissionParser]
        self.parsers = [parser(loggingTools=self.loggingTools) for parser in parserConstructors]

    def transform(self, rawDataDto: RawDataDto) -> List[AttributeDto]:
        dataDict = rawDataDto.rawData
        self._assertValidJsonData(dataDict)
        attributes = list()
        for parser in self.parsers:
            try:
                attributes.extend(parser.parse(dataDict))
            except Exception as e:
                self.loggingTools.logParserFailure(transformer=type(self), parser=type(parser), exception=e)
        return attributes
