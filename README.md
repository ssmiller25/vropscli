


* Inspired by https://github.com/johnddias/vropsrelay
* Using Pipenv for package management.  See https://jcutrer.com/howto/dev/python/pipenv-pipfile for basic tutorial


Basic usage at [USAGE.md](USAGE.md)

# First Time

* Run ```pipenv --python 3.6``` In current directory
* Run ```pipenv update``` to ensure everything is up to date

# To Use

* Run ```pipenv shell``` to enter environment

# To Distribute

* On "target" platofrm (Windows, Mac, etc), run:
```
pipenv install pyinstaller
pyinstaller -F vropscli.py
```
