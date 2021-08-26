# Directory Structure

A fresh uvicore project called `mreschke.wiki` using the Poetry python virtual environment will have the following folder structure

```
├── bin/
│   ├── test-cov-html.sh
│   ├── test-cov.sh
│   └── test.sh
├── mreschke/
│   └── wiki/
│       ├── commands/
│       │   └── welcome.py
│       ├── config/
│       │   ├── app.py
│       │   └── package.py
│       ├── database/
│       │   ├── seeders/
│       │   │   └── __init__.py
│       │   └── tables/
│       │       └── __init__.py
│       ├── http/
│       │   ├── api/
│       │   │   └── welcome.py
│       │   ├── assets/
│       │   │   ├── css/
│       │   │   ├── images/
│       │   │   └── js/
│       │   ├── controllers/
│       │   │   └── welcome.py
│       │   ├── public/
│       │   │   ├── assets/
│       │   │   │   └── wiki/
│       │   │   │       ├── css/
│       │   │   │       ├── images/
│       │   │   │       └── js/
│       │   │   ├── favicon.ico
│       │   │   └── robots.txt
│       │   ├── routes/
│       │   │   ├── api.py
│       │   │   └── web.py
│       │   ├── server.py
│       │   └── views/
│       │       └── wiki/
│       │           └── welcome.j2
│       ├── models/
│       │   └── __init__.py
│       └── services/
│           ├── bootstrap.py
│           └── wiki.py
├── tests/
│   ├── conftest.py
│   ├── __init__.py
│   └── test_example.py
├── .editorconfig
├── .env
├── .env-example
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
└── uvicore
```
