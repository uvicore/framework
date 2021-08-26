# Installation

Download the `uvicore-installer` bash script

<!-- wget uvicore.io/uvicore-installer /usr/local/bin -->
```bash
cd ~
wget https://raw.githubusercontent.com/uvicore/framework/master/bin/uvicore-installer
sudo mv uvicore-installer /usr/local/bin
sudo chmod a+x /usr/local/bin/uvicore-installer
```

Create your first uvicore application
```bash
cd ~/Code
uvicore-installer wiki
```

Once you answer all the questions, create your virtual environment of choice
```bash
cd ~/Code/wiki

# Create your virtual environment using your choice of env packages.
# poetry shell
# pipenv shell
# python -v venv env
# etc...
```

Now install the python dependencies
```bash
# And install the packages using the same environment choice.
# poetry install
# pipenv install
# pip -r requirements.txt
# etc...
```

Run your new application
```bash
./uvicore
./uvicore http serve
```

Visit `http://localhost:5000` in your browser





## Example Output of Installer

```
:: Uvicore Installer ::

Actions:
  * You are about to create a new directory wiki
  * You are about to clone master branch from https://github.com/uvicore/app into wiki
  * Once cloned, the wiki/.install/install.py python script will be executed to ask install questions

WARNING:
Please ensure you TRUST the repository you are cloning if 3rd party!
Please ensure you have read the repositories .install/install.py file if unsure!

Continue to clone and execute wiki/.install/install.py (y/N)? y

:: Installing Uvicore Package Schematic master https://github.com/uvicore/app into wiki ::
--------------------------------------------------------------------------------
  * Creating directory wiki
  * Cloning https://github.com/uvicore/app master branch into wiki
Cloning into 'wiki'...
remote: Enumerating objects: 66, done.
remote: Counting objects: 100% (66/66), done.
remote: Compressing objects: 100% (49/49), done.
remote: Total 66 (delta 6), reused 41 (delta 3), pack-reused 0
Receiving objects: 100% (66/66), 61.37 KiB | 628.00 KiB/s, done.
Resolving deltas: 100% (6/6), done.
  * Running the python installer script wiki/.install/install.py



================================= Package Name =================================
Package name is the actual "python package" compatible name. Most uvicore
packages should be given a vendor.package style namespace, preferably your name, developer
alias or company name.  Examples of what to enter here:
  * mreschke.wiki
  * yourname.blog
  * companyname.themes
Please do not skip the namespace and create root packages as they will
eventually cause namespace collisions amoung developers.  All dashes will be
converted to underscores.

Package Name (mreschke.wiki): mreschke.wiki


================================ Friendly Name ================================
Friendly name of this package, for example: Wiki, Acme Blog, Reporting Suite...

Friendly Name (mReschke Wiki): Wiki


================================== Your Name ==================================
Your full name is used in one of poetry pyproject.toml, setup.py or other
config type files.

Your Full Name (Matthew Reschke): Matthew Reschke


================================== Your Email ==================================
Your email is used in one of poetry pyproject.toml, setup.py or other
config type files.

Your Email (mreschke@example.com): mreschke@example.com


============================ Preferred Environment ============================
There are many python virtual environments people prefer.  This installer
will create the proper FILES (pyproject.toml, Pipfile, requirements.txt...) for
you but it will NOT actually create or activate any environments nor will it
install any package dependencies.  The installer will leave that up to you.

1)  Poetry - Creates a pyproject.toml poetry file
2)  Pipenv - Creates a Pipfile pipenv file
3)  Requirements.txt - Creates a simple requirements.txt file

Virtual Environment (1): 1


################################################################################


You are are about to customize this blank uvicore package schema as follows:
  * ('path', '~/Code/wiki')
  * ('package_name', 'mreschke.wiki')
  * ('friendly_name', 'Wiki')
  * ('your_name', 'Matthew Reschke')
  * ('your_email', 'mreschke@example.com')
  * ('environment', 'Poetry')

Continue (y/n)? y


:: Deleting unused test files and folders ::
  * Deleting .git
  * Deleting poetry.lock
  * Deleting pyproject.toml
  * Deleting .python-version

:: Copying stubbed files ::
  * Copying .install/stubs/pyproject.toml to pyproject.toml
  * Copying .install/stubs/README.md to README.md

:: Searching and Replacing acme.appstub in all files ::
  * Search and Replace in /tests/test_example.py
  * Search and Replace in /tests/conftest.py
  * Search and Replace in /tests/__init__.py
  * Search and Replace in /acme/appstub/services/bootstrap.py
  * Search and Replace in /acme/appstub/services/appstub.py
  * Search and Replace in /acme/appstub/models/__init__.py
  * Search and Replace in /acme/appstub/http/server.py
  * Search and Replace in /acme/appstub/http/routes/web.py
  * Search and Replace in /acme/appstub/http/routes/api.py
  * Search and Replace in /acme/appstub/http/controllers/welcome.py
  * Search and Replace in /acme/appstub/http/api/welcome.py
  * Search and Replace in /acme/appstub/database/tables/__init__.py
  * Search and Replace in /acme/appstub/database/seeders/__init__.py
  * Search and Replace in /acme/appstub/config/package.py
  * Search and Replace in /acme/appstub/config/app.py
  * Search and Replace in /acme/appstub/commands/welcome.py
  * Search and Replace in uvicore
  * Search and Replace in .env-example
  * Search and Replace in LICENSE
  * Search and Replace in pyproject.toml

:: Renaming files to new package name ::
  * Renaming acme/appstub/http/views/appstub to acme/appstub/http/views/wiki
  * Renaming acme/appstub/services/appstub.py to acme/appstub/services/wiki.py
  * Copying .env-example to .env

:: Moving package folder to new package name ::
  * Renaming acme/appstub to mreschke/wiki

:: Cleaning up ::
  * Deleting acme
  * Deleting .install


################################################################################


!! Uvicore installation complete!  You must now MANUALLY perform the following: !!
  * cd ~/Code/wiki
  * poetry shell
  * poetry install
  * Modify the LICENSE file to your liking
  * Modify the license listed in your pyproject.toml file
  * Modify .gitignore and .editorconfig to your liking
  * Add code to git or other source control provider
  * Run ./uvicore
  * Run ./uvicore wiki welcome
  * Run ./uvicore http serve
  * Visit http://127.0.0.1:5000
  * Visit http://127.0.0.1:5000/api/docs

Thanks for using Uvicore!
```
