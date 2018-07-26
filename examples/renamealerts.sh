#!/bin/sh
#
# Basic script to rename all alerts of a particular type
export COUNT=1
./vropscli getAlertsDefinitionsByAdapterKind HPE3PAR_ADAPTER | jq . > hpalert.json
cat hpalert.json | while read line; do 
    if echo $line | grep -q name; then 
        COUNTSTR=$(printf "%03d" $COUNT)
        echo ${line} | sed "s/\"name\": \"/\"name\": \"VROPS_HPE_${COUNTSTR} /g"
        COUNT=$(echo $COUNT + 1 | bc )
    else 
        echo ${line}
    fi
done > newhpalertdefs.json
./vropscli updateAlertDefinitions newhpalertdefs.json
