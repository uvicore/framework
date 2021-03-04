import uvicore
from uvicore.auth.support import password
from uvicore.support.dumper import dump, dd
from uvicore.auth.models.permission import Permission

@uvicore.seeder()
async def seed():
    #from uvicore.auth.models

    # NOTICE, each model role is seeded from the db seeder command
    # This is where I add additional permissions

    await Permission.insert([
        {
            'entity': None,
            'name': 'admin',
        },
    ])

    # NO, we do this from db seeder command now

    # uvicore.log.item('Seeding table permissions')

    # entities = [
    #     uvicore.db.tablename('auth.group_roles'),
    #     uvicore.db.tablename('auth.groups'),
    #     uvicore.db.tablename('auth.permissions'),
    #     uvicore.db.tablename('auth.role_permissions'),
    #     uvicore.db.tablename('auth.roles'),
    #     uvicore.db.tablename('auth.user_groups'),
    #     uvicore.db.tablename('auth.user_roles'),
    #     uvicore.db.tablename('auth.users'),
    # ]

    # permissions = [
    #     'create',   # Django add
    #     'read',     # Django view
    #     'update',   # Django change
    #     'delete',   # Django delete
    # ]

    # bulk = []
    # for entity in entities:
    #     for permission in permissions:
    #         bulk.append(Permission(entity=entity, name=entity + '.' + permission))

    # await Permission.insert(bulk)
