import logging
from typing import List, NamedTuple

from common.domain.dto.RawDataDto import RawDataDto
from common.repository.SessionFactory import sessionFactory
from common.service.persistence.RawDataService import rawDataService
from transformer.Transformer import Transformer
from transformer.adapter.TransformDestination import TransformDestination


class RawDataDtoAndBrandName(NamedTuple):
    rawDataDto: RawDataDto
    brandName: str


class TransformerService:

    def __init__(self, destination: TransformDestination, transformers: List[Transformer]):
        self.destination = destination
        self.log = logging.getLogger(self.__class__.__name__)
        self.brandNameToTransformer = dict()
        self._registerTransformers(transformers)

    def _registerTransformers(self, transformers: List[Transformer]) -> None:
        for transformer in transformers:
            for brandName in transformer.brandNames:
                if (currentReg := self.brandNameToTransformer.get(brandName)):
                    self.log.warning(f"Brand {brandName} - replacing existing registration: "
                                     f"{type(currentReg)} with: {type(transformer)}")
                self.brandNameToTransformer[brandName] = transformer

    def _validateRawDataDto(self, rawDataDto: RawDataDto):
        if not rawDataDto.dataId:
            raise ValueError("RawDataDto must have (data_id or raw_data) and model_id.")

    def _fetchRawDataDtoAndBrandName(self, rawDataDto: RawDataDto) -> RawDataDtoAndBrandName:
        with sessionFactory.newSession() as session:
            rawDataEntity = rawDataService.getByDataId(dataId=rawDataDto.dataId, session=session)
            if rawDataDto.modelId and rawDataDto.modelId != rawDataEntity.model_id:
                self.log.warning(f"Expected modelId: {rawDataDto.modelId} found modelId: {rawDataEntity.model_id}.")
                raise ValueError("The provided modelId is inconsistent with the fetched model_id")
            fetchedDto = RawDataDto(dataId=rawDataEntity.data_id, rawData=rawDataEntity.raw_data,
                                    modelId=rawDataEntity.model_id, createdAt=rawDataEntity.created_at)
            brandName = rawDataEntity.model.brand.name
        return RawDataDtoAndBrandName(rawDataDto=fetchedDto, brandName=brandName)

    def _selectTransformer(self, brandName: str) -> Transformer:
        pass

    def transform(self, rawDataDto: RawDataDto) -> None:
        self._validateRawDataDto(rawDataDto)
        syncedRawDataDto, brandName = self._fetchRawDataDtoAndBrandName(rawDataDto)
        transformer = self._selectTransformer(brandName)
        attributeDtos = transformer.transform(rawDataDto)
        self.destination.accept(attributes=attributeDtos, rawDataDto=syncedRawDataDto)
