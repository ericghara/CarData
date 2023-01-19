from typing import List

from common.domain.dto.AttributeDto import AttributeDto
from common.domain.dto.RawDataDto import RawDataDto
from transformer.adapter.TransformDestination import TransformDestination


class MockDestination(TransformDestination):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.calledWith = list() # List[(List[AttributeDto], RawDataDto)]

    def accept(self, attributeDtos: List[AttributeDto], rawDataDto: RawDataDto) -> None:
        self.calledWith.append((attributeDtos, rawDataDto))




