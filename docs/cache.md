# Cache

All values inserted to the cache store always use the config expire TTL seconds.
This means all keys will automatically delete themselves.  You can override each insert operation using the optional `seconds=` parameter.  Using `seconds=0` means the key
will NEVER expire.  If you want every key to persist forever, update your config seconds to 0.

## Stores

There are currently 2 stores.  `Redis` and `Array`

The `array` store simply stores cached data in memory.  Array store does have full TTL expiry!  It should act just like redis cache except that it is in your running apps memory.  When the app does, cache does.  Only stores TTL=0 (infinite) data as long as the app lives.  Expired entries are only deleted (memory cleared) when that key is accessed somehow.  There is no expired garbage collector unless the key is accessed.



## Usage

You can obtain a singleton cache instance in multiple ways

```python

# These options are already .connect() to the default cache store
from uvicore import cache
cache = uvicore.cache  # Or just use uvicore.cache everywhere

# These options require you to run .connect().  If .connect() is empty, the default
# cache store is used.  You may also specify the store with .connect('redis')
from uvicore.cache.manager import Manager as Cache
cache = Cache.connect()
cache = uvicore.ioc.make('cache').connect()
```

Use an alternate store other than the default defined in your config
```python
await cache.store('redis').get('key1')
```

Get one or more values from cache
```python
# Get a single value by key
await cache.get('key1')

# Get a dictionary of multiple key value pairs if requesting multiple keys
await cache.get(['key1', 'key2'])
```

Get one or more values from cache with a default value if not exists.  If key does not exist return a DEFAULT value, but do NOT set that default back to the cache store.
```python
await cache.get('missing1', default='default if not found')

# Works with multiple key value pairs.  Returned dictionary will either have the data
# for each key, or use the default value
await cache.get(['missing1', 'key1'], default='not found')
```

Remember.  Get one or more values if exist.  If not SET the default to the cache store and return it.  Different that `.get()` with a `default=` because `.remember()` will set the default in the cache store.  Works with callbacks!
```python
# Single key value
await cache.remember('key1', 'default key3')

# Multiple key value returns.  If any one does not exist, the default is SET in the cache store
await cache.remember(['key1', 'key2'], 'default value')

# Using custom TTL seconds
await cache.remember('key1', 'default value', seconds=60)

# Default can be a callback.  This is ideal for retrieving a value from cache if exists.  If not
# exist, run a complex query and set the queries results into the cache.
def expensive_query():
    pass
await cache.remember('key1', expensive_query)
```

Check if a single cache key exists
```python
await cache.has('key1')
```

Put a single key value in cache
```python
await cache.put('key1', 'value1')

# If no seconds is passed, uses default TTL seconds from config
await cache.put('key1', 'value1', seconds=60)
```

Put multiple key value pairs into cache
```python
await cache.put({
    'key3': 'value 3',
    'key4': 'value 4',
})
# with optional seconds= parameter
```

Pull one or more values from cache and delete after retrieval. Like get, but
once retrieved, cache entry is DELETED.
```python
# Single pull
await cache.pull('key1')

# Multiple
await cache.pull(['key1', 'key2'])
```

Add a single value only if not exists.  Like put, but will not overwrite an existing value.
```python
# Return true if success (meaning key did not exist and we added it), otherwise
# false for already exists
await cache.add('key1', 'value1')
```

Touch a key.  This alters the last access time of a key but does not retrieve the value.
If `seconds=` are passed it will RESET the TTL to the given seconds.
```python
# Update the last access time, but do NOT modify the TTL
await cache.touch('key1')

# Update the last access time and reset the TTL to seconds=
await cache.touch('key1', seconds=60)

# Returns true if key exists and we touched or modified the TTL.  False if key does not exist.
```

Increment a key.  If key does not exist, it will create it.  Increment returns the current value after the increment
```python
# Uses default TTL seconds
new_int = await cache.increment('key1')

# Custom TTL seconds expire
await cache.increment('key1', seconds=60)

# Custom increment integer
await cache.increment('key1', 10)
```

Forget (delete) one or more keys
```python
# A single key
await cache.forget('key1')

# Multiple keys
await cache.forget(['key1', ['key2'])
```

Delete all cache keys.  This is "redis safe" as it only deletes keys in the redis database
that begin with the cache prefix defined in your config.  It does NOT delete all keys in your database!
```python
await cache.flush()
```
