import uvicore
import inspect
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Mapper as MapperInterface


@uvicore.service()
class _Mapper(MapperInterface):
    """Entity mapper for model->table or table->model conversions"""

    def __init__(self, entity, *args):
        # Mapper can be used from the model as a @classmethod
        # or as an instance (post.mapper)
        if inspect.isclass(entity):
            # Mapper is being accessed from a static class (Post.mapper())
            # Both entity and instance are the entity itself, there is no instance
            self.entity = entity
            self.instance = entity
        else:
            # Mapper is being accessed from a class instance
            # So the actual entity is the instance.__class__ (the metaclass)
            # while the instance is the model class itself
            self.entity = entity.__class__
            self.instance = entity
        self.args = args

    def column(self) -> str:
        """Convert a model field name into a table column name"""
        fieldname = self.args[0]
        field = self.entity.modelfields.get(fieldname)
        if field:
            return field.column
        return fieldname

    def field(self):
        """Convert a table column name into a model field name"""
        column = self.args[0]
        for field in self.entity.modelfields.values():
            if field.column == column:
                return field.name
        return column

    def model(self):
        """Convert a dict or List[dict] into a model or List[Model]

        Works on a single record as dict - entity.mapper(DictModel).model()
        Works on a list of dict - entity.mapper(ListOfDictModel).model()
        Passes through if already a Model or List[Model]
        If mixed List of Dict and Model, converts all to Models
        """

        if self.args:
            # Model(s) are being passed in (entity.mapper(models).table())
            values = self.args[0]
        else:
            # No passed values, use self instance (model.mapper().table())
            values = self.instance

        single = False
        if type(values) != list:
            values = [values]
            single = True

        models = []
        for value in values:
            if type(value) == dict:
                # Convert dict to actual Model instance
                models.append(self.entity(**value))
            else:
                # Already a model instance
                models.append(value)

        if single: return models[0]
        return models

    def row_to_model(self):
        """Convert a single table row (SQLAlchemy RowProxy) into a model instance"""
        row = self.args[0]
        prefix = None
        if len(self.args) == 2: prefix = self.args[1]
        fields = {}

        #dump(row.keys(), prefix)
        for field in self.instance.__modelfields__.values():
            if not field.column: continue
            column = field.column
            if prefix: column = prefix + '__' + column
            if hasattr(row, column):
                fields[field.name] = getattr(row, column)
        return self.entity(**fields)

    def table(self):
        """Convert an model instance into a dictionary matching the tables columns

        Works on a single model - model.mapper().table() or entity.mapper(model).table()
        Or on a list of model instances - entity.mapper(ListOfModelInstances).tabel()
        Or on a list of model dictionaries - entity.mapper(ListOfModelDict).table()
        Does not convert or recurse into relations
        """
        if self.args:
            # Model(s) are being passed in (entity.mapper(models).table())
            models = self.args[0]
        else:
            # No passed models, use self instance (model.mapper().table())
            models = self.instance

        single = False
        if type(models) != list:
            models = [models]
            single = True

        tables = []
        for model in models:
            row = {}
            if type(model) == dict:
                # Model is a dict, convert to model instance
                model = self.entity(**model)

            for (field, value) in model.__dict__.items():
                field = self.entity.modelfields.get(field)
                if field.column and not field.read_only:
                    row[field.column] = value
            tables.append(row)

        # Return
        if single: return tables[0]
        return tables

                # bulk = []
        # for model in models:
        #     if type(model) == dict:
        #         # Value is a dictionary, not an actual model, convert to model
        #         model = entity(**model)
        #     #bulk.append(model.to_table())
        #     #bulk.append(model.mapper(model).table())
        #     bulk.append(model.mapper().table())

        # columns = {}
        # for (field, value) in self.instance.__dict__.items():
        #     field = self.entity.modelfields.get(field)
        #     if field.column and not field.read_only:
        #         columns[field.column] = value
        # return columns



    # # Field->Column
    # Mapper('slug').column() !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # # Column->Field
    # Mapper('unique_slug').field() !!!!!!!!!!!!!!!!!!!!!!!

    # # Model->TableDict
    # Mapper(User(email='adsf')).table() !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # # List[Model]->List[TableDict]
    # Mapper([
    #     User(email='asdf'),
    #     User(email='adsfasdf'),
    # ]).table()

    # # TableDict->Model
    # Mapper({
    #     'email': 'asdf'
    # }).model()

    # # List[TableDict]->List[Model]
    # Mapper([
    #     {
    #         'email': 'adsf',
    #     },
    #     {
    #         'email': 'asdasdf',
    #     }
    # ]).model()

    # # Table name - no, should be in db, has nothing todo with entities
    # Mapper('auth.users').tablename()



    # Usage:
    # Post.mapper().table()
    # post.mapper().table()
