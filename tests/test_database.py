import pytest
import uvicore

from uvicore.support.dumper import dump
from starlette.testclient import TestClient


@pytest.mark.asyncio
async def xtest_database(app1):
    from uvicore.auth.models.user import User
    from app1.models.post import Post


    # db = uvicore.db.connect()



    # engine = await db.engine()
    # table = User.__table__
    # query = table.select()
    # results = await db.fetchall(query)
    # dump(results)

#    users = db.connection('wiki').table('users').select('email').get()

    from uvicore import db

    #user = await db.table('auth_users').find(1)
    #user = await db.conn('app1').table('auth_users').find(1)
    #user = await db.query().table('auth_users').find(1)
    # user = await (
    #     db.query('auth')
    #     .select('email')
    #     .table('users')
    #     .where('id', 1)
    #     .get()
    # )
    # dump(user)

    # Works, join
    # from sqlalchemy import select
    # posts = Post.__table__
    # users = User.__table__
    # query = (
    #     select([
    #         posts.c.id,
    #         posts.c.title,
    #         users.c.email,
    #     ])
    #     .select_from(posts.join(users))
    #     #work!  .select_from(posts.join(users, posts.c.creator_id == users.c.id))
    # )
    # results = await db.fetchall(query)
    # dump(results)


    post = await (
        db.query('app1')
        .table('posts')
        .join('users', 'posts.creator_id', '=', 'users.id')
        .get()
    )
    dump(post)



    # Works
    #users = await db.query().table('auth_users').get()
    #dump(users)



    # db = await uvicore.db.database()
    # table = User.__table__
    # query = table.select()
    # results = await db.fetch_all(query)
    # for result in results:
    #     #dump(type(result))
    #     #dump(result.email)
    #     dump(User._to_model(result))

    #dump(User.email1())

    #user = await User.find(1)
    #dump(user._info())

    # User._query.find()
    # User._query.where('adf', 'asdf').all()
    # User._query.all()

    # User.query().find()
    # User.query().where('asdf', 'asdf').all()
    # User.query().all()

    # User.qfind(1)
    # User.qwhere('asdf', 'asdf').qall()
    # User.qall()
    # User.qsave()

    # User.dbfind(1)
    # User.dbwhere('asdf', 'asdf').dbwhere('asdf').dball()
    # User.dbsave()
    # User.dbinsert([])

    # User._find(1)
    # User._where('asdf', 'asdf')._where('asdf', 'asdf')._all()
    # User._all()
    # User._insert('asdf')

    # User.where('info_', 'matthew')






    # #print(app.providers)

    # #dump(uvicore.app.providers)

    # #dump(uvicore.db.connections)

    # from app1.models.post import Post
    #from uvicore.auth.models.user import User
    # #dump(Post.info())

    # #metakey = 'sqlite:///:memory'

    #users = await User.all()
    #dump(users)




    # client = TestClient(uvicore.app.http.server)
    # #print(uvicore.app.http.server)
    # response = client.get('/app1/api/posts')
    # dump(response)

    #dump(client)




    #from uvicore.support import path
    #print(path.find_base(__file__) + '/testapp/app')
    assert 1 == 2
    #assert __version__ == '0.1.0'


