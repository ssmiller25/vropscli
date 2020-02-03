#!/bin/sh

#
#  A linux shell version of backupvrsopconfig.ps1 from John Xu
#


currenttime=$(date +%Y-%d-%m-%H-%m)

if [ -r $HOME/.vropscli.yml ]; then
    echo "Using ${HOME}/.vropscli.yml for credentials"
else
    vropsuser = "admin"
    while vropspassword = ""; do
        echo -n "Enter an admin password: "
        read -s vropspassword
    done
    echo -n "Type in vrops host: "
    read vropshost
    authinfo = "--user ${vropsuser} --password ${vropspassword} --host ${vropshost} "
fi

components="getVropsLicense getCurrentActivity getAllCredentials getSolution getAdapters getAdapterKinds"
for component in ${components}; do 
    echo "Writing ${component} backup"
    ./vropscli $component $authinfo > $component"_"$currenttime.csv
done
# Get licesnes for individual solutions
cat getSolution_$currenttime.csv | grep -v id | while read line; do
    solution=$(echo ${line} | cut -f1 -d,)
    echo "Solution License for ${solution}"

    solutionlicense=$(./vropscli getSolutionLicense ${solution} 2>/dev/null)
    echo "$solution,$solutionlicense" >> getSolutionLicense_$currenttime.csv
done


echo "Backup complete"

