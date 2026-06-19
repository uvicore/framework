"""
Inline ORM table definitions.

A model may define its schema INLINE via __connection__ + __tablename__ + a raw
__table__ list of SQLAlchemy columns, instead of pointing __tableclass__ at a
separate Table class.  The ModelMetaclass builds a real sa.Table from that list
(mirroring uvicore.database.Table) so inline and separate-file tables behave
identically.

The models are defined INSIDE the tests on purpose: the metaclass builds the
sa.Table at class-definition time, which must happen after the database has
bootstrapped (the app1 fixture), not at module import / pytest collection time.
"""
import pytest
import sqlalchemy as sa
from sqlalchemy.schema import CreateTable, DropTable
from typing import Optional


@pytest.mark.asyncio
async def test_inline_table_builds_real_sa_table(app1):
    import uvicore
    from uvicore.orm import Model, ModelMetaclass, Field

    @uvicore.model('tests.InlineWidgetA')
    class Widget(Model['Widget'], metaclass=ModelMetaclass):
        __connection__ = 'app1'
        __tablename__ = 'zinline_widgets_a'
        __table__ = [
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String(length=50)),
            sa.Column('size', sa.Integer),
        ]
        __table_kwargs__ = {'sqlite_autoincrement': True}
        id: Optional[int] = Field('id', primary=True, read_only=True)
        name: str = Field('name')
        size: int = Field('size')

    # The raw list was turned into a real sa.Table associated with app1's metadata
    assert isinstance(Widget.table, sa.Table)
    assert Widget.tablename == 'zinline_widgets_a'
    assert [c.name for c in Widget.table.columns] == ['id', 'name', 'size']
    assert Widget.connection == 'app1'
    # The built table shares the connection's metadata
    assert Widget.table.metadata is uvicore.db.metadata('app1')

    # Keep the shared app1 metadata clean
    Widget.table.metadata.remove(Widget.table)


@pytest.mark.asyncio
async def test_inline_table_end_to_end_crud(app1):
    import uvicore
    from uvicore.orm import Model, ModelMetaclass, Field

    @uvicore.model('tests.InlineWidgetB')
    class Widget(Model['Widget'], metaclass=ModelMetaclass):
        __connection__ = 'app1'
        __tablename__ = 'zinline_widgets_b'
        __table__ = [
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String(length=50)),
            sa.Column('size', sa.Integer),
        ]
        id: Optional[int] = Field('id', primary=True, read_only=True)
        name: str = Field('name')
        size: int = Field('size')

    await uvicore.db.execute(CreateTable(Widget.table), connection='app1')
    try:
        await Widget.insert([
            {'name': 'alpha', 'size': 10},
            {'name': 'beta', 'size': 20},
        ])
        rows = await Widget.query().order_by('id').get()
        assert len(rows) == 2
        assert rows[0].name == 'alpha'
        assert isinstance(rows[0].id, int)              # db-generated pk works inline too

        big = await Widget.query().where('size', '>', 15).get()
        assert len(big) == 1 and big[0].name == 'beta'
    finally:
        try:
            await uvicore.db.execute(DropTable(Widget.table), connection='app1')
        finally:
            Widget.table.metadata.remove(Widget.table)


@pytest.mark.asyncio
async def test_inline_table_requires_connection_and_tablename(app1):
    import uvicore
    from uvicore.orm import Model, ModelMetaclass, Field

    # An inline __table__ list with no __connection__/__tablename__ is a clear error
    with pytest.raises(Exception, match='__connection__ and __tablename__'):
        @uvicore.model('tests.InlineWidgetBad')
        class Widget(Model['Widget'], metaclass=ModelMetaclass):
            __table__ = [sa.Column('id', sa.Integer, primary_key=True)]
            id: Optional[int] = Field('id', primary=True, read_only=True)
