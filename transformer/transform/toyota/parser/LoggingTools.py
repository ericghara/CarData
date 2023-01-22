import logging
from typing import Dict, Optional

from common.domain.dto.AttributeDto import AttributeDto
from common.domain.enum.MetadataType import MetadataType


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

    def logTitleFailure(self, parser: type, exception: Exception, modelJson: Dict) -> None:
        self.log.debug(f"Failure to parse title: {parser.__name__} for model {self._getModelName(modelJson)}")
        self.log.debug(f"Error message:\n", exception.__cause__)

    def logNoAttributes(self, parser: type) -> None:
        self.log.debug(f"No Attributes found for {parser.__name__}")

    def logDuplicateAttributeDto(self, parser: type, attributeDto: AttributeDto) -> None:
        self.log.debug(f"{parser.__name__} - duplicate attribute for {attributeDto}")

    def logDebug(self, message: str, parser: Optional[type] = "Unknown Transformer", modelJson: Optional[Dict] = None):
        if not modelJson:
            modelName = "Unknown Model"
        modelName = self._getModelName(modelJson)
        self.log.debug(f"{parser.__name__} : {modelName} - {message}")

    def logParserFailure(self, transformer: type, parser: type, exception: Exception) -> None:
        logging.info(f"{transformer.__name__} - {parser.__name__} ")
        logging.debug("Parser Failure:\n", exc_info=exception)
