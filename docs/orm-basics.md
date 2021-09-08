# ORM Basics


## Introduction
asdf



## Hooks

In your model, you can override these defs

```python
# New records only, actual INSERTS
_before_insert(self)
_after_insert(self)

# Both insert or update, any save to the database
_before_save(self)
_after_save(self)

# Delete
_before_delete(self)
_after_delete(self)
```

## Events

The ORM hooks also fire named string based events to use anywhere else in the system.  String is based on the models FQN (fully qualified name).  For example if the model is `uvicore.auth.models.user.User` the event names would be

```
uvicore.orm-{uvicore.auth.models.user.User}-BeforeInsert
uvicore.orm-{uvicore.auth.models.user.User}-AfterInsert

uvicore.orm-{uvicore.auth.models.user.User}-BeforeSave
uvicore.orm-{uvicore.auth.models.user.User}-AfterSave

uvicore.orm-{uvicore.auth.models.user.User}-BeforeDelete
uvicore.orm-{uvicore.auth.models.user.User}-AfterDelete
```
