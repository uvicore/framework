import uvicore
from uvicore import log
from app1.models.tag import Tag

@uvicore.seeder()
async def seed():
    log.item('Seeding table tags')
    tags = [
        Tag(name='linux', creator_id=1),
        Tag(name='mac', creator_id=1),
        Tag(name='bsd', creator_id=2),
        Tag(name='laravel', creator_id=2),
        Tag(name='lumen', creator_id=3),
        Tag(name='django', creator_id=3),
        Tag(name='flask', creator_id=4),
        Tag(name='fastapi', creator_id=4),
        Tag(name='starlette', creator_id=4),
    ]
    await Tag.insert(tags)


