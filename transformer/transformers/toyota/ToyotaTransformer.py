import logging
from typing import Dict

from transformer.Transformer import Transformer
from transformer.attribute_dto.AttributeDto import *
from transformer.transformers.toyota.LoggingTools import LoggingTools


class ToyotaTransformer(Transformer):

    def __init__(self):
        super().__init__(manufacturerCommon="toyota", brandNames={"toyota", "Lexus"})
        self.log = logging.getLogger(self.__class__.__name__)
        self.loggingTools = LoggingTools(logger=self.log)

    def transform(self, jsonData: Dict) -> List[AttributeDto]:
        pass