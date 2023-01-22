import json
import logging
import uuid
from typing import Type, Dict, Optional

from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType


class LoggingTools:

    def __init__(self, logger: logging.Logger):
        self.log = logger

    def logNoAttributes(self, parser: Type, modelIdentifier: str):
        """
        :param parser:
        :param modelIdentifier: any str, typically something that can assist in identifying
        the model being parsed such as "{Year} {Brand} {Model}"
        :return:
        """
        self.log.info(f"No Attributes found for: {modelIdentifier} - {parser.__name__}")

    def logTitleFailure(self, parser: type, modelIdentifier: str):
        self.log.debug(f"Failure parsing title for: {modelIdentifier} - {parser.__name__}")

    def logtAttributeFailure(self, parser: type, modelIdentifier: str, metadataType: MetadataType):
        self.log.debug(f"Failure to metadata: {metadataType} from {parser.__name__}: {modelIdentifier} ")

    def logUnexpectedSchema(self, parser: type, modelIdentifier: str, exception: Optional[Exception]):
        self.log.warning(f"Encountered an unexpected RawData Schema: {modelIdentifier} - {parser.__name__}",
                         exc_info=exception)

    def getModelIdentifier(self, dataDict: Dict) -> str:
        """
        Return an identifier that can be used for logging (optimally human-readable,
        but non-readable and consistent as a fallback)
        :param dataDict:
        :return:
        """
        try:
            params = dataDict['config']['vsParams']
            paramsByName = {param['name']: param['value'] for param in params if
                            param['name'] in ("makes", "models", "years")}
            year = paramsByName['years']
            make = paramsByName['makes']
            model = paramsByName['models']
            return f"{year} - {make} {model}"
        except:
            # use hash as an id
            hashId = hash(json.dumps(dataDict))
            return f"Unknown - {hashId}"
