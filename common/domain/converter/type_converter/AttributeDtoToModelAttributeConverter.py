from common.domain.converter.type_converter.TypeConverter import TypeConverter
from common.domain.dto.AttributeDto import AttributeDto
from common.domain.json.JsonEncoder import jsonEncoder
from common.repository.Entities import ModelAttribute


class AttributeDtoToModelAttributeConverter(TypeConverter):

    inputType = AttributeDto
    outputType = ModelAttribute

    def convert(self, attributeDto: AttributeDto) -> ModelAttribute:
        # jsonEncoder maps AttributeDto to attribute_type and encodes the metadata
        # other attributes unchanged by jsonEncoder
        attributeDict = jsonEncoder.default(attributeDto)
        return ModelAttribute(attribute_id=attributeDict['attributeId'], attribute_type=attributeDict['attributeType'],
                              title=attributeDict['title'], model_id=attributeDict['modelId'],
                              attribute_metadata=attributeDict['attributeMetadata'],
                              updated_at=attributeDict['updatedAt'])

