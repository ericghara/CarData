from common.domain.converter.type_converter.TypeConverter import TypeConverter
from common.domain.dto.AttributeDto import AttributeDto, attributeTypeToAttributeDto
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.entities import ModelAttribute
from common.domain.json.JsonDecoder import jsonDecoder


class ModelAttributeToAttributeDtoConverter(TypeConverter):

    inputType = ModelAttribute
    outputType = AttributeDto

    def convert(self, modelAttribute: ModelAttribute) -> AttributeDto:
        metadata = None
        # converts AttributeMetadata to a List[Dict]
        mapper = jsonDecoder.getMappingFunction(AttributeMetadata)
        if modelAttribute.attribute_metadata:
            metadata = [mapper(rawMetadata) for rawMetadata in modelAttribute.attribute_metadata]
        try:
            constructor = attributeTypeToAttributeDto[modelAttribute.attribute_type]
        except KeyError as e:
            raise ValueError(f"attribute_type {modelAttribute.attribute_type} has an unknown AttributeDto mapping.")
        return constructor(attributeId=modelAttribute.attribute_id, title=modelAttribute.title, modelId=modelAttribute.model_id, metadata=metadata,
                           updatedAt=modelAttribute.updated_at)

