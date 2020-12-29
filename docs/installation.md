# Installation

Download the `uvicore-new-app` bash script

```bash
wget uvicore.io/uvicore-new-app /usr/local/bin
chmod a+x /usr/local/bin/uvicore-new-app
```

Create your first uvicore application
```bash
cd ~/Code
uvicore-new-app ./wiki
```

Once you answer all the questions, create your virtual environment of choice
```bash
cd ~/Code/wiki

# Create your virtual environment using your choice of env packages.
# poetry shell
# pipenv shell
# python -v venv env
# etc...

# And install the packages using the same environment choice.
# poetry install
# pipenv install
# pip -r requirements.txt
# etc...
```

Run your new application
```bash
./uvicore
```


Install optional packages depending on your application needs (example using poetry)
```bash
# Optional MySQL Support
poetry add databases[mysql]

# Optional SQLite Support
poetry add databases[sqlite]

# Optional PostgreSQL Support
poetry add databases[postgresql]
```
