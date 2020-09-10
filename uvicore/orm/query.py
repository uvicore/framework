import operator as operators
import sqlalchemy as sa
from typing import Any, List, Tuple, Union


class QueryBuilder:

    def __init__(self, entity = None):
        self.entity = entity
        self.conn = entity.__connection__
        self.table = entity.__table__
        self._where = []
        self._where_or = []

    # def __get__(self, instance, owner):
    #     return self.__class__(owner)

    def where(self, column: Union[str, List[Tuple]], operator: str = None, value: Any = None):
        if type(column) == str:
            if not value:
                value = operator
                operator = '='
            self._where.append((column, operator.lower(), value))
        else:
            for where in column:
                if len(where) == 2:
                    self.where(where[0], '=', where[1])
                else:
                    self.where(where[0], where[1], where[2])
        return self

    def or_where(self, wheres: List[Tuple]):
        # if not value:
        #     value = operator
        #     operator = '='
        #self._where_or.append((column, operator, value))
        where_or = []
        for where in wheres:
            if len(where) == 2:
                where_or.append((where[0], '=', where[1]))
            else:
                where_or.append((where[0], where[1].lower(), where[2]))
        self._where_or = where_or
        return self

    async def find(self, pk_value: Any):
        primary = self._primary()
        self.where(primary, pk_value)
        table, query = self._build('select')
        results = await self.entity._fetchone(query)
        if results:
            return self.entity._to_model(results)

    async def get(self):
        # Build query
        table, query = self._build('select')
        print(query)

        # Execute query
        results = await self.entity._fetchall(query)

        # Convert results to List of entity
        models = []
        for row in results:
            models.append(self.entity._to_model(row))

        # Clear builder
        #entity.__query__ = {}

        # Return List of entity
        return models

    # async def insert(self, values: List):
    #     # Convert each entity into a dictionary of table data
    #     bulk = []
    #     for value in values:
    #         bulk.append(value._to_table())
    #     query = self.table.insert()
    #     await self.entity._execute(query, bulk)

    def _build(self, method: str = 'select'):
        table = self.table
        query = None

        # where
        #   select
        #   update (not in insert)
        #   delete

        # insert will never come into this get() or _build function

        if method == 'select':
            # if self._select:
            #     columns = []
            #     #for select in self._select:
            #     columns = [getattr(table.c, x) for x in self._select]
            #     query = sa.select(columns)
            # else:
            query = sa.select([table])

        # Where And
        if self._where:
            where_ands = self._build_where(self._where)
            query = query.where(sa.and_(*where_ands))

        # Where Or
        if self._where_or:
            where_ors = self._build_where(self._where_or)
            query = query.where(sa.or_(*where_ors))


        return table, query

    def _build_where(self, wheres: List[Tuple]):
        statements = []
        table = self.table
        for where in wheres:
            column, operator, value = where
            if type(value) == str and value.lower() == 'null': value = None
            if operator == 'in':
                statements.append(getattr(table.c, column).in_(value))
            elif operator == '!in':
                statements.append(sa.not_(getattr(table.c, column).in_(value)))
            elif operator == 'like':
                statements.append(getattr(table.c, column).like(value))
            elif operator == '!like':
                statements.append(sa.not_(getattr(table.c, column).like(value)))
            else:
                op = self._operator(operator)
                statements.append(op(getattr(table.c, column), value))
        return statements


    def _operator(self, operator: str):
        ops = {
            '=': operators.eq,
            '==': operators.eq,
            '!=': operators.ne,
            '>': operators.gt,
            '<': operators.lt,
        }
        return ops[operator]

    def _primary(self):
        for field in self.entity.__fields__.values():
            extra = field.field_info.extra
            if 'primary' in extra and extra.get('primary') == True:
                return field.name
