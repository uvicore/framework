from __future__ import annotations
import uvicore
from typing import Optional, Any
from app1.database.tables import attributes as table
from uvicore.orm.fields import Field
from uvicore.orm.model import Model, ModelMetaclass


#@uvicore.ioc.bind('app1.models.attribute.Attribute')

@uvicore.model()
class Attribute(Model['Attribute'], metaclass=ModelMetaclass):
    """App1 Polymorphic One-To-Many Attributes"""

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


# IoC Class Instance
#Attribute: AttributeModel = uvicore.ioc.make('app1.models.attribute.Attribute', AttributeModel)

# Update forwrad refs (a work around to circular dependencies)
#from app1.models.post import Post  # isort:skip
#from app1.models.user import User  # isort:skip
#Image.update_forward_refs()
