from app1.models.tag import Tag

async def seed():
    tags = [
        Tag(name='linux'),
        Tag(name='mac'),
        Tag(name='bsd'),
        Tag(name='laravel'),
        Tag(name='lumen'),
        Tag(name='django'),
        Tag(name='flask'),
        Tag(name='fastapi'),
        Tag(name='starlette'),
    ]
    await Tag.insert(tags)


