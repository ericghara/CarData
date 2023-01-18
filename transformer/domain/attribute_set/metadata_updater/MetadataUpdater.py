from abc import ABC, abstractmethod
from typing import List, Optional

from common.domain.dto.AttributeMetadata import AttributeMetadata


class MetadataUpdater(ABC):
    @abstractmethod
    def update(self, dictMetadata: Optional[List[AttributeMetadata]],
               newMetadata: Optional[List[AttributeMetadata]]) -> bool:
        """
        Return true if metadata should be updated to newMetadata, false if no update should be made (dict remains
        in current state)
        :param dictMetadata:
        :param newMetadata:
        :return:
        """
        pass
