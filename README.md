# Uvicore

Welcome to Uvicore!  The Async Python Framework for Artisans. An Elegant Fullstack Python Web, API and CLI Framework.


## Warning

This project is currently under heavy **active** development.  Although I am using this framework in Production personally, I would advise you against it just yet.  It is mostly stable but not feature complete.


## What is Uvicore?

* A fullstack blazing fast asynchronous python Web, API and CLI framework.
* Inspired by the elegance and design quality of Laravel.  Though it is NOT a Laravel clone by any stretch of the imagination.  If you want Laravel, go get Laravel and stop complaining about PHP :)
* Not a mirco framework, up and running with a complete system in minutes, no boilerplate.
* Deeply config driven with extremely deep merged and overridable package configs.
* Package based.  Apps are packages, packages are apps.  No "shell" or "project" required.  Run it or use it in another running app, all in one.
* Service Provider style package bootstrapping.
* Full async database query builder build on encode/databases...or use the ORM!
* Elegant custom async ORM inspired by Eloquent (but still very different).  Not another Django ORM clone thank God!
* Complex and complete ORM relations including polymorphism.
* Easy redis caching system (great for optimizing API database hits).
* IoC (Inversion of Control).  Framework looks back to your app to determine import of every module.  You can override ANYTHING from core or other developers packages!
* Blazing fast DUAL routers for Web and API usage, built on Starlette and FastAPI.
* Perfectly suited for old-school server-side traditional post-back template driven web apps.
* Perfectly suited for API backend only, quicker and easier that Django Rest Framework, built on FastAPI but with fullstack routing, controllers, ORM, caching...no boilerplate.
* Websockets!  Well yeah, its async!
* ORM Models can query local database OR switch to remote API and query the data over uvicore automatic ORM crud APIs without code changing, syntax identical.  What?  This means your package IS the "server" and also the "client/sdk for API access".  Let that sink in a bit.
* Automatic ORM Crud API's out of the box.  Never write a single controller or endpoint again.  Simply build Models. Instant API with granular roles and permission management.
* Granular groups, roles, permission management with Authentication middleware and route guards.
* Quick and easy JWT authentication with an external IDP (FusionAuth!)
* Multiple middleware authenticators.  APIs can autodetect and respond to Basic Auth, Digest, JWT and more.
* Automatic OpenAPI 3.0 generated documentation for all API routes include automatic model router.
* Fully async CLI based on asyncclick.  Query async ORM models and jobs from the CLI exactly as you would from an async web controller.  Everything can call async methods!
* Event pub/sub system.  Subscribe to all Uvicore core events in the bootstrap process, ORM CRUD, authentication systems and any event fired from your packages.
* And much more....documentation to come soon!



## Feeling Dangerous?

It works with a full installer, but there is little documentation yet so its up to you to deduce the system, though it's reasonably self explanatory.

```bash
wget https://raw.githubusercontent.com/uvicore/framework/master/bin/uvicore-installer
mv uvicore-installer /usr/local/bin
chmod a+x /usr/local/bin/uvicore-installer

cd ~/Code
uvicore-installer  # To see help
uvicore-installer ./blog

# Follow the post-installation instructions
# Review your .env
# Review all configs
# Download this https://github.com/uvicore/framework code and review the guts since there are no docs yet :)  Look in the tests/apps/app1 folder for a small test app to glean how to use it.
# Sorry, it's not done yet, but working hard on it!
```


## Stable v1.0 Roadmap

I am tracking issues and enhancements for v1.0 in the Issues Milestones (and on a million sticky notes).  Before this project can be considered ready for public use I need to complete the following:

* Proof the system by finishing several Production sites, APIs and CLIs at my current company.
* Write far more tests and attempt 100% coverage
* Build the main website at https://uvicore.io
* Complete elegant documentation (ever read Laravels docs?  Like that.) at https://docs.uvicore.io



## License

The Uvicore framework is open-sourced software licensed under the MIT license.
