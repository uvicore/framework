from __future__ import annotations

import uvicore
from app1.database.tables import slots as table
from uvicore.orm import Model, ModelMetaclass, Field, BelongsTo


@uvicore.model()
class Slot(Model['Slot'], metaclass=ModelMetaclass):
    """App1 Slot (composite natural-key child of Depot)"""

    __tableclass__ = table.Slots

    id: int | None = Field('id',
        primary=True,
        description='Slot primary key',
        read_only=True,
    )

    region: str = Field('region',
        description='Shard/region key',
    )

    depot_code: str = Field('depot_code',
        description='Depot code within the region',
    )

    label: str = Field('label',
        description='Slot label',
    )

    # Inverse on a COMPOSITE key:
    #   slots.region = depots.region AND slots.depot_code = depots.code
    depot: Depot | None = Field(None,
        description='Parent depot',
        relation=BelongsTo('app1.models.depot.Depot',
            foreign_key=['region', 'code'],
            local_key=['region', 'depot_code'],
        ),
    )


from app1.models.depot import Depot  # isort:skip
