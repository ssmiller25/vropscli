#!/bin/sh 
#
# Basic script to rename all alerts of a particular type
#
if [[ $# -lt 2 ]]
then
  echo ""
  echo  "Error:    Not enough parameters"
  echo  "Usage:    renamealerts.sh <ADAPTERKIND> <SYNCFILE>"
  echo  "Example:  /renamealerts.sh PALOALTONETWORKS_ADAPTER alertfile.csv"
  echo  "  Note:  The prepended text does NOT include a space automatically"
  echo "" 
  echo  "To get Available ADAPTERKINDs, run ./vropscli getAdapterKinds"
  echo  ""
  exit 1
fi

ADAPTERKIND=$1
SYNCFILE=$2

export COUNT=1
./vropscli getAlertsDefinitionsByAdapterKind ${ADAPTERKIND} | python -m json.tool > oldalert.json
cat oldalert.json | while read line; do 
    if echo $line | grep -q name; then 
	purealertname=$(echo $line | sed 's/\"name\": \"\(.*\)\",/\1/')
	if $(cat ${SYNCFILE} | tr ',' ' ' | grep -q -e "^${purealertname}\$"); then
	     echo "Already renamed ${purealertname}" 1>&2
             echo ${line}
	else
	     echo "Renaming ${purealertname}" 1>&2
             newalertname=$(cat ${SYNCFILE} | grep -e ",${purealertname}\$" | tail -n 1 | tr ',' ' ' )
             if [ -z "$newalertname" ]; then
                echo "WARNING: \"${purealertname}\" does NOT appear in the ${SYNCFILE}.  Perhaps it needs to be added?" 1>&2
             else
                echo \"name\": \"${newalertname}\",
	     fi
	fi
    else
       echo ${line}
    fi
done  > newalert.json
#./vropscli updateAlertDefinitions newalert.json
#rm oldalert.json
#rm newalert.json
