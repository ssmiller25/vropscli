# vROpsCLI

A utiltiy to assist in managing a vRealize Operation Manager (vROps) environment through the CLI.  A user can perform MP installs and upgrades, licensing management,
endpoint configuration, credential management, and more!  The design is focused around exposing core functionality that can be scripted to make more complex solutions.

* Downloads are available on [the release page](https://github.com/BlueMedora/vropscli/releases).
* Usage details can be located at [USAGE.md](USAGE.md)
* Examples scripts that use the utilty are located in the [examples directory](https://github.com/BlueMedora/vropscli/examples/)


# Development Environment Setup

* Run ```pipenv --python 3.6``` In current directory
* Run ```pipenv update``` to ensure everything is up to date

## To Use

* Run ```pipenv shell``` to enter environment

## To Distribute

* On "target" platofrm (Windows, Mac, etc), run:
```
pipenv install pyinstaller
pyinstaller -F vropscli.py
```

# Notes

* Inspired by https://github.com/johnddias/vropsrelay
* Using Pipenv for package management.  See https://jcutrer.com/howto/dev/python/pipenv-pipfile for basic tutorial
