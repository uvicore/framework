from __future__ import annotations

from typing import List

import uvicore
from app1.database.tables import depots as table
from uvicore.orm import Model, ModelMetaclass, Field, HasMany


@uvicore.model()
class Depot(Model['Depot'], metaclass=ModelMetaclass):
    """App1 Depot (composite natural-key parent)"""

    __tableclass__ = table.Depots

    id: int | None = Field('id',
        primary=True,
        description='Depot primary key',
        read_only=True,
    )

    region: str = Field('region',
        description='Shard/region key',
    )

    code: str = Field('code',
        description='Depot code (unique only within a region)',
    )

    name: str = Field('name',
        description='Depot name',
    )

    # One-To-Many on a COMPOSITE key, paired and ANDed in declared order:
    #   depots.region = slots.region AND depots.code = slots.depot_code
    slots: List[Slot] | None = Field(None,
        description='Slots in this depot',
        relation=HasMany('app1.models.slot.Slot',
            foreign_key=['region', 'depot_code'],
            local_key=['region', 'code'],
        ),
    )


from app1.models.slot import Slot  # isort:skip
