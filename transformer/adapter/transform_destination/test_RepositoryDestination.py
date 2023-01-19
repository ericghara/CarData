import uuid
from datetime import date, datetime
from unittest import TestCase

from common.domain.converter.Converter import converter
from common.domain.dto.AttributeDto import Grade, BodyStyle, Transmission
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.dto.RawDataDto import RawDataDto
from common.domain.enum.AttributeType import AttributeType
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from common.exception.IllegalArgumentError import IllegalArgumentError
from common.exception.IllegalStateError import IllegalStateError
from common.repository.Entities import Manufacturer, Brand, Model, RawData, ModelAttribute
from common.repository.SessionFactory import sessionFactory
from common.repository.test_common.DbContainer import DbContainer
from common.service.persistence.ModelAttributeService import modelAttributeService
from transformer.adapter.transform_destination.RepositoryDestination import RepositoryDestination


class IntegrationTestRepositoryDestination(TestCase):
    container: DbContainer = None
    rawDataDto: RawDataDto = None  # source for transformations

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
        self.destination = RepositoryDestination(overwriteExisting=False)

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
            self.rawDataDto = converter.convert(camry2023Data, RawDataDto)

    def tearDown(self) -> None:
        self.container.deleteAll()
        self.rawDataDto = None

    def test_acceptSingeAttributeNoMetadata(self):
        attributeDtos = [Grade(title="Grade")]
        self.destination.accept(attributeDtos=attributeDtos, rawDataDto=self.rawDataDto)
        with sessionFactory.newSession() as session:
            modelAttributes = list(
                modelAttributeService.getAttributesByModelId(modelId=self.rawDataDto.modelId, session=session))
            self.assertEqual(1, len(modelAttributes), "A single ModelAttribute record inserted to database")
            foundModelAttribute = modelAttributes[0]
            expectedModelAttribute = converter.convert(attributeDtos[0], ModelAttribute)
            self.assertEqual(expectedModelAttribute.title, foundModelAttribute.title, "Title")
            self.assertEqual(expectedModelAttribute.attribute_type, foundModelAttribute.attribute_type,
                             "attribute_type")
            self.assertEqual(self.rawDataDto.modelId, foundModelAttribute.model_id, "model_id")
            self.assertIsNone(foundModelAttribute.attribute_metadata, "attribute_metadata must be None")
            self.assertTrue(isinstance(foundModelAttribute.updated_at, datetime), "updated at must be datetime type")
            self.assertTrue(isinstance(foundModelAttribute.attribute_id, str), "attribute_id must be a str")

    def test_acceptSingleAttributeWithMetadata(self):
        attributeDtos = [BodyStyle(title="BodyStyle",
                                   metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_BASE_MSRP,
                                                               value=30_000, unit=MetadataUnit.DOLLARS)])]
        self.destination.accept(attributeDtos=attributeDtos, rawDataDto=self.rawDataDto)
        with sessionFactory.newSession() as session:
            modelAttributes = list(
                modelAttributeService.getAttributesByModelId(modelId=self.rawDataDto.modelId, session=session))
            self.assertEqual(1, len(modelAttributes), "A single ModelAttribute record inserted to database")
            foundModelAttribute = modelAttributes[0]
            expectedMetadata = [{"metadataType": "COMMON_BASE_MSRP", "value": 30_000, "unit": "DOLLARS"}]
            self.assertEqual(expectedMetadata, foundModelAttribute.attribute_metadata)

    def test_acceptMultipleAttributes(self):
        attributeDtos = [BodyStyle(title="BodyStyle"), Grade(title="Grade")]
        self.destination.accept(attributeDtos=attributeDtos, rawDataDto=self.rawDataDto)
        with sessionFactory.newSession() as session:
            modelAttributes = list(
                modelAttributeService.getAttributesByModelId(modelId=self.rawDataDto.modelId, session=session))
            self.assertEqual(2, len(modelAttributes), "Two model attributes inserted into database")
            foundTypeAndTitle = {(modelAttribute.attribute_type, modelAttribute.title) for modelAttribute in
                                 modelAttributes}
        self.assertIn((AttributeType.BODY_STYLE, "BodyStyle"), foundTypeAndTitle)
        self.assertIn((AttributeType.GRADE, "Grade"), foundTypeAndTitle)

    def test_acceptRaisesOnOverwriteWhenOverwriteExistingIsFalse(self):
        self.destination = RepositoryDestination(overwriteExisting=False)
        attributeDtos = [BodyStyle(title="BodyStyle")]
        self.destination.accept(attributeDtos=attributeDtos, rawDataDto=self.rawDataDto)  # first insert
        self.assertRaises(IllegalStateError,
                          lambda: self.destination.accept(attributeDtos=attributeDtos, rawDataDto=self.rawDataDto))

    def test_acceptOverwritesWhenOverwriteExistingIsTrue(self):
        self.destination = RepositoryDestination(overwriteExisting=True)
        firstInsert = [BodyStyle(title="BodyStyle"), Grade(title="Grade")]
        self.destination.accept(attributeDtos=firstInsert, rawDataDto=self.rawDataDto)  # first insert
        secondInsert = [Transmission(title="Transmission")]
        self.destination.accept(attributeDtos=secondInsert, rawDataDto=self.rawDataDto)  # second insert
        with sessionFactory.newSession() as session:
            modelAttributes = list(
                modelAttributeService.getAttributesByModelId(modelId=self.rawDataDto.modelId, session=session))
            self.assertEqual(1, len(modelAttributes), "A single ModelAttribute record inserted to database")
            foundModelAttribute = modelAttributes[0]
            self.assertEqual(AttributeType.TRANSMISSION, foundModelAttribute.attribute_type, "Expected AttributeType")
            self.assertEqual("Transmission", foundModelAttribute.title, "Expected Title")

    def test_acceptRaisesIllegalArgumentErrorWhenModelNotFound(self):
        self.rawDataDto.modelId = uuid.uuid4()  # make modelId inconsistent with DB
        attributeDtos = [Transmission(title="Transmission")]
        self.assertRaises(IllegalArgumentError,
                          lambda: self.destination.accept(attributeDtos=attributeDtos, rawDataDto=self.rawDataDto))
