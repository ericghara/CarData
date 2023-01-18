import logging
from typing import List, Type, Callable, Dict, Any

from common.domain.json.object_mapper import ObjectMapper
from common.domain.json.object_mapper.AttributeMetadataMapper import AttributeMetadataMapper


class JsonDecoder:

    def __init__(self, objectMappers: List[ObjectMapper]):
        self.log = logging.getLogger(type(self).__name__)
        self._typeToMapper = dict()
        self._initMappers(objectMappers)

    def _initMappers(self, objectMappers: List[ObjectMapper]) -> None:
        for mapper in objectMappers:
            objectType = mapper.getObjectType()
            if (oldMapper := self._typeToMapper.get(objectType)):
                logging.warning(f"Mapping for {objectType} already exists.  Replacing {oldMapper} with {mapper}")
            self._typeToMapper[objectType] = mapper

    def getMappingFunction(self, objectType: Type) -> Callable[[Dict], Any]:
        try:
            return self._typeToMapper[objectType].map
        except KeyError:
            raise ValueError(f"Could not match {objectType} to a mapper.")

jsonDecoder = JsonDecoder(objectMappers=[AttributeMetadataMapper()])

