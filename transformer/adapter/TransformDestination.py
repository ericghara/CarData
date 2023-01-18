from abc import ABC, abstractmethod
from typing import List

from common.domain.dto.AttributeDto import AttributeDto
from common.domain.dto.RawDataDto import RawDataDto


class TransformDestination(ABC):

    @abstractmethod
    def accept(self, attributes: List[AttributeDto], rawDataDto: RawDataDto) -> None:
        pass