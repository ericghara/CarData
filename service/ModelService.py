import uuid

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
        brand = brandService.getBrandByNameAndManufacturer(manufacturerCommon, brandName, session)
        if not brand:
            raise ValueError(f'Could not find brand matching manufacturer common name: {manufacturerCommon}, brand name {brandName}')
        return brand

    # Retrieves all models from specified year for a specific brand sorted by Model Name
    def getModelYear(self, manufacturerCommon: str, brandName: str, modelYear: 'date', session: 'Session') -> Iterator['Model']:
            return session.query(Model).outerjoin(Brand).outerjoin(Manufacturer)\
                .where(Manufacturer.common_name == manufacturerCommon, Brand.name == brandName, Model.model_year == modelYear)\
                .order_by(Model.name)


    def getModelByBrandNameModelNameModelYear(self, brandName: str, modelName: str, modelYear: date, session: 'Session') -> 'Model':
        query = session.query(Model).outerjoin(Brand).where(
            brandName == Brand.name, modelName == Model.name, modelYear == Model.model_year)
        return query.first()

    def getMostRecentModel(self, brandName: str, modelName: str, session: 'Session') -> 'Model':
        stmt = select(Model).outerjoin(Brand).where(
            brandName == Brand.name, modelName == Model.name).order_by(desc(Model.model_year) ).limit(1)
        return session.scalars(stmt).one()

    def getModelsByBrandNameAndModelName(self, brandName: str, modelName: str, session: 'Session') -> List['Model']:
        query = session.query(Model).outerjoin(Brand).where(
            brandName == Brand.name, modelName == Model.name).order_by(desc(Model.model_year))
        return query

    def deleteModelByBrandNameModelNameModelYear(self, brandName: str, modelName: str, modelYear: 'date', session: Session) -> None:
        toDel = self.getModelByBrandNameModelNameModelYear(
            brandName=brandName, modelName=modelName, modelYear=modelYear, session=session)
        if not toDel:
            raise ValueError(f'Could not locate a model matching the Brand Name: {brandName}, '
                             f'Model Name {modelName} and Model Year {modelYear}')
        session.delete(toDel)

    def upsert(self, records : List['ModelDto'], session: 'Session') -> Iterator['ModelDto']:
        models = list()
        for record in records:
            if record.model_id is None:
                record.model_id = str(uuid.uuid4() )
                models.append(vars(record) )
        insertStmt = insert(self.table).values(models)
        # set in on conflict is redundant, it's just so the row is 'modified', allowing it to be returned
        # based on the model_no_dupes constraint the NEW model_year must match the OLD model_year
        updateStmt = insertStmt.on_conflict_do_update(
            constraint='model_no_dups', set_={'model_year':insertStmt.excluded.model_year}).returning(Model)
        for modelRecord in session.execute(updateStmt):
            yield ModelDto(**modelRecord)

modelService = ModelService()





