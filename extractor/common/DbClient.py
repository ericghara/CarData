from repository.SessionFactory import sessionFactory
from repository.dto import Model as ModelDto
from repository.Entities import RawData, Model, Brand














class ModelInfo:

    def __init__(self, modelName: str, modelCode: str, path: str, isArchived: bool | str):
        self.modelName = modelName
        self.modelCode = modelCode
        self.path = path
        # not currently used for anything
        if type(isArchived) is str:
            isArchived = isArchived.capitalize() == 'True'
        self.isArchived = isArchived

    def __repr__(self) -> str:
        return f'ModelInfo({self.modelName}, {self.modelCode}, {self.path}, {self.isArchived})'

    def __eq__(self, other) -> bool:
        if type(self) is not type(other):
            return False
        return vars(self) == vars(other)