from uuid import UUID
from pydantic import BaseModel, Field


# TODO дополнить атрибутами


class RequirementRequest(BaseModel):
    project_id: UUID = Field(description='ID проекта')
    name: str = Field(description='Название')
    description_text: str = Field(description='Описание')


class RequirementResponse(BaseModel):
    id: UUID = Field(description='ID записи')
    project_id: UUID = Field(description='ID проекта')
    name: str = Field(description='Название')
    description_text: str = Field(description='Описание')


class Requirement(BaseModel):
    pass  # TODO переделать под схемы из swagger.yaml


class RequirementListResponse(BaseModel):
    data: list[Requirement]
