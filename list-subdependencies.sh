# Everything in grep below is dependencies I already delcare in pyproject.toml
# So the output will be all subdependencies.
# I use this list to add to my pyproject.toml just so poetry build pins all subdependencies.

pip freeze | grep -iv anyio | grep -iv colored | grep -iv prettyprinter | grep -iv environs | grep -iv argon2 | grep -iv cryptography | grep -iv aiohttp | grep -iv merge | grep -iv jinja | grep -iv pydantic | grep -iv httpx | grep -iv uvicore | grep -iv sqlalchemy | grep -iv alembic | grep -iv aiomysql | grep -iv aiosqlite | grep -iv asyncpg | grep -iv redis | grep -iv starlette | grep -iv fastapi | grep -iv uvicorn | grep -iv gunicorn | grep -iv aiofiles | grep -iv requests | grep -iv itsdangerous | grep -iv uvloop | grep -iv httptools | grep -iv python-multipart | grep -iv pyjwt | grep -iv pytest
