from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from repository.Entities import entities


class ManufacturerService:

    def __init__(self):
        pass

    def getManufacturerByCommonName(self, commonName: str, session: 'Session') -> 'Manufacturer':
        stmt = select(entities.Manufacturer).where(entities.Manufacturer.common_name == commonName)
        return session.execute(stmt).fetchOne()

    def insertManufacturer(self, manufacturer: 'Manufacturer', session: 'Session') -> None:
        session.add(manufacturer)
        return

    # Not a cascading delete
    # Will raise error if there are child brands due to fk_constraint
    def deleteManufacturer(self, commonName: str, session: 'Session') -> None:
        stmt = delete(entities.Manufacturer).where(entities.Manufacturer.common_name == commonName)
        session.execute(stmt)

manufacturerService = ManufacturerService()







