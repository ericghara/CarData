from abc import ABC
from typing import Type, Dict, Any


class ObjectMapper(ABC):

    objectType: Type

    def map(self, jsonDict: Dict)-> Any:
        pass

    def getObjectType(self) -> Type:
        return self.objectType