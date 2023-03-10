from abc import ABC
from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID

from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.AttributeType import AttributeType


class AttributeDto(ABC):
    """
    Is a DTO for Model Attributes.  The `metadata` consists of ``AttributeMetadata`` objects which are JSON
    serializable allowing straightforward conversion to a ``ModelAttribute`` entity.
    """

    def __init__(self, title: str, attributeId: Optional[UUID] = None, modelId: Optional[UUID] = None,
                 metadata: Optional[List[AttributeMetadata]] = None, updatedAt: Optional[datetime] = None):
        self.attributeId = attributeId
        self.title = title
        self.modelId = modelId
        self.metadata = metadata
        self.updatedAt = updatedAt

    def __eq__(self, other: Any) -> bool:
        """
        Only ``attribute_type`` and ``title`` are significant for equality
        :param other:
        :return:
        """
        if not type(self) == type(other):
            return False
        return self.attributeId == other.attributeId and self.title == other.title and self.modelId == other.modelId and self.updatedAt == other.updatedAt

    def _assertStrictEq(self, other: Any) -> None:
        """
        For testing.  An equals implementation that compares all instance variables.
        :param other:
        :return:
        """
        if not type(self) == type(other):
            raise AssertionError(f"AttributeType: {type(self)} != {type(other)}")
        if self.attributeId != other.attributeId:
            raise AssertionError(f"attributeId: {self.attributeId} != {other.attributeId}")
        if self.title != other.title:
            raise AssertionError(f"Title: {self.title} != {other.title}")
        if self.modelId != other.modelId:
            raise AssertionError(f"modelId: {self.modelId} != {other.modelId}")
        if self.updatedAt != other.updatedAt:
            raise AssertionError(f"modelId: {self.updatedAt} != {other.updatedAt}")
        if self.metadata is None or other.metadata is None:
            if (self.metadata is None and other.metadata) or (self.metadata and other.metadata is None):
                raise AssertionError(f"Metadata: {str(self.metadata)} != {str(other.metadata)}")
            return None
        if set(self.metadata) != set(other.metadata):
            raise AssertionError(f"Metadata: {self.metadata} != {other.metadata}")

    def __hash__(self) -> int:
        """
        Only ``attribute_type`` and ``title`` are hashed (similar to ``__eq__``)
        :return:
        """
        return hash((type(self), self.attributeId, self.title, self.modelId, self.updatedAt))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.title})"

    def __str__(self):
        return f"{type(self).__name__}: {self.title}\n" \
               f"\t{self.metadata}"


class Engine(AttributeDto):

    def __init__(self, title: str, attributeId: Optional[UUID] = None, modelId: Optional[UUID] = None,
                 metadata: Optional[List[AttributeMetadata]] = None, updatedAt: Optional[datetime] = None):
        super().__init__(title=title, attributeId=attributeId, modelId=modelId, metadata=metadata, updatedAt=updatedAt)


class Transmission(AttributeDto):

    def __init__(self, title: str, attributeId: Optional[UUID] = None, modelId: Optional[UUID] = None,
                 metadata: Optional[List[AttributeMetadata]] = None, updatedAt: Optional[datetime] = None):
        super().__init__(title=title, attributeId=attributeId, modelId=modelId, metadata=metadata, updatedAt=updatedAt)


class Drive(AttributeDto):

    def __init__(self, title: str, attributeId: Optional[UUID] = None, modelId: Optional[UUID] = None,
                 metadata: Optional[List[AttributeMetadata]] = None, updatedAt: Optional[datetime] = None):
        super().__init__(title=title, attributeId=attributeId, modelId=modelId, metadata=metadata, updatedAt=updatedAt)


class BodyStyle(AttributeDto):

    def __init__(self, title: str, attributeId: Optional[UUID] = None, modelId: Optional[UUID] = None,
                 metadata: Optional[List[AttributeMetadata]] = None, updatedAt: Optional[datetime] = None):
        super().__init__(title=title, attributeId=attributeId, modelId=modelId, metadata=metadata, updatedAt=updatedAt)


class Grade(AttributeDto):

    def __init__(self, title: str, attributeId: Optional[UUID] = None, modelId: Optional[UUID] = None,
                 metadata: Optional[List[AttributeMetadata]] = None, updatedAt: Optional[datetime] = None):
        super().__init__(title=title, attributeId=attributeId, modelId=modelId, metadata=metadata, updatedAt=updatedAt)


class Package(AttributeDto):

    def __init__(self, title: str, attributeId: Optional[UUID] = None, modelId: Optional[UUID] = None,
                 metadata: Optional[List[AttributeMetadata]] = None, updatedAt: Optional[datetime] = None):
        super().__init__(title=title, attributeId=attributeId, modelId=modelId, metadata=metadata, updatedAt=updatedAt)


class InteriorColor(AttributeDto):

    def __init__(self, title: str, attributeId: Optional[UUID] = None, modelId: Optional[UUID] = None,
                 metadata: Optional[List[AttributeMetadata]] = None, updatedAt: Optional[datetime] = None):
        super().__init__(title=title, attributeId=attributeId, modelId=modelId, metadata=metadata, updatedAt=updatedAt)


class ExteriorColor(AttributeDto):

    def __init__(self, title: str, attributeId: Optional[UUID] = None, modelId: Optional[UUID] = None,
                 metadata: Optional[List[AttributeMetadata]] = None, updatedAt: Optional[datetime] = None):
        super().__init__(title=title, attributeId=attributeId, modelId=modelId, metadata=metadata, updatedAt=updatedAt)


class Accessory(AttributeDto):

    def __init__(self, title: str, attributeId: Optional[UUID] = None, modelId: Optional[UUID] = None,
                 metadata: Optional[List[AttributeMetadata]] = None, updatedAt: Optional[datetime] = None):
        super().__init__(title=title, attributeId=attributeId, modelId=modelId, metadata=metadata, updatedAt=updatedAt)


class Option(AttributeDto):

    def __init__(self, title: str, attributeId: Optional[UUID] = None, modelId: Optional[UUID] = None,
                 metadata: Optional[List[AttributeMetadata]] = None, updatedAt: Optional[datetime] = None):
        super().__init__(title=title, attributeId=attributeId, modelId=modelId, metadata=metadata, updatedAt=updatedAt)


class Other(AttributeDto):

    def __init__(self, title: str, attributeId: Optional[UUID] = None, modelId: Optional[UUID] = None,
                 metadata: Optional[List[AttributeMetadata]] = None, updatedAt: Optional[datetime] = None):
        super().__init__(title=title, attributeId=attributeId, modelId=modelId, metadata=metadata, updatedAt=updatedAt)


# registry for mapping AttributeType and corresponding AttributeDto
attributeDtoToAttributeType = {
    Engine: AttributeType.ENGINE,
    Transmission: AttributeType.TRANSMISSION,
    Drive: AttributeType.DRIVE,
    BodyStyle: AttributeType.BODY_STYLE,
    Grade: AttributeType.GRADE,
    Package: AttributeType.PACKAGE,
    InteriorColor: AttributeType.INTERIOR_COLOR,
    ExteriorColor: AttributeType.EXTERIOR_COLOR,
    Accessory: AttributeType.ACCESSORY,
    Option: AttributeType.OPTION,
    Other: AttributeType.OTHER
}

# inverse mapping of attributeDtoToAttributeType
attributeTypeToAttributeDto = {attributeType: attributeDto for attributeDto, attributeType in
                               attributeDtoToAttributeType.items()}
