import logging
from typing import List

from common.domain.dto.AttributeDto import AttributeDto, Accessory, Package
from common.domain.dto.RawDataDto import RawDataDto
from transformer.transform.Transformer import Transformer
from transformer.transform.toyota.parser.LoggingTools import LoggingTools
from transformer.transform.toyota.parser.AccessoryParser import AccessoryParser
from transformer.transform.toyota.parser.BodyStyleParser import BodyStyleParser
from transformer.transform.toyota.parser.DriveParser import DriveParser
from transformer.transform.toyota.parser.EngineParser import EngineParser
from transformer.transform.toyota.parser.ExteriorColorParser import ExteriorColorParser
from transformer.transform.toyota.parser.GradeParser import GradeParser
from transformer.transform.toyota.parser.InteriorColorParser import InteriorColorParser
from transformer.transform.toyota.parser.PackageParser import PackageParser
from transformer.transform.toyota.parser.TransmissionParser import TransmissionParser


class ToyotaTransformer(Transformer):

    def __init__(self):
        super().__init__(manufacturerCommon='Toyota', brandNames=['Toyota', "Lexus"])
        self.log = logging.getLogger(self.__class__.__name__)
        self.loggingTools = LoggingTools(logger=self.log)
        self.parsers = [EngineParser(self.loggingTools), TransmissionParser(self.loggingTools),
                        DriveParser(self.loggingTools), BodyStyleParser(self.loggingTools),
                        GradeParser(self.loggingTools), PackageParser(self.loggingTools),
                        InteriorColorParser(self.loggingTools), ExteriorColorParser(self.loggingTools),
                        AccessoryParser(self.loggingTools)]

    def transform(self, rawDataDto: RawDataDto) -> List[AttributeDto]:
        jsonData = rawDataDto.rawData
        self._assertValidJsonData(jsonData)
        attributes = list()
        for parser in self.parsers:
            try:
                attributes.extend(parser.parse(jsonData))
            except Exception as e:
                self.loggingTools.logParserFailure(transformer=type(self), parser=type(parser), exception=e)
        return self._deDupAccessoryPackage(attributes)

    def _deDupAccessoryPackage(self, attributes: List[AttributeDto]):
        """
        Packages are often dual listed as accessories and Grades by Toyota. This method,
        strips all accessories that are also listed in packages
        :return:
        """
        otherAttributes = list()
        accessoryGradeByTitle = dict()
        for attribute in attributes:
            if isinstance(attribute, (Accessory, Package) ):
                if isinstance(accessoryGradeByTitle.get(attribute.title, None), (type(None), Accessory) ):
                    accessoryGradeByTitle[attribute.title] = attribute
            else:
                otherAttributes.append(attribute)
        return otherAttributes + list(accessoryGradeByTitle.values())
