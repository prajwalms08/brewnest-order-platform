from decimal import Decimal

from pydantic import BaseModel, Field


class Modifier(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )
    price: Decimal = Field(
        ge=0,
    )


class MenuCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    price: Decimal = Field(
        gt=0,
    )

    category: str = Field(
        min_length=1,
        max_length=50,
    )

    modifiers: list[Modifier] = []


class MenuResponse(BaseModel):
    name: str
    price: Decimal
    category: str
    id: str
    modifiers: list[Modifier] = []