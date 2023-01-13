from abc import ABC
from typing import List, Optional, Any

from repository.AttributeType import AttributeType
from transformer.common.dto.AttributeMetadata import AttributeMetadata


class AttributeDto(ABC):
    """
    Is a DTO for Model Attributes.  The `metadata` consists of ``AttributeMetadata`` objects which are JSON
    serializable allowing straightforward conversion to a ``ModelAttribute`` entity.
    """

    def __init__(self, attributeType: AttributeType, title: str, metadata: Optional[List[AttributeMetadata]] = None):
        self.attributeType = attributeType
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
        return self.attributeType == other.attributeType and self.title == other.title

    def _assertStrictEq(self, other: Any) -> None:
        """
        For testing.  An equals implementation that compares all instance variables.
        :param other:
        :return:
        """
        if self.attributeType != other.attributeType:
            raise AssertionError(f"AttributeType: {self.attributeType} != {other.attributeType}")
        if self.title != other.title:
            raise AssertionError(f"Title: {self.title} != {other.title}")
        if self.metadata is None or other.metadata is None:
            return self.metadata is None and other.metadata is None
        if set(self.metadata) != set(other.metadata):
            raise AssertionError(f"Metadata: {self.metadata} != {other.metadata}")

    def __hash__(self) -> int:
        """
        Only ``attribute_type`` and ``title`` are hashed (similar to ``__eq__``)
        :return:
        """
        return hash((self.attributeType, self.title))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.attributeType}, {self.title})"

    def __str__(self):
        return f"{self.attributeType.value}: {self.title}\n" \
               f"\t{self.metadata}"


class Engine(AttributeDto):

    def __init__(self, title: str, metadata: List[AttributeMetadata] = None):
        super().__init__(attributeType=AttributeType.ENGINE, title=title, metadata=metadata)


class Transmission(AttributeDto):

    def __init__(self, title: str, metadata: List[AttributeMetadata] = None):
        super().__init__(attributeType=AttributeType.TRANSMISSION, title=title, metadata=metadata)

    def __dict__(self):
        return {'title' : self.title, 'metadata' : self.metadata}


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


class Accessory(AttributeDto):

    def __init__(self, title: str, metadata: List[AttributeMetadata] = None):
        super().__init__(attributeType=AttributeType.ACCESSORY, title=title, metadata=metadata)


class Other(AttributeDto):

    def __init__(self, title: str, metadata: List[AttributeMetadata] = None):
        super().__init__(attributeType=AttributeType.OTHER, title=title, metadata=metadata)
