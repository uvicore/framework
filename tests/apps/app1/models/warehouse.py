from __future__ import annotations

from typing import List

import uvicore
from app1.database.tables import warehouses as table
from uvicore.orm import Model, ModelMetaclass, Field, HasMany, HasOne


@uvicore.model()
class Warehouse(Model['Warehouse'], metaclass=ModelMetaclass):
    """App1 Warehouse (natural-key parent)"""

    __tableclass__ = table.Warehouses

    id: int | None = Field('id',
        primary=True,
        description='Warehouse primary key',
        read_only=True,
    )

    code: str = Field('code',
        description='Unique natural key for the warehouse',
        sortable=True,
        searchable=True,
    )

    name: str = Field('name',
        description='Warehouse name',
    )

    # One-To-Many on a NATURAL key: warehouses.code = bins.warehouse_code
    # (local_key is `code`, NOT the `id` primary key)
    bins: List[Bin] | None = Field(None,
        description='Bins in this warehouse',
        relation=HasMany('app1.models.bin.Bin', foreign_key='warehouse_code', local_key='code'),
    )

    # One-To-One on a NATURAL key
    meta: WarehouseMeta | None = Field(None,
        description='Warehouse meta record',
        relation=HasOne('app1.models.warehouse_meta.WarehouseMeta', foreign_key='warehouse_code', local_key='code'),
    )


from app1.models.bin import Bin  # isort:skip
from app1.models.warehouse_meta import WarehouseMeta  # isort:skip
