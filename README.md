# vROpsCLI

A utility to assist in managing a vRealize Operation Manager (vROps) environment through the CLI.  A user can perform MP installs and upgrades, licensing management,
endpoint configuration, credential management, and more!  The design is focused around exposing core functionality that can be scripted to make more complex solutions.

## Usage

* Downloads are available on [the release page](https://github.com/BlueMedoraPublic/vropscli/releases).
* Usage details can be located at [USAGE.md](USAGE.md)
* Examples scripts that use the utilty are located in the [examples directory](https://github.com/BlueMedoraPublic/vropscli/tree/master/examples)
* Blog articles
  * [Introducing vROpsCLI from Blue Medora](https://bluemedora.com/introducing-vropscli-from-blue-medora/)
  * [Blue Medora vROpsCLI Tutorial Part One: Getting Started](https://bluemedora.com/blue-medora-vropscli-tutorial-part-one-getting-started/)

## Development Environment Setup

* Make sure to have Python and Pipenv install
  * For Mac, Install Homebrew (this may take a while if Xcode needs to be installed):

```sh
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

* Run `pipenv --python 3.7` In current directory (or `pipenv --python 3.6 for vROps build directly`)
  * If a local python is not available, you may need to [install pyenv](https://github.com/pyenv/pyenv-installer)
* Run `pipenv lock --pre` and `pipenv sync` to ensure everything is up to date

### To Use

* Run `pipenv shell` to enter environment

### To Distribute

Make sure to compile this on the *oldest* OS you wish to support with your binary!


* Run pylint tests

```sh
pylint --disable=all --enable=F,E,unreachable,duplicate-key,unnecessary-semicolon,global-variable-not-assigned,unused-variable,binary-op-exception,bad-format-string,anomalous-backslash-in-string,bad-open-mode *.py
```

* Run installer locally

```sh
pipenv shell
pipenv install pyinstaller
pyinstaller -F vropscli.py
```

* If you wish to compile to work natively on a vROps system (SLES 11), run the Docker build script:

```sh
./build.sh
```

Binary build will be in a `artifacts` directory

## Notes

* Inspired by [vROps Relay](https://github.com/johnddias/vropsrelay)
* Using Pipenv for package management.  See [this pipenv tutorial](https://jcutrer.com/howto/dev/python/pipenv-pipfile) for basic tutorial
