from collections import deque
from typing import List, Optional

from common.domain.dto.AttributeDto import AttributeDto
from common.domain.dto.RawDataDto import RawDataDto
from transformer.transformer.Transformer import Transformer


class MockTransformer(Transformer):

    def __init__(self, transformReturnValues: List[List[AttributeDto]] = None, manufacturerCommon: str = 'manufacturer',
                 brandNames: Optional[List[str]] = None):
        super().__init__(manufacturerCommon=manufacturerCommon, brandNames=brandNames or ["brand"])
        self.returnValues = deque()
        self.calledWith = list()  # List[RawDataDto]
        self.addReturnValues(transformReturnValues)

    def addReturnValues(self, returnValues: Optional[List[List[AttributeDto]]]):
        for returnValue in (returnValues or list()):
            self.returnValues.appendleft(returnValue)

    def transform(self, rawDataDto: RawDataDto) -> List[AttributeDto]:
        self.calledWith.append(rawDataDto)
        if not self.returnValues:
            raise AssertionError("Out of return values.  Called too many times?")
        return self.returnValues.pop()
