from sqlalchemy import CheckConstraint, Column, Date, DateTime, ForeignKey, String, UniqueConstraint, text, Text, Enum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, declarative_base

from common.domain.enum.AttributeType import AttributeType

Base = declarative_base()

class Manufacturer(Base):
    __tablename__ = 'manufacturer'

    manufacturer_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"))
    official_name = Column(String(255), nullable=False, unique=True)
    common_name = Column(String(255), nullable=False, unique=True)

    brands = relationship('Brand', back_populates='manufacturer', cascade='all, delete-orphan')

class Brand(Base):
    __tablename__ = 'brand'

    brand_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"))
    manufacturer_id = Column(ForeignKey('manufacturer.manufacturer_id'), nullable=False)
    name = Column(String(255), nullable=False, unique=True)

    manufacturer = relationship('Manufacturer', back_populates='brands')
    models = relationship('Model', back_populates='brand', cascade='all, delete-orphan')

class Model(Base):
    __tablename__ = 'model'
    __table_args__ = (
        CheckConstraint("date_trunc('year'::text, (model_year)::timestamp with time zone) = model_year"),
        UniqueConstraint('brand_id', 'name', 'model_year')
    )

    model_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"))
    name = Column(String(255), nullable=False)
    model_year = Column(Date, nullable=False)
    brand_id = Column(ForeignKey('brand.brand_id'), nullable=False)

    brand = relationship('Brand', back_populates='models')
    raw_data = relationship('RawData', back_populates='model', cascade='all, delete-orphan')
    model_attribute = relationship('ModelAttribute', back_populates='model', cascade='all, delete-orphan')

class RawData(Base):
    __tablename__ = 'model_raw_config_data'
    __table_args__ = (
        UniqueConstraint('model_id', 'created_at'),
    )

    data_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"))
    raw_data = Column(JSONB(astext_type=Text()), nullable=False)
    model_id = Column(ForeignKey('model.model_id'), nullable=False)
    created_at = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    model = relationship('Model', back_populates='raw_data')

class ModelAttribute(Base):
    __tablename__ = 'model_attribute'
    __table_args__ = (
        UniqueConstraint('attribute_type', 'title', 'model_id'),
    )

    attribute_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"), nullable=False)
    attribute_type = Column(Enum(AttributeType), nullable=False)
    title = Column(Text, nullable=False)
    model_id = Column(ForeignKey('model.model_id'), nullable=False)
    attribute_metadata = Column(JSONB(astext_type=Text()), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    model = relationship('Model', back_populates='model_attribute')
