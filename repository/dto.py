from dataclasses import dataclass
from datetime import date
from uuid import UUID

#These are simple objects. They are not DB proxies like entities


@dataclass
class Model:

    def __init__(self, name: str, model_year: 'date', brand_id: str, model_id: UUID = None):
        self.model_id = model_id
        self.name = name
        self.model_year = model_year
        self.brand_id = brand_id
