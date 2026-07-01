from __future__ import annotations

import uvicore
from app1.database.tables import warehouse_meta as table
from uvicore.orm import Model, ModelMetaclass, Field, BelongsTo


@uvicore.model()
class WarehouseMeta(Model['WarehouseMeta'], metaclass=ModelMetaclass):
    """App1 Warehouse Meta (natural-key one-to-one child of Warehouse)"""

    __tableclass__ = table.WarehouseMeta

    id: int | None = Field('id',
        primary=True,
        description='Warehouse meta primary key',
        read_only=True,
    )

    warehouse_code: str = Field('warehouse_code',
        description='Natural key referencing warehouses.code',
    )

    note: str = Field('note',
        description='Free-form note about the warehouse',
    )

    # Inverse on a NATURAL key
    warehouse: Warehouse | None = Field(None,
        description='Parent warehouse',
        relation=BelongsTo('app1.models.warehouse.Warehouse', foreign_key='code', local_key='warehouse_code'),
    )


from app1.models.warehouse import Warehouse  # isort:skip
