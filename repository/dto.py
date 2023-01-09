from dataclasses import dataclass
from datetime import date
from typing import Optional, Dict
from uuid import UUID
from repository.DataTypes import AttributeType

# These are simple objects. They are not DB proxies like entities

@dataclass
class Model:
    name: str
    model_year: 'date'
    brand_id: str = None  # Optional
    model_id: UUID = None  # Optional



