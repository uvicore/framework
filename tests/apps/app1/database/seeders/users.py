from uvicore import log
from uvicore.auth.models.user import User
#from app1.models.user import User

async def seed():
    log.item('Seeding table users')

    # You can insert parent records with relations as Dict
    # Though its not BULK, its a loop in the ORM
    # This inserts user first, then contact with link back to new user
    await User.insert_with_relations([
        {
            'email': 'administrator@example.com',
            'app1_extra': 'hi',
            'contact': {
                'name': 'Administrator',
                'title': 'God',
                'address': '777 Heaven Ln',
                'phone': '777-777-7777',
                # NO, user_id=1
            }
        }
    ])

    # You can use .insert() as a List of model instances
    await User.insert([
        #NO - User(email='administrator@example.com', app1_extra='hi'),
        User(email='manager1@example.com'),

        #User(email='manager2@example.com', app1_extra='there'),
        User(email='manager2@example.com'),

        #NO - User(email='user1@example.com'),
        #NO - User(email='user2@example.com'),
    ])

    # You can also user .insert() as a list of Dict
    await User.insert([
        {
            'email': 'user1@example.com'
        }
    ])
