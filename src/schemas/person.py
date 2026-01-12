"""
Pydantic схемы для Person
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PersonBase(BaseModel):
    """Базовая схема Person"""
    external_id: str = Field(..., description="Внешний ID из SSO")
    status: str = Field(default="active", description="Статус пользователя")


class PersonCreate(PersonBase):
    """Схема для создания Person"""
    pass


class PersonUpdate(BaseModel):
    """Схема для обновления Person"""
    status: Optional[str] = None


class PersonInDB(PersonBase):
    """Схема Person из БД"""
    id: int
    datetime_created: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PersonResponse(PersonInDB):
    """Схема ответа с Person"""
    pass

