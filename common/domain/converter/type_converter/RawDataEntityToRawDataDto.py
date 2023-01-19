from common.domain.converter.type_converter.TypeConverter import TypeConverter
from common.domain.dto.RawDataDto import RawDataDto
from common.repository.Entities import RawData


class RawDataEntityToRawDataDto(TypeConverter):

    inputType = RawData
    outputType = RawDataDto

    def convert(self, rawDataEntity: RawData) -> RawDataDto:
        return RawDataDto(dataId=rawDataEntity.data_id, rawData=rawDataEntity.raw_data,
                                    modelId=rawDataEntity.model_id, createdAt=rawDataEntity.created_at)