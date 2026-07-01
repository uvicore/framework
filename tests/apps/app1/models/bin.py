from __future__ import annotations

import uvicore
from app1.database.tables import bins as table
from uvicore.orm import Model, ModelMetaclass, Field, BelongsTo


@uvicore.model()
class Bin(Model['Bin'], metaclass=ModelMetaclass):
    """App1 Bin (natural-key child of Warehouse)"""

    __tableclass__ = table.Bins

    id: int | None = Field('id',
        primary=True,
        description='Bin primary key',
        read_only=True,
    )

    warehouse_code: str = Field('warehouse_code',
        description='Natural key referencing warehouses.code',
    )

    label: str = Field('label',
        description='Bin label',
    )

    # Inverse on a NATURAL key: bins.warehouse_code = warehouses.code
    warehouse: Warehouse | None = Field(None,
        description='Parent warehouse',
        relation=BelongsTo('app1.models.warehouse.Warehouse', foreign_key='code', local_key='warehouse_code'),
    )


from app1.models.warehouse import Warehouse  # isort:skip
