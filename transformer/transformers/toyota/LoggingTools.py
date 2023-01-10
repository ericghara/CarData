import logging
from typing import Dict

from transformer.attribute_dto.AttributeDto import *
from transformer.attribute_metadata.MetadataType import MetadataType


class LoggingTools:

    def __init__(self, logger: logging.Logger):
        self.log = logger

    def _getModelName(self, modelJson: Dict) -> Optional[str]:
        if not modelJson or not (title := modelJson.get('title')):
            self.log.debug("Could not parse Model['title']")
            return None
        return title

    def logMetadataFailure(self, metadataType: MetadataType, exception: Exception, modelJson: Dict) -> None:
        self.log.debug(f"Failure to parse: {metadataType.name} for model {self._getModelName(modelJson)}")
        self.log.debug(f"Error message:\n", exception.__cause__)

    def logTitleFailure(self, transformer: type, exception: Exception, modelJson: Dict) -> None:
        self.log.debug(f"Failure to parse title: {transformer.__name__} for model {self._getModelName(modelJson)}")
        self.log.debug(f"Error message:\n", exception.__cause__)

    def logNoAttributes(self, transformer: type) -> None:
        self.log.debug(f"No Attributes found for {transformer.__name__}")

    def logDuplicateAttributeDto(self, transformer: type, attributeDto: AttributeDto) -> None:
        self.log.debug(f"{transformer.__name__} - duplicate attribute for {attributeDto}")

    def logDebug(self, message: str, transformer: Optional[type] = "Unknown Transformer", modelJson: Optional[Dict] = None):
        if not modelJson:
            modelName = "Unknown Model"
        modelName = self._getModelName(modelJson)
        self.log.debug(f"{transformer.__name__} : {modelName} - {message}")
