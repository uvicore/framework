# Cache 100

## Summary

Uvicore comes with a built-in caching system capable of connecting to any number of backend storage services.  Uvicore currently ships with `Redis` and `In App Memory` caching backends.  Additional backend drivers can easily be created by the community.

The caching system is generally used to cache expensive database queries or other data lookups.  But of course, you are free to use it for any arbitrary key/value storage.  Just remember, cache is not a database, it expires unless you define otherwise.  Even still, it should be considered volatile.


## Configuration

Most of uvicore's configuration is set to sensible defaults with quick and easy `.env` file overrides.

By default, caching is set to use the `array` store.  This means you can start using caching right away without any further configuration.

If you want to switch to a `Redis` backend caching system, simply edit your `.env` file and configure these simple values
```
# Cache redis connection
REDIS_CACHE_HOST=127.0.0.1
REDIS_CACHE_PORT=6379
REDIS_CACHE_DB=2

# Cache configuration
CACHE_STORE=redis
CACHE_EXPIRE=600
```

!!! tip
    `.env` file tweaks are all you need to get started.  You are good to go.

    If you want to dig deeper into the configuration, keep reading...


All cache configuration is done at the running application level.  This means your `config/app.py` config.  In that file you will notice this entry
```python
    # --------------------------------------------------------------------------
    # Cache Configuration
    # If no cache config defined, the default of 'array' caching will be used
    # --------------------------------------------------------------------------
    'cache': {
        'default': env('CACHE_STORE', 'array'),  # redis, array
        'stores': {
            'redis': {
                'driver': 'uvicore.cache.backends.redis.Redis',
                'connection': 'cache',
                'prefix': env('CACHE_PREFIX', 'acme.appstub::cache/'),
                'seconds': env.int('CACHE_EXPIRE', 600),  # 0=forever
            },
        },
    },
```
This entire top-level `cache` config key is optional.  If not defined, caching is defaulted to using the `array` store.  Caching can never be "disabled", because other packages you depend on may be using a ton of cache calls.  The default of `array` ensures those calls function properly even if you don't have Redis or some other backend available.

In this example, the `stores` Dict contains one cache store by a named key `redis`.  The `default` string defines which store is used when you make a call to `uvicore.cache` without explicitly defining which store to use.  Simply adjusting your `.env` with `CACHE_STORE=redis` ensures all calls to cache will now be using the `redis` store.

The `driver` section defines the backend python adapter that handles redis caching, in this case, the built-in `uvicore.cache.backends.redis.Redis` python module.  Any community member can create a cache compatible backend by examining that module and adhering to the `CacheInterface`.

The `prefix` section defines the prefix added to each key that is saved to cache.  Good for Redis if you have dozens of apps using cache.  This prefix is also how `cache.flush()` can delete all cache entries it "owns" without flushing the entire Redis database.

The `seconds` are the default expiration given to each cache key.  Cache is generally meant to expire.  If you don't ever want key/values to expire, set `seconds: 0`.  This config defines the default behavior of `cache.put()` and other save methods.  You can also override each individual call using the optional seconds parameter `cache.put('mykey', 'myvalue', seconds=50)`

The `connection` key is pointing to a redis database connection key which is defined in your packages `config/package.py` configuration.  All packages created from the [Uvicore Installer](/installation/) already contain a `cache` redis connection key.  All you have to do is ensure your `.env` has the proper values to override it.
```python
    # --------------------------------------------------------------------------
    # Redis Connections
    # --------------------------------------------------------------------------
    'redis': {
        'default': env('REDIS_DEFAULT', 'wiki'),
        'connections': {
            'wiki': {
                'host': env('REDIS_WIKI_HOST', '127.0.0.1'),
                'port': env.int('REDIS_WIKI_PORT', 6379),
                'database': env.int('REDIS_WIKI_DB', 0),
                'password': env('REDIS_WIKI_PASSWORD', None),
            },
            'cache': {
                'host': env('REDIS_CACHE_HOST', '127.0.0.1'),
                'port': env.int('REDIS_CACHE_PORT', 6379),
                'database': env.int('REDIS_CACHE_DB', 2),
                'password': env('REDIS_CACHE_PASSWORD', None),
            },
        },
    },
```



## Stores

Uvicore ships with 2 backend cache stores, `Redis` and `Array`.  The community (that means YOU) may easily create other stores like memcache.

The `array` store simply stores cached data in the running apps memory.  Array store does have full TTL expiry!  It should act just like redis cache except that it is in your running apps memory.  When the app dies, cache is gone forever.  This means cache entries with no expiry (seconds=0) will disappear when the app stops. Array is best used for testing or when you import another uvicore package that uses caching, but you don't have redis and don't really care about the cache.



## Expiration

All values inserted to the cache store always use the config expire TTL seconds.
This means all keys will automatically delete themselves.  You can override each insert operation using the optional `seconds=` parameter.  Using `seconds=0` means the key
will NEVER expire.  If you want every key to persist forever, update your config seconds to 0.



## Usage

You can obtain a cache instance in multiple ways.  The easiest and **recommended** method is to simply use `uvicore.cache` since `import uvicore` is most likely already at the top of every file you will use.
```python
import uvicore
uvicore.cache.get('key1')


# Or

import uvicore.cache
cache.get('key1')
```

You can optionally get the cache instance from the [IoC](/ioc/) either by `uvicore.ioc.make` or by simply importing the cache manager.  In either case, you must manually `connect()` to start using the cache.
```python
# These options require you to run .connect().  If .connect() has no parameters, the default
# cache store is used from your config.  You may also specify the store with .connect('redis')
from uvicore.cache.manager import Manager as Cache
cache = Cache.connect()

# Or using .make()
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

The `.remember()` method will get one or more values if exist, if not, it will set the default to the cache store and return it.  Different that `.get()` with a `default=` because `.remember()` will set the default in the cache store.  This is the **recommended** method to automatically cache expensive database queries or lookups into cache.  Works with callbacks!
```python
# Single key value
await cache.remember('key1', 'default key3')

# Multiple key value returns.  If any one does not exist, the default is SET in the cache store
await cache.remember(['key1', 'key2'], 'default value')

# Using custom TTL seconds
await cache.remember('key1', 'default value', seconds=60)

# Default can be a callback.  This is ideal for retrieving a value from cache if exists.  If not
# exist, run a complex query and set the queries results into the cache.
def wiki_posts():
    return await Post.query().get()
await cache.remember('all_posts', wiki_posts)
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
