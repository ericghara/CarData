from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict
from uuid import UUID


@dataclass
class RawDataDto:
    dataId: Optional[UUID]
    rawData: Optional[Dict]
    modelId: Optional[UUID]
    createdAt: Optional[datetime]