from repository.Entities import entities
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from ManufacturerService import manufacturerService


class BrandService:
    def __init__(self):
        pass

    def _getManufacturer(self, manufacturerCommon: str, session: 'Session') -> 'Manufacturer':
        manufacturer = manufacturerService.getManufacturerByCommonName(manufacturerCommon, session)
        if not manufacturer:
            raise ValueError('Manufacturer Common name not found.')
        return manufacturer

    def getBrandByNameAndManufacturer(self, manufacturerCommon: str, brandName: str, session: 'Session') -> 'Brand':
        stmt = select(entities.Brand).outerjoin(entities.Manufacturer).where(
            entities.Manufacturer.common_name == manufacturerCommon, entities.Brand.name == brandName)
        return session.scalars(stmt).one()

    def getBrandByName(self, brandName: str, session: 'Session') -> 'Brand':
        stmt = select(entities.Brand).where(entities.Brand.name == brandName)
        return session.scalars(stmt).one()

    # raises on duplicate manufacturer or brand
    def insertBrand(self, manufacturerCommon: str, brand: 'Brand', session: 'Session') -> None:
        manufacturer = self._getManufacturer(manufacturerCommon, session)
        manufacturer.brands.append(brand)
        return

    def deleteBrand(self, name: str, session: 'Session') -> None:
        stmt = delete(entities.Brand).where(entities.Brand.name == name)
        session.execute(stmt)
        return

brandService = BrandService()





