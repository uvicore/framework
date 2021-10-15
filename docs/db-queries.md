# Database Queries

## QueryBuilder

xyz


## Other

Maybe raw queries against an actual table module?



## Raw Queries without Table Modules

You can query database tables without a pre-defined SQLAlchemy table class.

```python
query = f"""
    SELECT
        *
    FROM
        sometable
    WHERE
        -- Parameterization works, or can just use somekey = 'somevalue', but is less secure
        somekey = :v
"""
params= {
    'v': 'parameterized value here',
}
results = await uvicore.db.fetchall(query, params, connection='myapp')
```

Can also use `fetchone()` and `execute()` for INSERTS, UPDATES and DELETES
