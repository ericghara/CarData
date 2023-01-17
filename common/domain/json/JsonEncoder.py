import json
from typing import Any, Type, List, NamedTuple

from common.domain.json.object_encoder.AttributeEncoder import AttributeEncoder
from common.domain.json.object_encoder.AttributeMetadataEncoder import AttributeMetadataEncoder
from common.domain.json.object_encoder.ObjectEncoder import ObjectEncoder


class TypeAndEncoder(NamedTuple):
    objectType: Type
    objectEncoder: ObjectEncoder


class JsonEncoder(json.JSONEncoder):

    def __init__(self, encoders: List[ObjectEncoder]):
        super().__init__()
        self.encoderRelay = list()
        for objectEncoder in encoders:
            self.encoderRelay.append(
                TypeAndEncoder(objectType=objectEncoder.objectType, objectEncoder=objectEncoder))
            objectEncoder.setJsonEncoder(self)

    def default(self, obj: Any) -> Any:
        """
        converts the input to a JSON serializable container/object that json.dumps can natively encode
        :param obj:
        :return:
        """
        try:
            objectEncoder = next(typeAndEncoder.objectEncoder for typeAndEncoder in self.encoderRelay if
                                 isinstance(obj, typeAndEncoder.objectType))
        except StopIteration:
            return json.JSONEncoder.default(self, obj)
        return objectEncoder.toSerializable(obj)

jsonEncoder = JsonEncoder([AttributeEncoder(), AttributeMetadataEncoder()])