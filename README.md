# vROpsCLI

A utility to assist in managing a vRealize Operation Manager (vROps) environment through the CLI.  A user can perform MP installs and upgrades, licensing management,
endpoint configuration, credential management, and more!  The design is focused around exposing core functionality that can be scripted to make more complex solutions.

* Downloads are available on [the release page](https://github.com/BlueMedoraPublic/vropscli/releases).
* Usage details can be located at [USAGE.md](USAGE.md)
* Examples scripts that use the utilty are located in the [examples directory](https://github.com/BlueMedoraPublic/vropscli/examples/)


# Development Environment Setup

* Make sure to have Python and Pipenv install
** For Mac, Install Homebrew (this may take a while if Xcode needs to be installed):
```/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"```
** ```brew install pipenv```
* Run ```pipenv --python 3.7``` In current directory
* Run ```pipenv update``` to ensure everything is up to date

## To Use

* Run ```pipenv shell``` to enter environment

## To Distribute

Make sure to compile this on the *oldest* OS you wish to support with your binary!
* If you wish to compile to work natively on a vROps system (SLES 11), follow the direction in [vropsbuild.md](vropsbuild.md)
```
pipenv install pyinstaller
pyinstaller -F vropscli.py
```

# Notes

* Inspired by https://github.com/johnddias/vropsrelay
* Using Pipenv for package management.  See https://jcutrer.com/howto/dev/python/pipenv-pipfile for basic tutorial
