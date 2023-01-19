import logging
from typing import List, NamedTuple, Type, Optional, Any

from common.domain.converter.type_converter.AttributeDtoToModelAttributeConverter import \
    AttributeDtoToModelAttributeConverter
from common.domain.converter.type_converter.ModelAttributeToAttributeDtoConverter import \
    ModelAttributeToAttributeDtoConverter
from common.domain.converter.type_converter.RawDataEntityToRawDataDto import RawDataEntityToRawDataDto
from common.domain.converter.type_converter.TypeConverter import TypeConverter
from common.exception.IllegalStateError import IllegalStateError


class ConversionCapability(NamedTuple):
    inputType: Type
    outputType: Type


class Converter:
    """
    An easily composable class that performs type conversions.  Type Converters that implement
    the ``TypeConverter`` interface may be registered and accessed through ``Converter``.
    """

    def __init__(self, typeConverters: Optional[List[TypeConverter]]):
        self.typeConverterRegistry = dict()
        self.log = logging.getLogger(type(self).__name__)
        for typeConverter in typeConverters or list():
            self.registerTypeConverter(typeConverter)

    def registerTypeConverter(self, typeConverter: TypeConverter):
        conversion = ConversionCapability(inputType=typeConverter.getInputType(),
                                          outputType=typeConverter.getOutputType())
        if (oldTypeConverter := self.typeConverterRegistry.get(conversion)):
            self.log.warning(
                f"Replacing conversion registration: {conversion} from converter: {oldTypeConverter} to: {typeConverter}")
        self.typeConverterRegistry[conversion] = typeConverter

    def convert(self, obj: Any, outputType: Type) -> Any:
        conversion = ConversionCapability(inputType=type(obj), outputType=outputType)
        try:
            typeConverter = self.typeConverterRegistry[conversion]
        except KeyError as e:
            typeConverter = None
            # Search if obj class is a child of a convertable class
            for conversionCapability in self.typeConverterRegistry.keys():
                if isinstance(obj, conversionCapability.inputType) and outputType == conversionCapability.outputType:
                    typeConverter = self.typeConverterRegistry[conversionCapability]
                    break
        if not typeConverter:
            raise IllegalStateError(f"No converter is registered for the conversion: {conversion}")
        return typeConverter.convert(obj)


converter = Converter(typeConverters=[ModelAttributeToAttributeDtoConverter(),
                                      AttributeDtoToModelAttributeConverter(),
                                      RawDataEntityToRawDataDto()])
