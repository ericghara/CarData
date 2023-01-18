from abc import ABC, abstractmethod
from typing import Type


class TypeConverter(ABC):

    inputType: Type
    outputType: Type

    @abstractmethod
    def convert(self, object: 'inputType') -> 'outputType':
        pass

    def getInputType(self) -> Type:
        return self.inputType

    def getOutputType(self) -> Type:
        return self.outputType

