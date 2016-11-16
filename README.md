## Prerequisites
sqlite3
python3

Run `pip install -r requirements.txt` to get dependencies.

Tested in OSX and arm linux (debian wheezy)

## How to run

```
python setup.py develop

# Set up the database
python quippy_wat/scripts/initializedb.py development.ini

pserve development.ini

# go to http://localhost:6543/quips
```
