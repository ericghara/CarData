from abc import abstractmethod, ABC
from typing import Dict, List

from transformer.attribute_dto.AttributeDto import AttributeDto


class AttributeParser(ABC):

    @abstractmethod
    def parse(self, jsonData: Dict) -> List[AttributeDto]:
        """
        Parses attributes from a model's raw JSON data.  Each attribute
        parser should return a certain type of AttributeDto (i.e. ``Engine`` or ``Transmission``).
        A Transformer is therefore composed of many attribute parsers.
        :param jsonData:
        :return:
        """
        pass