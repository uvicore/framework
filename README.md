# Uvicore

**The Async Python Framework for Artisans. An Elegant Fullstack Python Web, API and CLI Framework**


This is a full stack python framework with everything included.  Built on other micro frameworks such as Starlette and FastAPI but resembling neither.  Uvicore feels like no other python framework you have ever used.  Think Laravel instead of Django or Flask.

More to come later.

Under heavy development.  Do NOT use this repository yet.


## Features

* Super fast, built on Starlette, FastAPI (but feels like neither) and other libraries.
* Equally well suited for complete CLI apps, Rest APIs with OpenAPI Docs and Traditional web applications.
* Fully asynchronous including CLI apps for unix socket programming and of course Websockets.
* Automatic API generation from all ORM models without a single line of View or Controller code.
* Full OpenAPI 3 automatically generated docs.
* All apps are packages and all packages are apps.  A modular framework with app override capability for configs, templates, assets, routes, models and more.  Reuse your app inside other apps as libraries for a Python native micro service architecture.  Or use the automatically generated API from ORM models for a Rest based micro service architecture with no extra work.
* Custom IoC (Inversion of Control) system to swap any concrete implementation without changing imports.
* Asynchronous database layer for MySQL, SQLite and Postgres.
* All new custom asynchronous ORM (NOT another django ORM clone) with support for every relationship including polymorphism.  Enjoy Laravel's Eloquent ORM?  You'll love this one.
* Full python type hinting for IDE code intellisense across every module including ORM model fields and methods.



## ToDo

* Write complete ORM tests with 100% coverage
* Need better ORM where AND with OR mixed around.  Currently it only does all ANDs then all WHEREs which won't work for complex queries.  For example grouping 2 where ANDs with an OR like so

```sql
SELECT DISTINCT posts.id, posts.unique_slug, posts.title, posts.other, posts.creator_id, posts.owner_id, attributes.*
FROM posts LEFT OUTER JOIN attributes ON attributes.attributable_type = 'posts' AND posts.id = attributes.attributable_id
WHERE
(attributes.key = 'post1-test1' and attributes.value = 'value for post1-test1')
or
(attributes.key = 'post2-test1' and attributes.value = 'value for post2-test1')
```

* Cannot update attributes from a parent (post.add('attributes'))...IntegrityError.  See posts seeder for notes.
