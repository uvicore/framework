import uvicore
from uvicore import log
from app1.models.image import Image

@uvicore.seeder()
async def seed():
    log.item('Seeding table images')

    # Get related tablenames with proper prefixes
    posts = uvicore.db.tablename('app1.posts')
    users = uvicore.db.tablename('auth.users')


    # await Image.insert([
    #     # Post Images
    #     Image(imageable_type=posts, imageable_id=1, filename='post1-image1.png', size='1234932'),

    #     # User Images
    #     Image(imageable_type=users, imageable_id=1, filename='user1-image1.png', size='2483282'),
    # ])
