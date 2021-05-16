# Installation

Download the `uvicore-installer` bash script

```bash
wget uvicore.io/uvicore-installer /usr/local/bin
chmod a+x /usr/local/bin/uvicore-installer
```

Create your first uvicore application
```bash
cd ~/Code
uvicore-installer ./wiki 0.1
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

