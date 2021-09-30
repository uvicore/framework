# Mkdocs and Material


## Common Links

[Service Provider](/service-providers/)
[Pydantic](/orm-pydantic/)
[Uvicore CLI](/cli/)
[SuperDict](/superdict/)

[IoC](/ioc/)

[Uvicore Installer](/installation/)

[encode/databases](https://github.com/encode/databases)

[SQLAlchemy Core](https://docs.sqlalchemy.org/en/13/core/tutorial.html)

[View Composers](/view-composers/)

## Common names

yourname.yourapp



## Common paragraphs


In order to use the database layer with Uvicore you must first ensure you have installed the `database` extras from the framework.  This is by default already included in the `uvicore-installer`.
```
# Poetry pyproject.toml
uvicore = {version = "0.1.*", extras = ["database", "redis", "web"]}

# Pipenv Pipfile
uvicore = {version = "==0.1.*", extras = ["database", "redis", "web"]}

# requirements.txt
uvicore[database,redis,web] == 0.1.*
```



After the database extras have been installed you must update your `config.package.py` `dependencies` OrderedDict in `config/package.py`
```python
    'dependencies': OrderedDict({
        'uvicore.foundation': {
            'provider': 'uvicore.foundation.services.Foundation',
        },
        # ...
        'uvicore.database': {
            'provider': 'uvicore.database.services.Database',
        },
        # ...
    }),
```




## Admonitions

https://squidfunk.github.io/mkdocs-material/reference/admonitions/#supported-types

!!! note
    Note here
    and here

---

!!! tip
    Tip here - NO title
    and here

    ```python
    def hi():
        """Code in a admonition provided by superfences"""
        pass
    ```

---

!!! note ""
    No title use ""

---

!!! check
    asdf

---

!!! info "with title here"
    Info here
    and here

---

!!! warning "With title"
    Warning here

---

!!! danger
    asdfasdfasdf
    asdf

---

???+ info "Collapsible Admonition"
    Collapsible note
    Plus means default to open

---

!!! seealso
    asdfasdfasdf
    asdf


## Content Tabs

!!! example

    === "Mac"

        ```bash
        do mac stuff
        ```

    === "Linux"

        ```bash
        do linux stuff
        ```


## Footnotes

Lorem ipsum[^1] dolor sit amet, consectetur adipiscing elit.[^2]



[^1]: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
[^2]:
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    multi line


## Icons and Emojis

Smile Emoji :smile:

See https://emojiguide.com/ or https://emojipedia.org for all emoji.

I use the twitter emoji

You can also just paste 🧒 emoji right in markdown.  Or use things like :slightly_frowning_face:

This theme comes with these 3 FULL SETS of icons!

* :material-account-circle: – `.icons/material/account-circle.svg`
* :fontawesome-regular-laugh-wink: – `.icons/fontawesome/regular/laugh-wink.svg`
* :octicons-octoface-16: – `.icons/octicons/octoface-16.svg`


## Tasklist


* [x] Lorem ipsum dolor sit amet, consectetur adipiscing elit
* [ ] Vestibulum convallis sit amet nisi a tincidunt
    * [x] In hac habitasse platea dictumst
    * [x] In scelerisque nibh non dolor mollis congue sed et metus
    * [ ] Praesent sed risus massa
* [ ] Aenean pretium efficitur erat, donec pharetra, ligula non scelerisque
