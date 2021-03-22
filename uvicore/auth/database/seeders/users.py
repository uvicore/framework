import uuid
import uvicore
from uvicore.auth.models.user import User
from uvicore.auth.models.role import Role
from uvicore.support.dumper import dump, dd


@uvicore.seeder()
async def seed():
    uvicore.log.item('Seeding table users')

    # Get all roles keyed by name
    roles = await Role.query().key_by('name').get()

    unique_id = str(uuid.uuid4())
    # How you "would" do it, but None password means login never allowed
    #pwd = password.create(unique_id)
    pwd = None

    user = await User(
        uuid=unique_id,
        username='anonymous',
        email='anonymous@example.com',
        first_name='Anonymous',
        last_name='User',
        title='Anonymous',
        disabled=True,
        password=None,
        creator_id=1,
    ).save()

    await user.link('roles', [
        roles['Anonymous']
    ])

    # users = []
    # fake = Faker()
    # for _ in range(2):
    #     user = User(
    #         email=fake.email()
    #     )
    #     await user.save()
