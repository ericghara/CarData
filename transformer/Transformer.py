from abc import ABC, abstractmethod
from typing import Dict, List

from common.domain.dto.AttributeDto import AttributeDto
from common.domain.dto.RawDataDto import RawDataDto


class Transformer(ABC):

    def __init__(self, manufacturerCommon: str, brandNames: List[str]):
        self.manufacturerCommon = manufacturerCommon
        self.brandNames = brandNames

    def _assertValidJsonData(self, jsonData: Dict) -> None:
        if not jsonData:
            raise ValueError("jsonData was None or Empty.")

    @abstractmethod
    def transform(self, rawDataDto: RawDataDto) -> List[AttributeDto]:
        pass

    def getManufacturerCommon(self) -> str:
        return self.manufacturerCommon

    def canTransform(self) -> List[str]:
        return self.brandNames

