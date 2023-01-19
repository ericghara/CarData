import uuid
from datetime import datetime, date
from unittest import TestCase, mock

from parameterized import parameterized

from common.domain.converter.Converter import converter
from common.domain.dto.AttributeDto import Other
from common.domain.dto.RawDataDto import RawDataDto
from common.domain.entities import Manufacturer, Brand, Model, RawData
from common.exception.IllegalArgumentError import IllegalArgumentError
from common.exception.IllegalStateError import IllegalStateError
from common.repository.SessionFactory import sessionFactory
from common.repository.test_common.DbContainer import DbContainer
from transformer.adapter.transform_destination.MockDestination import MockDestination
from transformer.service.TransformerService import TransformerService
from transformer.transform.MockTransformer import MockTransformer


class TestTransformerService(TestCase):

    def setUp(self):
        self.sessionFactoryMock = mock.patch('transform.service.TransformerService.sessionFactory.newSession',
                                             side_effect=AssertionError('Should not interact with repository'))
        self.mockTransformer0 = MockTransformer(manufacturerCommon='Toyota', brandNames=['Lexus', 'Toyota'])
        self.mockTransformer1 = MockTransformer(manufacturerCommon='manufacturer', brandNames=['brand'])
        self.transformerService = TransformerService(destination=MockDestination(),
                                                     transformers=[self.mockTransformer0,
                                                                   self.mockTransformer1])

    def tearDown(self) -> None:
        for mockObj in self.sessionFactoryMock,:
            if mockObj:
                mockObj.stop()

    @parameterized.expand(['Lexus', 'Toyota', 'brand'])
    def test__selectTransformer(self, brandName: str):
        foundTransformer = self.transformerService._selectTransformer(brandName)
        self.assertIn(brandName, foundTransformer.brandNames)

    def test__selectTransformerRaisesIllegalArgumentErrorUnknownBrandName(self):
        self.assertRaises(IllegalArgumentError, lambda: self.transformerService._selectTransformer("FakeBrand"))

    def test_transformRaisesIllegalArgumentErrorWhenRawDataDtoHasNoDataId(self):
        invalidDto = RawDataDto(dataId=None, rawData={}, modelId=uuid.uuid4(), createdAt=datetime.now())
        self.assertRaises(IllegalArgumentError, lambda: self.transformerService.transform(invalidDto))


class IntegrationTestTransformerService(TestCase):
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
        self.mockTransformer = MockTransformer(manufacturerCommon='Toyota', brandNames=['Lexus', 'Toyota'])
        self.mockDestination = MockDestination()
        self.transformerService = TransformerService(destination=self.mockDestination,
                                                     transformers=[self.mockTransformer])

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
            self.rawDataDto = converter.convert(camry2023Data, RawDataDto)

    def test_transformRaisesWhenModelIdInconsistent(self):
        self.rawDataDto.modelId = uuid.uuid4()  # make modelId inconsistent with DB state
        self.assertRaises(IllegalStateError, lambda: self.transformerService.transform(self.rawDataDto))

    def test_transformCallsExpectedTransformer(self):
        attributeDtos = [Other(title="Fake Attribute")]
        self.mockTransformer.addReturnValues(returnValues=[attributeDtos])
        self.transformerService.transform(self.rawDataDto)
        self.assertEqual(self.rawDataDto, self.mockTransformer.calledWith[0],
                         "mockTransformer called with expected RawDataDto")
        self.assertEqual(1, len(self.mockTransformer.calledWith), "MockTransformer called once")

    def test_transformCallsDestinationWithExpectedParameters(self):
        attributeDtos = [Other(title="Fake Attribute")]
        self.mockTransformer.addReturnValues(returnValues=[attributeDtos])
        self.transformerService.transform(self.rawDataDto)
        self.assertEqual((attributeDtos, self.rawDataDto), self.mockDestination.calledWith[0])
        self.assertEqual(1, len(self.mockDestination.calledWith))
