# Mkdocs and Material



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
