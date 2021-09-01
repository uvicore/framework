import uvicore
from uvicore import log
from app1.models.contact import Contact

@uvicore.seeder()
async def seed():
    log.item('Seeding table contacts')

    contacts = [
        #Contact(name='Administrator', title='God', address='777 Heaven Ln', phone='777-777-7777', user_id=1),
        #NO - done in user.py seeder - Contact(name='Manager One', title='Manager1', address='111 Manager Way', phone='111-111-1111', user_id=2),
        Contact(name='Manager Two', title='Manager2', address='222 Manager Way', phone='222-222-2222', user_id=4),
        Contact(name='User One', title='User1', address='333 User Dr.', phone='333-333-3333', user_id=5),
        #NO  done in post.py seeder - Contact(name='User Two', title='User2', address='444 User Dr.', phone='444-444-4444', user_id=5),
    ]
    await Contact.insert(contacts)
