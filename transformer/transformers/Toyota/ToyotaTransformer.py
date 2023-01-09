import logging
from typing import Dict

from transformer.Transformer import Transformer
from transformer.attribute_dto.AttributeDto import *
from transformer.transformers.Toyota.LoggingTools import LoggingTools


class ToyotaTransformer(Transformer):

    def __init__(self):
        super().__init__(manufacturerCommon="Toyota", brandNames={"Toyota", "Lexus"})
        self.log = logging.getLogger(self.__class__.__name__)
        self.loggingTools = LoggingTools(logger=self.log)

    def transform(self, jsonData: Dict) -> List[AttributeDto]:
        context = self.TransformContext(jsonData)

        return context.attributeDtos  # think about this, could also just directly return ModelAttributes
