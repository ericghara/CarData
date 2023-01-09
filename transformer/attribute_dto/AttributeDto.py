from abc import ABC
from typing import List, Optional, Any

from repository.DataTypes import AttributeType
from transformer.attribute_metadata.AttributeMetadata import AttributeMetadata


class AttributeDto(ABC):
    """
    Is a DTO for Model Attributes.  The `metadata` consists of ``AttributeMetadata`` objects which are JSON
    serializable allowing straightforward conversion to a ``ModelAttribute`` entity.
    """

    def __init__(self, attributeType: AttributeType, title: str, metadata: Optional[List[AttributeMetadata]] = None):
        if metadata is None:
            metadata = list()
        self.attribute_type = attributeType
        self.title = title
        self.metadata = metadata

    def __eq__(self, other: Any) -> bool:
        """
        Only ``attribute_type`` and ``title`` are significant for equality
        :param other:
        :return:
        """
        if not isinstance(other, self.__class__):
            return False
        return self.attribute_type == other.attribute_type and self.title == other.title

    def _allParamEq(self, other: Any) -> bool:
        """
        For testing.  An equals implementation that compares all instance variables.
        :param other:
        :return:
        """
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        """
        Only ``attribute_type`` and ``title`` are hashed (similar to ``__eq__``)
        :return:
        """
        return hash((self.attribute_type, self.title))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.attribute_type}, {self.title})"


class Engine(AttributeDto):

    def __init__(self, title: str, metadata: List[AttributeMetadata] = None):
        super().__init__(attributeType=AttributeType.ENGINE, title=title, metadata=metadata)


class Transmission(AttributeDto):

    def __init__(self, title: str, metadata: List[AttributeMetadata] = None):
        super().__init__(attributeType=AttributeType.TRANSMISSION, title=title, metadata=metadata)


class Drive(AttributeDto):

    def __init__(self, title: str, metadata: List[AttributeMetadata] = None):
        super().__init__(attributeType=AttributeType.DRIVE, title=title, metadata=metadata)


class BodyStyle(AttributeDto):

    def __init__(self, title: str, metadata: List[AttributeMetadata] = None):
        super().__init__(attributeType=AttributeType.BODY_STYLE, title=title, metadata=metadata)


class Grade(AttributeDto):

    def __init__(self, title: str, metadata: List[AttributeMetadata] = None):
        super().__init__(attributeType=AttributeType.GRADE, title=title, metadata=metadata)


class Package(AttributeDto):

    def __init__(self, title: str, metadata: List[AttributeMetadata] = None):
        super().__init__(attributeType=AttributeType.PACKAGE, title=title, metadata=metadata)


class InteriorColor(AttributeDto):

    def __init__(self, title: str, metadata: List[AttributeMetadata] = None):
        super().__init__(attributeType=AttributeType.INTERIOR_COLOR, title=title, metadata=metadata)


class ExteriorColor(AttributeDto):

    def __init__(self, title: str, metadata: List[AttributeMetadata] = None):
        super().__init__(attributeType=AttributeType.EXTERIOR_COLOR, title=title, metadata=metadata)


class Accessories(AttributeDto):

    def __init__(self, title: str, metadata: List[AttributeMetadata] = None):
        super().__init__(attributeType=AttributeType.ACCESSORIES, title=title, metadata=metadata)


class Other(AttributeDto):

    def __init__(self, title: str, metadata: List[AttributeMetadata] = None):
        super().__init__(attributeType=AttributeType.OTHER, title=title, metadata=metadata)
