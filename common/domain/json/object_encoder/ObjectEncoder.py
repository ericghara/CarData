from abc import ABC, abstractmethod
from typing import Type, Any, Optional


class ObjectEncoder(ABC):
    objectType: Type
    jsonEncoder: Optional['jsonEncoder']

    @abstractmethod
    def toSerializable(self, object: Any) -> Any:  # returns a json serializable object Dict, List with primitive values
        pass

    # must make forward reference to JsonEncoder to avoid circular ref
    def setJsonEncoder(self, jsonEncoder: 'JsonEncoder') -> None:
        """
        Passes jsonEncoder so ``ObjectEncoder`` may encode nested complex objects
        :param jsonEncoder:
        :return:
        """
        self.jsonEncoder = jsonEncoder
