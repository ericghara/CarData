from abc import ABC, abstractmethod
from typing import Dict, List, Set

from transformer.attribute_dto.AttributeDto import AttributeDto


class Transformer(ABC):

    def __init__(self, manufacturerCommon: str, brandNames: Set[str]):
        self.manufacturerCommon = manufacturerCommon
        self.brandNames = brandNames

    def _assertValidJsonData(self, jsonData: Dict) -> None:
        if not jsonData:
            raise ValueError("jsonData was None or Empty.")

    @abstractmethod
    def transform(self, jsonData: Dict) -> List[AttributeDto]:
        pass

    def getManufacturerCommon(self) -> str:
        return self.manufacturerCommon

    def canTransform(self, brandName) -> bool:
        return brandName in self.brandNames

