#!/bin/sh
#
# Basic script to rename all alerts of a particular type
#
if [[ $# -lt 2 ]]
then
  echo ""
  echo  "Error:    Not enough parameters"
  echo  "Usage:    renamealerts.sh <ADAPTERKIND> <PREPEND_TEXT>"
  echo  "Example:  /renamealerts.sh PALOALTONETWORKS_ADAPTER VROPS_PA_"
  echo  "  Note:  The prepended text does NOT include a space automatically"
  echo "" 
  echo  "To get Available ADAPTERKINDs, run ./vropscli getAdapterKinds"
  echo  ""
  exit 1
fi

ADAPTERKIND=$1
PREPENDTEXT=$2

export COUNT=1
./vropscli getAlertsDefinitionsByAdapterKind ${ADAPTERKIND} | python -m json.tool > oldalert.json
cat oldalert.json | while read line; do 
    if echo $line | grep -q name; then 
        COUNTSTR=$(printf "%03d" $COUNT)
        echo ${line} | sed "s/\"name\": \"/\"name\": \"VROPS_HPE_${COUNTSTR} /g"
        COUNT=$(echo $COUNT + 1 | bc )
    else 
        echo ${line}
    fi
done > newalert.json
./vropscli updateAlertDefinitions newalert.json
rm oldalert.json
rm newalert.json
