from datetime import date
from unittest import TestCase

from common.domain.enum.AttributeType import AttributeType
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
        self.assertEqual(beforeCount+1, afterCount)

    def test_getAttributesFor(self) -> None:
        expectedNum = 4
        with sessionFactory.newSession() as session:
            foundAttributes = modelAttributeService.getAttributesFor(brandName='toyota', modelName='Camry', modelYear=date(2023,1,1), session=session)
            foundNum = len(foundAttributes)
        self.assertEqual(expectedNum, foundNum)

    def test_getAttributeByTypeAndTitle(self) -> None:
        with sessionFactory.newSession() as session:
            camry2023 = modelAttributeService._getModel(brandName="toyota", modelName="Camry",
                                                        modelYear=date(2023, 1, 1), session=session)
            foundAttribute = modelAttributeService.getAttributeByTypeAndTitle(attributeType=AttributeType.GRADE, title="LE", modelId=camry2023.model_id, session=session)
            expected = [attribute for attribute in camry2023.model_attribute if attribute.title == "LE"][0]
            self.assertEqual(expected, foundAttribute)

    def test_getAttributesByModelId(self) -> None:
        with sessionFactory.newSession() as session:
            camry2023 = modelAttributeService._getModel(brandName="toyota", modelName="Camry",
                                                        modelYear=date(2023, 1, 1), session=session)
            expectedAttributes = set(camry2023.model_attribute)
            foundAttributes = set(modelAttributeService.getAttributesByModelId(modelId=camry2023.model_id, session=session) )
            self.assertEqual(expectedAttributes, foundAttributes)

    def test_getAttributesByModelIdAndType(self) -> None:
        with sessionFactory.newSession() as session:
            camry2023 = modelAttributeService._getModel(brandName="toyota", modelName="Camry",
                                                        modelYear=date(2023, 1, 1), session=session)
            expectedAttributes = {attribute for attribute in camry2023.model_attribute if attribute.attribute_type == AttributeType.GRADE}
            foundAttributes = set(modelAttributeService.getAttributesByModelIdAndType(modelId=camry2023.model_id, attributeType=AttributeType.GRADE, session=session) )
            self.assertEqual(expectedAttributes, foundAttributes)

    def test_getAttributesByAttributeId(self) -> None:
        with sessionFactory.newSession() as session:
            camry2023 = modelAttributeService._getModel(brandName="toyota", modelName="Camry",
                                                        modelYear=date(2023, 1, 1), session=session)
            expectedAttributes = {attribute for attribute in camry2023.model_attribute}
            queryIds = [attribute.attribute_id for attribute in expectedAttributes]
            foundAttributes = set(modelAttributeService.getAttributesByAttributeId(attributeIds=queryIds, session=session) )
            self.assertEqual(expectedAttributes, foundAttributes)










