#!/bin/sh
#
# Upgrade MP and sync with alert rename script automatically!
#

if [[ "$#" -lt "2" ]]; then
  echo "Please pass the Pak and adapter kind as paramters"
  exit 1
fi

if [[ -r "$1" ]]; then
  pak_file=$1
else
  echo "$1 is NOT a readable file!"
  exit 1
fi

if [[ ! -z "$2" ]]; then
  if ./vropscli getAdapterKinds | grep -qx "$2"; then
     adapterkind=$2
  else
     echo "$2 does not match a correct adapter kind!"
     exit 1
  fi
else
  echo "$2 is an empty string!!!"
  exit 1
fi

function step_header() {
	echo ""
	echo "================================="
	echo "${1}"
	echo "================================="
	echo ""

}

function exit_error() {
  echo "ERROR: $1"
  exit 1
}

step_header "Startup PAK Upgrade at $(date)"

step_header "Backup Up Alert Definitions"
./vropscli getAlertsDefinitionsByAdapterKind ${adapterkind} > alertbackup.json || exit_error "Alert backup failed"

step_header "Removing Alert Definitions"
./vropscli deleteAlertDefinitions alertbackup.json || exit_error "Alert cleanup failed"

step_header "Upgrading MP"
current_version=$(./vropscli getSolution solution | grep ${adapterkind} | python -m json.tool | grep version | awk ' { print $2; } ' | tr -d \")
echo "Current Version is ${current_version}"
PakID=$(./vropscli uploadPak $pak_file | grep pak_id | awk ' { print $2 } ')
if [[ -z ${PakID} ]]; then
   exit_error "Issue with uploading PAK file"
fi
./vropscli installPak ${PakID} || exit_error "Issue Starting Pak Upgrade"

step_header "Monitoring Upgrade"
while true; do
  date
  ./vropscli getCurrentActivity current_pak_activity
  echo ""
  if ./vropscli getCurrentActivity current_pak_activity | grep pak_id | grep -q null; then
    break
  fi
  sleep 30
done

step_header "Verifing Upgrade"
new_version=$(./vropscli getSolution solution | grep DellPowerEdge | python -m json.tool | grep version | awk ' { print $2; } ' | tr -d \")

if [[ "${current_version}" == "${new_version}" ]]; then
  echo "ERROR: Current version and new version match!  Rolling back alert definitions"
  # Delete and restore alert definitions that might have been created
  ./vropscli getAlertsDefinitionsByAdapterKind ${adapterkind} > alerttodelete.json
  ./vropscli deleteAlertDefinitions alerttodelete.json
  ./vropscli createAlertDefinitions alertbackup.json

  exit_error "Version number after upgrade is the same!  ${current_version}"
fi
step_header "Applying Alert Rename"
./alertsync.sh ${adapterkind} masteralertlist.csv || exit_error "Issue applying alert defintion changes!"
step_header "Upgrade Completed Successfully at $(date)"
exit 0
