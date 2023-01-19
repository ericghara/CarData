from datetime import date
from unittest import TestCase

from common.domain.converter.Converter import converter
from common.domain.dto.AttributeDto import AttributeDto, Accessory, Grade, BodyStyle
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.dto.RawDataDto import RawDataDto
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from common.repository.Entities import Manufacturer, Brand, Model, RawData
from common.repository.SessionFactory import sessionFactory
from common.repository.test_common.DbContainer import DbContainer
from common.service.persistence.ModelAttributeService import modelAttributeService
from common.service.persistence.ModelService import modelService
from transformer.service.TransformerService import transformerService


class TestEndToEnd(TestCase):
    container: DbContainer = None

    @classmethod
    def setUpClass(cls):
        cls.container = DbContainer()
        cls.container.start()
        cls.container.initTables()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.container.stop()

    def setUp(self):
        self.insertData()

    def tearDown(self) -> None:
        self.container.deleteAll()
        self.rawDataDto = None

    def insertData(self) -> None:
        with sessionFactory.newSession() as session:
            # manufacturer
            toyotaManufacturer = Manufacturer(official_name='Toyota Motor Company', common_name='Toyota')
            # brands
            toyotaBrand = Brand(name='Toyota', manufacturer=toyotaManufacturer)
            lexusBrand = Brand(name='Lexus', manufacturer=toyotaManufacturer)
            session.add(toyotaBrand)
            # models
            camry2023 = Model(name='Camry', model_year=date(2023, 1, 1), brand=toyotaBrand)
            camry2023Data = RawData(model=camry2023, raw_data={'fake': True})
            session.add_all([toyotaManufacturer, toyotaBrand, lexusBrand, camry2023, camry2023Data])
            session.commit()

    def test_ToyotaBrandTransformToDatabaseDestination(self):
        raw_data = {"model": [{"accessories": [
            {"title": "Touring Package",
             "price": "$2,540",
             "attributes": {"group": {"value": "Exterior"}}}]}]}
        with sessionFactory.newSession() as session:
            camry = modelService.getModelByBrandNameModelNameModelYear(brandName='Toyota', modelName="Camry",
                                                                       modelYear=date(2023, 1, 1), session=session)
            camryRawData = RawData(raw_data=raw_data, model=camry)
            session.add(camryRawData)
            session.commit()
            rawDataDto = converter.convert(camryRawData, RawDataDto)
        transformerService.transform(rawDataDto)
        with sessionFactory.newSession() as session:
            modelAttributes = list(
                modelAttributeService.getAttributesByModelId(modelId=rawDataDto.modelId, session=session))
            attributeDtos = [converter.convert(obj=modelAttribute, outputType=AttributeDto) for modelAttribute in
                             modelAttributes]
        # There are some default attributes
        self.assertEqual(3, len(attributeDtos), "expected number of attributes")
        foundAccessoryByType = {type(attributeDto): attributeDto for attributeDto in attributeDtos}
        expectedAccessory = Accessory(title="Touring Package", metadata=[
            AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=2540, unit=MetadataUnit.DOLLARS),
            AttributeMetadata(metadataType=MetadataType.ACCESSORY_CATEGORY, value="Exterior")
        ])
        expectedAccessory._assertStrictEq(foundAccessoryByType.get(Accessory))
        Grade("Standard")._assertStrictEq(foundAccessoryByType.get(Grade))
        BodyStyle("Standard")._assertStrictEq(foundAccessoryByType.get(BodyStyle))
