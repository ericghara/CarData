from typing import *
from uuid import UUID

from sqlalchemy.orm import Session

from common.domain.entities import Manufacturer


class ManufacturerRepository:

    def __init__(self):
        pass

    def getManufacturerByCommonName(self, commonName: str, session: 'Session') -> 'Manufacturer':
        query = session.query(Manufacturer).where(Manufacturer.common_name == commonName)
        return query.first()

    def getManufacturerById(self, manufacurerId: UUID, session: Session):
        query = session.query(Manufacturer).where(Manufacturer.manufacturer_id == manufacurerId)
        return query.first()

    def getAllManufacturers(self, session: 'Session') -> Iterator['Manufacturer']:
        query = session.query(Manufacturer)
        return query

    def deleteManufacturerByCommonName(self, commonName: str, session: 'Session') -> None:
        toDel = self.getManufacturerByCommonName(commonName, session)
        if not toDel:
            raise ValueError(f'No record found with Manufacturer Common Name: {commonName}')
        session.delete(toDel)

    def deleteAllManufacturers(self, session: 'Session') -> None:
        for manufacturer in self.getAllManufacturers(session):
            session.delete(manufacturer)


manufacturerRepository = ManufacturerRepository()







