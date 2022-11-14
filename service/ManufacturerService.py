from typing import *
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from repository.Entities import Manufacturer

class ManufacturerService:

    def __init__(self):
        pass

    def getManufacturerByCommonName(self, commonName: str, session: 'Session') -> 'Manufacturer':
        query = session.query(Manufacturer).where(Manufacturer.common_name == commonName)
        return query.first()

    def getAllManufacturers(self, session: 'Session') -> Iterator['Manufacturer']:
        query = session.query(Manufacturer)
        return query

    def deleteManufacturerByCommonName(self, commonName: str, session: 'Session') -> None:
        toDel = self.getManufacturerByCommonName(commonName, session)
        session.delete(toDel)

    def deleteAllManufacturers(self, session: 'Session') -> None:
        for manufacturer in self.getAllManufacturers(session):
            session.delete(manufacturer)


manufacturerService = ManufacturerService()







