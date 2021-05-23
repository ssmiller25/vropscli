# ChangeLog

All notable changes to vROps will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

- Bump py from 1.9 to 1.10 to address CVE-2020-29651
- Bump pyyaml from 5.3 to 5.4 to address CVE-2020-14343

## v1.3.0

features and fixes

* added collector group support to 'getAdapter' and 'createAdapter' https://github.com/BlueMedoraPublic/vropscli/pull/133
* alert definition output is now pretty pretty printed https://github.com/BlueMedoraPublic/vropscli/pull/131
* switch to token authentication to add vrops 8.0 compatibility https://github.com/BlueMedoraPublic/vropscli/pull/127
* added 'setResourceForMaintenance' command https://github.com/BlueMedoraPublic/vropscli/pull/114
* crash when token endpoint returns non 200 status resolved https://github.com/BlueMedoraPublic/vropscli/issues/106
* added ability to create relationships https://github.com/BlueMedoraPublic/vropscli/pull/104

security
* PyYaml CVE-2017-18342 resolved https://github.com/BlueMedoraPublic/vropscli/pull/115

For a full list of changes, see the milestone https://github.com/BlueMedoraPublic/vropscli/issues?q=is%3Aclosed+milestone%3A1.3.0

## v1.2.1

* Updated requests to 2.2.0 to address CVE-2018-18074 #94
* Update instructions for vROps build #62

More details can be found in the Github release page

## v1.2.0
First public release!

* Better error handing, both overall and in specific use cases.
* Credentials can be specified on command line as well as saved to local file.

More details can be found in the Github release page

## v1.1.0

* PR #33: Update some supporting scripts
* PR #31: Allow usage of strings when specifing adapter instances or credential instances.  UUID are still allowed,
          so not considered breaking.
* PR #29: Bug with collector status if resourceStatus is BLANK

## v1.0.1

* Bug #25: Version number not displayed properly

## v1.0.0

* Production release!  Added a few extra credential handing routines

## v0.2.0

* BREAKING CHANGE:  Will now encrypt passwords in the .vropscli.yml file

## v0.1.0

* Initial version
