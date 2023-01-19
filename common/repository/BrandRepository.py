from sqlalchemy.orm import Session

from common.domain.entities import Brand, Manufacturer
from common.repository.ManufacturerRepository import manufacturerRepository


class BrandRepository:
    def __init__(self):
        pass

    def _getManufacturer(self, manufacturerCommon: str, session: 'Session') -> 'Manufacturer':
        manufacturer = manufacturerRepository.getManufacturerByCommonName(manufacturerCommon, session)
        if not manufacturer:
            raise ValueError('Manufacturer Common name not found.')
        return manufacturer

    def getBrandByNameAndManufacturer(self, manufacturerCommon: str, brandName: str, session: 'Session') -> 'Brand':
        query = session.query(Brand).outerjoin(Manufacturer).where(
            Manufacturer.common_name == manufacturerCommon, Brand.name == brandName)
        return query.first()

    def getBrandByName(self, brandName: str, session: 'Session') -> 'Brand':
        query = session.query(Brand).where(Brand.name == brandName)
        return query.first()

    # raises on duplicate manufacturer or brand
    def insertBrand(self, manufacturerCommon: str, brand: 'Brand', session: 'Session') -> None:
        manufacturer = self._getManufacturer(manufacturerCommon, session)
        manufacturer.brands.append(brand)
        return

    def deleteBrandByName(self, name: str, session: 'Session') -> None:
        toDel = self.getBrandByName(name, session)
        if not toDel:
            raise ValueError(f'No records found for Brand name: {name}.')
        session.delete(toDel)
        return

brandRepository = BrandRepository()





