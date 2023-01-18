import uuid
from datetime import date, datetime
from unittest import TestCase

from nose_parameterized import parameterized

from common.domain.dto.AttributeDto import AttributeDto, Transmission, Grade
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.AttributeType import AttributeType
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from common.repository.Entities import ModelAttribute
from common.repository.SessionFactory import sessionFactory
from common.repository.test_common.DbContainer import DbContainer
from common.service.persistence.ModelAttributeService import modelAttributeService


class TestModelAttributeService(TestCase):
    container = None

    @classmethod
    def setUpClass(cls):
        cls.container = DbContainer()
        cls.container.start()
        cls.container.initTables()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.container.stop()

    def setUp(self) -> None:
        self.container.insetTestRecords()

    def tearDown(self) -> None:
        self.container.deleteAll()

    @parameterized.expand([(ModelAttribute(attribute_id=uuid.UUID('00000000-0000-0000-0000-000000000000'),
                                           attribute_type=AttributeType.TRANSMISSION, title='test',
                                           model_id=uuid.UUID('11111111-1111-1111-1111-111111111111'),
                                           attribute_metadata=None,
                                           updated_at=datetime.fromtimestamp(800025)),
                            Transmission(title="test", attributeId=uuid.UUID('00000000-0000-0000-0000-000000000000'),
                                         modelId=uuid.UUID('11111111-1111-1111-1111-111111111111'), metadata=None,
                                         updatedAt=datetime.fromtimestamp(800025))),
                           # Testcase with metadata
                           (ModelAttribute(title="title", attribute_type=AttributeType.GRADE, attribute_metadata=[
                               {"metadataType": "COMMON_MSRP", "value": "Test", "unit": "DOLLARS"}]),
                            Grade(title="title", metadata=[
                                AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value="Test",
                                                  unit=MetadataUnit.DOLLARS)]))
                           ])
    def test__convertModelAttributeToModelDto(self, modelAttribute: ModelAttribute, expected: AttributeDto):
        found = modelAttributeService._convertModelAttributeToModelDto(modelAttribute)
        expected._assertStrictEq(found)

    @parameterized.expand([(Transmission(title="test", attributeId=uuid.UUID('00000000-0000-0000-0000-000000000000'),
                                         modelId=uuid.UUID('11111111-1111-1111-1111-111111111111'), metadata=None,
                                         updatedAt=datetime.fromtimestamp(800025)),
                            ModelAttribute(attribute_id=uuid.UUID('00000000-0000-0000-0000-000000000000'),
                                           attribute_type=AttributeType.TRANSMISSION, title='test',
                                           model_id=uuid.UUID('11111111-1111-1111-1111-111111111111'),
                                           attribute_metadata=None,
                                           updated_at=datetime.fromtimestamp(800025))
                            ),
                           # Testcase with metadata
                           (Grade(title="title", metadata=[
                               AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value="Test",
                                                 unit=MetadataUnit.DOLLARS)]),
                            ModelAttribute(attribute_id=None, attribute_type=AttributeType.GRADE, title="title",
                                           model_id=None,
                                           attribute_metadata=[
                                               {"metadataType": "COMMON_MSRP", "value": "Test", "unit": "DOLLARS"}],
                                           updated_at=None))
                           ])
    def test__convertAttributeDtoToModelAttribute(self, attributeDto: AttributeDto, expected: ModelAttribute):
        stripPrivate = lambda modelAttribute: {key: value for key, value in modelAttribute.__dict__.items() if
                                               not key.startswith("_")}
        found = modelAttributeService._convertAttributeDtoToModelAttribute(attributeDto)
        self.assertEqual(stripPrivate(expected), stripPrivate(found))

    def test_insert(self) -> None:
        with sessionFactory.newSession() as session:
            camry2023 = modelAttributeService._getModel(brandName="toyota", modelName="Camry",
                                                        modelYear=date(2023, 1, 1), session=session)
            beforeCount = len(camry2023.model_attribute)
            newAttribute = ModelAttribute(model=camry2023, attribute_type=AttributeType.GRADE,
                                          title="SE",
                                          attribute_metadata={'starting_msrp': 27_760})
            modelAttributeService.insert(modelAttribute=newAttribute, session=session)
            session.commit()
            afterCount = len(camry2023.model_attribute)
        self.assertEqual(beforeCount + 1, afterCount)

    def test_getAttributesFor(self) -> None:
        expectedNum = 4
        with sessionFactory.newSession() as session:
            foundAttributes = modelAttributeService.getAttributesFor(brandName='toyota', modelName='Camry',
                                                                     modelYear=date(2023, 1, 1), session=session)
            foundNum = len(foundAttributes)
        self.assertEqual(expectedNum, foundNum)

    def test_getAttributeByTypeAndTitle(self) -> None:
        with sessionFactory.newSession() as session:
            camry2023 = modelAttributeService._getModel(brandName="toyota", modelName="Camry",
                                                        modelYear=date(2023, 1, 1), session=session)
            foundAttribute = modelAttributeService.getAttributeByTypeAndTitle(attributeType=AttributeType.GRADE,
                                                                              title="LE", modelId=camry2023.model_id,
                                                                              session=session)
            expected = [attribute for attribute in camry2023.model_attribute if attribute.title == "LE"][0]
            self.assertEqual(expected, foundAttribute)

    def test_getAttributesByModelId(self) -> None:
        with sessionFactory.newSession() as session:
            camry2023 = modelAttributeService._getModel(brandName="toyota", modelName="Camry",
                                                        modelYear=date(2023, 1, 1), session=session)
            expectedAttributes = set(camry2023.model_attribute)
            foundAttributes = set(
                modelAttributeService.getAttributesByModelId(modelId=camry2023.model_id, session=session))
            self.assertEqual(expectedAttributes, foundAttributes)

    def test_getAttributesByModelIdAndType(self) -> None:
        with sessionFactory.newSession() as session:
            camry2023 = modelAttributeService._getModel(brandName="toyota", modelName="Camry",
                                                        modelYear=date(2023, 1, 1), session=session)
            expectedAttributes = {attribute for attribute in camry2023.model_attribute if
                                  attribute.attribute_type == AttributeType.GRADE}
            foundAttributes = set(modelAttributeService.getAttributesByModelIdAndType(modelId=camry2023.model_id,
                                                                                      attributeType=AttributeType.GRADE,
                                                                                      session=session))
            self.assertEqual(expectedAttributes, foundAttributes)

    def test_getAttributesByAttributeId(self) -> None:
        with sessionFactory.newSession() as session:
            camry2023 = modelAttributeService._getModel(brandName="toyota", modelName="Camry",
                                                        modelYear=date(2023, 1, 1), session=session)
            expectedAttributes = {attribute for attribute in camry2023.model_attribute}
            queryIds = [attribute.attribute_id for attribute in expectedAttributes]
            foundAttributes = set(
                modelAttributeService.getAttributesByAttributeId(attributeIds=queryIds, session=session))
            self.assertEqual(expectedAttributes, foundAttributes)
