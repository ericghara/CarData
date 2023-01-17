import logging
from typing import Dict, List

from common.domain.dto.AttributeDto import AttributeDto, Accessory, Package
from common.domain.dto.modelDto import Model as ModelDto
from transformer.Transformer import Transformer
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser.AccessoryParser import AccessoryParser
from transformer.transformers.toyota.parser.BodyStyleParser import BodyStyleParser
from transformer.transformers.toyota.parser.DriveParser import DriveParser
from transformer.transformers.toyota.parser.EngineParser import EngineParser
from transformer.transformers.toyota.parser.ExteriorColorParser import ExteriorColorParser
from transformer.transformers.toyota.parser.GradeParser import GradeParser
from transformer.transformers.toyota.parser.InteriorColorParser import InteriorColorParser
from transformer.transformers.toyota.parser.PackageParser import PackageParser
from transformer.transformers.toyota.parser.TransmissionParser import TransmissionParser


class ToyotaTransformer(Transformer):

    def __init__(self):
        super().__init__(manufacturerCommon="toyota", brandNames={"toyota", "Lexus"})
        self.log = logging.getLogger(self.__class__.__name__)
        self.loggingTools = LoggingTools(logger=self.log)
        self.parsers = [EngineParser(self.loggingTools), TransmissionParser(self.loggingTools),
                        DriveParser(self.loggingTools), BodyStyleParser(self.loggingTools),
                        GradeParser(self.loggingTools), PackageParser(self.loggingTools),
                        InteriorColorParser(self.loggingTools), ExteriorColorParser(self.loggingTools),
                        AccessoryParser(self.loggingTools)]

    def transform(self, jsonData: Dict, modelDto: ModelDto) -> List[AttributeDto]:
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
