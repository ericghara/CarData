from dataclasses import dataclass
from datetime import date
from uuid import UUID

#These are simple objects. They are not DB proxies like entities


@dataclass
class Model:

    name: str
    model_year: 'date'
    brand_id: str
    model_id: UUID = None

