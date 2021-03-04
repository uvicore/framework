import uvicore
from app1.models.contact import Contact
from uvicore.auth.models.user import User
from uvicore.auth.models.group import Group
from uvicore.auth.models.role import Role


@uvicore.seeder()
async def seed():
    uvicore.log.item('Seeding table users')

    # Get all groups keyed by name
    groups = await Group.query().key_by('name').get()

    # Get all roles keyed by name
    roles = await Role.query().key_by('name').get()


    # You can insert parent records with relations as Dict
    # Though its not BULK, its a loop in the ORM
    # This inserts user first, then contact with link back to new user
    # await User.insert_with_relations([
    #     {
    #         'email': 'administrator@example.com',
    #         'app1_extra': 'hi',
    #         'contact': {
    #             'name': 'Administrator',
    #             'title': 'God',
    #             'address': '777 Heaven Ln',
    #             'phone': '777-777-7777',
    #             # NO, user_id=1
    #         }
    #     }
    # ])

    # Example of deleteing a HasOne child
    #user = await User.query().find(1)
    #await user.delete('contact')

    # You can insert one so you can insert relations right after
    user = await User(
        email='manager1@example.com',
        first_name='Manager',
        last_name='One',
        password='techie',
        creator_id=1,
    ).save()
    # Technically this DOES work, but it means you model has to have user_id as optional requored=False, which may not be what you want for OpenAPI doc visuals
    # but create can accept a Dict or an actual Model
    #await user.create('contact', Contact(name='Manager One', title='Manager1', address='111 Manager Way', phone='111-111-1111'))
    await user.create('contact', {
        'name': 'Manager One',
        'title': 'Manager1',
        'address': '111 Manager Way',
        'phone': '111-111-1111',
        #'user_id': 2 # NOT needed as its inferred
    })
    await user.link('groups', [
        groups['Manager']
    ])
    await user.link('roles', [
        roles['Post Users']
    ])

    # You can use .insert() as a List of model instances
    await User.insert([
        User(
            email='manager2@example.com',
            first_name='Manager',
            last_name='Two',
            creator_id=1,
            app1_extra='there',
            password='techie',
        ),
    ])
    user = await User.query().find(email='manager2@example.com')
    await user.link('groups', [
        groups['Administrator']
    ])


    # You can also user .insert() as a list of Dict
    await User.insert([
        {
            'email': 'user1@example.com',
            'first_name': 'User',
            'last_name': 'One',
            'creator_id': 2,
            'password': 'techie',
        }
    ])
