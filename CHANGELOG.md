# ChangeLog

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
