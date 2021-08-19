from __future__ import annotations
import uvicore
from typing import Optional, Any
from app1.database.tables import attributes as table
from uvicore.orm import Model, ModelMetaclass, Field


@uvicore.model()
class Attribute(Model['Attribute'], metaclass=ModelMetaclass):
    """Polymorphic One-To-Many Attributes"""

    # Database table definition
    __tableclass__ = table.Attributes

    id: Optional[int] = Field('id',
        primary=True,
        description='Attribute ID',
        read_only=True,
    )

    attributable_type: str = Field('attributable_type',
        description='Polymorphic Attribute Type',
        required=True,
    )

    attributable_id: int = Field('attributable_id',
        description="Polymorphic Attribute Types ID",
        required=True,
    )

    key: str = Field('key',
        description='Attribute Key',
        required=True,
        json=True,
    )

    value: Any = Field('value',
        description="Attribute Value",
        required=True,
    )
