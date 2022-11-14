from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from repository.Entities import Brand,Manufacturer

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
        query = session.query(Brand).outerjoin(Manufacturer).where(
            Manufacturer.common_name == manufacturerCommon, Brand.name == brandName)
        return query.one()

    def getBrandByName(self, brandName: str, session: 'Session') -> 'Brand':
        query = session.query(Brand).where(Brand.name == brandName)
        return query.one()

    # raises on duplicate manufacturer or brand
    def insertBrand(self, manufacturerCommon: str, brand: 'Brand', session: 'Session') -> None:
        manufacturer = self._getManufacturer(manufacturerCommon, session)
        manufacturer.brands.append(brand)
        return

    def deleteBrand(self, name: str, session: 'Session') -> None:
        stmt = delete(Brand).where(Brand.name == name)
        session.execute(stmt)
        return

brandService = BrandService()





