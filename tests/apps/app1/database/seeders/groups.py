import uvicore
from uvicore.auth.support import password
from uvicore.auth.models.role import Role
from uvicore.auth.models.group import Group
from uvicore.support.dumper import dump, dd


@uvicore.seeder()
async def seed():
    uvicore.log.item('Seeding table groups')

    # Get all roles
    roles = await Role.query().key_by('name').get()

    await Group.insert_with_relations([
        # {
        #     'name': 'Manager',
        #     'roles': [
        #         roles['Employee']
        #     ]
        # }

        # Uvicore groups should match FusionAuth Roles (NOT FA groups)
        {
            'name': 'Accounting',
        },
        {
            'name': 'Accounting Manager',
        },
        {
            'name': 'Development',
        },
        {
            'name': 'Employee',
        },
        {
            'name': 'HR',
        },
        {
            'name': 'HR Manager',
        },
        {
            'name': 'IT',
        },
        {
            'name': 'Marketing',
        },
        {
            'name': 'Marketing Manager',
        },
        {
            'name': 'Operations',
        },
        {
            'name': 'Operations Manager',
        },
        {
            'name': 'Sales External',
        },
        {
            'name': 'Sales Internal',
        },
        {
            'name': 'Sales Manager',
        },
        {
            'name': 'Tech Support',
        },
        {
            'name': 'Warehouse',
        },
        {
            'name': 'Warehouse Manager',
        },
    ])

    #await Group(name='Managers').save()
    #await Group(name='Employees').save()

