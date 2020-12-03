import uvicore
from uvicore import log
from app1.models.hashtag import Hashtag

@uvicore.seeder()
async def seed():
    log.item('Seeding table hashtags')
    hashtags = [
        Hashtag(name='important'),
        Hashtag(name='obsolete'),
        Hashtag(name='outdated'),
    ]
    await Hashtag.insert(hashtags)


