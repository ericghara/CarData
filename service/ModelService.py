from sqlalchemy import select, desc, delete

from repository.dto import Model as ModelDto
from typing import *
from datetime import date
from repository.Entities import Model, Brand, Manufacturer
from BrandService import brandService
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

class ModelService:

    def __init__(self):
        self.table = Model.__table__

    def _getBrand(self, manufacturerCommon: str, brandName: str, session: 'Session') -> 'Brand':
        brand = brandService.getBrand(manufacturerCommon, brandName, session)
        if not brand:
            raise ValueError(f'Could not find brand matching manufacturer common name: {manufacturerCommon}, brand name {brandName}')
        return brand

    # Retrieves all models from specified year for a specific brand
    def getModelYear(self, manufacturerCommon: str, brandName: str, modelYear: 'date', session: 'Session') -> List['Model']:
        stmt = select(Model).outerjoin(Brand).outerjoin(Manufacturer).where(
            Manufacturer.common_name == manufacturerCommon, Brand.name == brandName, Model.model_year == modelYear) \
            .order_by(Model.name)
        return session.scalars(stmt)

    def getModelByBrandNameModelNameModelYear(self, brandName: str, modelName: str, modelYear: date, session: 'Session') -> 'Model':
        stmt = select(Model).outerjoin(Brand).where(
            brandName == Brand.name, modelName == Model.name, modelYear == Model.model_year)
        return session.scalars(stmt).one()

    def getMostRecentModel(self, brandName: str, modelName: str, session: 'Session') -> 'Model':
        stmt = select(Model).outerjoin(Brand).where(
            brandName == Brand.name, modelName == Model.name).order_by(desc(Model.model_year) ).limit(1)
        return session.scalars(stmt).one()

    def getModelsByBrandNameAndModelName(self, brandName: str, modelName: str, session: 'Session') -> List['Model']:
        stmt = select(Model).outerjoin(Brand).where(
            brandName == Brand.name, modelName == Model.name).order_by(desc(Model.model_year))
        return session.scalars(stmt)

    # Does not cascade.  Will raise if orphans would be created.
    def deleteModelByBrandNameModelNameModelYear(self, brandName: str, modelName: str, modelYear: 'date', session: Session) -> None:
        stmt = delete(Model).outerjoin(Brand).where(
            brandName == Brand.name, modelName == Model.name, modelYear == Model.model_year)
        session.execute(stmt)

    def upsert(self, records : List['ModelDto'], session: 'Session') -> Generator['ModelDto']:
        insertStmt = insert(self.table).values([vars(dto) for dto in records])
        # set in on conflict is redundant, it's just so the row is 'modified', allowing it to be returned
        # based on the model_no_dupes constraint the NEW model_year must match the OLD model_year
        updateStmt = insertStmt.on_conflict_do_update(
            constraint='model_no_dups', set_={'model_year':insertStmt.excluded.model_year}).returning(Model)
        for modelRecord in session.execute(updateStmt):
            yield ModelDto(**modelRecord)

modelService = ModelService()





