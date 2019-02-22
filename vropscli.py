#!/usr/bin/env python3

# vropscli: Tool for interacting with vROps API from the command line
# Copyright (c) 2018 Blue Medora LLC
# This work is licensed under the terms of the MIT license.  
#  For a copy, see <https://opensource.org/licenses/MIT>. 

import vropsclilib as clilib
import requests
import json
import pprint
import fire
import csv
import sys
import os
import time
import yaml 
import traceback
#from urllib3.exceptions import HTTPError
from pathlib import Path


VERSION="1.2.2"

class vropscli:

    def getResource(self, resource):
        url = "https://" + self.config['host'] + "/suite-api/api/resources/" + resource

        headers = {
            'authorization': "vRealizeOpsToken " + self.token['token'],
            'accept': "application/json",
            }

        response = requests.request("GET", url, headers=headers, verify=False)
        response_parsed = json.loads(response.text)
        return response_parsed

    def getAdapter(self, adapterId):
        url = "https://" + self.config['host'] + "/suite-api/api/adapters/" + adapterId

        response = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)
        if response.status_code < 300:
            response_parsed = json.loads(response.text)
            return response_parsed
        else:
            # Search didn't work, try to do search across all adapters
            urlall = "https://" + self.config['host'] + "/suite-api/api/adapters"
            r = requests.request("GET", urlall, headers=clilib.get_token_header(self.token['token']), verify=False)
            r_parsed = json.loads(r.text)
            for instance in r_parsed["adapterInstancesInfoDto"]:
                if adapterId in instance["resourceKey"]["name"]:
                    return instance
            # if we get to this point, exit entire script...nothing found
            print("No adapter found for " + adapterId)
            r.raise_for_status()

    def getAdapters(self):
        url = "https://" + self.config['host'] + "/suite-api/api/adapters"

        response = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)
        response_parsed = json.loads(response.text)
        print("id,Name,Type")
        for instance in response_parsed["adapterInstancesInfoDto"]:
            print(instance["id"] + "," + instance["resourceKey"]["name"] + "," + instance["resourceKey"]["adapterKindKey"])

    def getCollectors(self):
        '''->

        Return all collectors, including their ID

        '''
        url = "https://" + self.config['host'] + "/suite-api/api/collectors"

        response = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)
        response_parsed = json.loads(response.text)
        print("id,Name,State")
        for instance in response_parsed["collector"]:
            print(instance["id"] + "," + instance["name"] + "," + instance["state"])

    def getAdapterKinds(self):
        url = "https://" + self.config['host'] + "/suite-api/api/adapterkinds"
        headers = {
            'authorization': "vRealizeOpsToken " + self.token['token'],
            'accept': "application/json",
            }
        response = requests.request("GET", url, headers=headers, verify=False)
        response_parsed = json.loads(response.text)
        adapterkindacc = []
        for adapter in response_parsed["adapter-kind"]:
          adapterkindacc.append(adapter["key"])
        return adapterkindacc

    def getAdapterKindConfigParams(self, adapterKind):
        url = "https://" + self.config['host'] + "/suite-api/api/adapterkinds/" + adapterKind + '/resourcekinds/'
        response = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)
        response_parsed = json.loads(response.text)
        key = ""
        for resource in response_parsed["resource-kind"]:
            if "ADAPTER_INSTANCE" in resource["resourceKindType"]:
                key=resource["key"]
        if key == "":
            print("No key found for " + adapterKind)
        rsurl = "https://" + self.config['host'] + "/suite-api/api/adapterkinds/" + adapterKind + '/resourcekinds/' + key
        rsresponse = requests.request("GET", rsurl, headers=clilib.get_token_header(self.token['token']), verify=False)
        return(json.loads(rsresponse.text)['resourceIdentifierTypes'])

    def getAdapterConfig(self, adapterId):
        '''->
        
        Return a CSV configuration for a single adapter

        ADAPTERID:  Id of solution or string search for the adapter name.  Id can be found from getAdapters action

        '''
        adapterInfo = self.getAdapter(adapterId)
        settingsinfo = {}
        for setting in adapterInfo["resourceKey"]["resourceIdentifiers"]:
            settingsinfo[setting["identifierType"]["name"]]=setting["value"]
        csvheader = []
        csvrow = {}
        csvheader = ["adapterkey","adapterKind","resourceKind","credentialId","collectorId","name","description"]
        csvrow["adapterkey"]=adapterInfo["id"]
        csvrow["adapterKind"]=adapterInfo["resourceKey"]["adapterKindKey"]
        csvrow["resourceKind"]=adapterInfo["resourceKey"]["resourceKindKey"]
        csvrow["credentialId"]=adapterInfo["credentialInstanceId"]
        csvrow["collectorId"]=adapterInfo["collectorId"]
        csvrow["name"]=adapterInfo["resourceKey"]["name"]
        csvrow["description"]=adapterInfo["description"]

        for configparam in adapterInfo["resourceKey"]["resourceIdentifiers"]:
            csvheader.append(configparam["identifierType"]["name"])
            csvrow[configparam["identifierType"]["name"]]=configparam["value"]
        csvwr = csv.DictWriter(sys.stdout, fieldnames=csvheader, quoting=csv.QUOTE_ALL)
        csvwr.writeheader()
        csvwr.writerow(csvrow)


    def getAdapterConfigs(self, adapterKindKey):
        '''->

        Return a CSV configuration for all adapters of the same adapter kind

        ADAPTERKINDKEY: The adatper kind key, which can get listed by calling getAdapterKinds

        '''
        url = "https://" + self.config['host'] + "/suite-api/api/adapters/?adapterKindKey=" + adapterKindKey
        response = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)

        csvheader = ["adapterkey","adapterKind","resourceKind","credentialId","collectorId","name","description"]

        settingsinfo = {}
        firstRun = 'true'
        response_parsed = json.loads(response.text)

        for adapterInfo in response_parsed["adapterInstancesInfoDto"]:
            csvrow = {}
            csvrow["adapterkey"]=adapterInfo["id"]
            csvrow["adapterKind"]=adapterInfo["resourceKey"]["adapterKindKey"]
            csvrow["resourceKind"]=adapterInfo["resourceKey"]["resourceKindKey"]
            csvrow["credentialId"]=adapterInfo["credentialInstanceId"]
            csvrow["collectorId"]=adapterInfo["collectorId"]
            csvrow["name"]=adapterInfo["resourceKey"]["name"]
            csvrow["description"]=adapterInfo["description"]

            for configparam in adapterInfo["resourceKey"]["resourceIdentifiers"]:
                if (firstRun == 'true'):
                    csvheader.append(configparam["identifierType"]["name"])
                csvrow[configparam["identifierType"]["name"]]=configparam["value"]
            if (firstRun == 'true'):
                csvwr = csv.DictWriter(sys.stdout, fieldnames=csvheader, quoting=csv.QUOTE_ALL)
                csvwr.writeheader()
            csvwr.writerow(csvrow)
            firstRun = 'false'

    def getAlertsDefinitionsByAdapterKind(self, adapterKindKey):
        '''->

        Produce the JSON definition of all alert definition for a particular adapter kind

        ADAPTERKINDKEY: Adapter kind, which can be found by calling getAdapterKinds
        

        '''
        url = "https://" + self.config['host'] + "/suite-api/api/alertdefinitions?adapterKind=" + adapterKindKey

        response = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)
        response_parsed = json.loads(response.text)
        print("{\"alertDefinitions\": " + json.dumps(response_parsed["alertDefinitions"]) + "}")

    def updateAlertDefinitions(self, alertConfigFile):
        '''->

        Update alert defintions from a file producted by the getAlertsDefinitionsByAdapterKind routine

        ALERTCONFIGFILE:  JSON file of alerts to update

        '''

        with open(alertConfigFile) as jsonFile:
            alertDefinitions = json.load(jsonFile)

        url = 'https://' + self.config['host'] + '/suite-api/api/alertdefinitions'
        for alertDefinition in alertDefinitions["alertDefinitions"]:
            r = requests.put(url, data=json.dumps(alertDefinition), headers=clilib.get_token_header(self.token['token']), verify=False)

            if r.status_code < 300:
                print(alertDefinition["name"] + ' updated successfully.')
            else:
                # Print error, but continue processing
                print(alertDefinition["name"] + ' updated failed!.')
                print(r.text())


    def generateAlertTemplate(self):
        newAlertData= {"alertDefinitions":[
                {
                  "adapterKindKey": "",
                  "cancelCycles": 1,
                  "description": "",
                  "name": "",
                  "resourceKindKey": "",
                  "states": [
                    {
                      "base-symptom-set": {
                        "aggregation": "ANY",
                        "relation": "SELF",
                        "symptomDefinitionIds": [
                          ""
                        ],
                        "symptomSetOperator": "AND",
                        "type": "SYMPTOM_SET"
                      },
                      "impact": {
                        "detail": "health",
                        "impactType": "BADGE"
                      },
                      "severity": ""
                    }
                  ],
                  "subType": 18,
                  "type": 19,
                  "waitCycles": 1
                }]
        }
        print(json.dumps(newAlertData))

    def createAlertDefinitions(self, alertConfigFile):
        '''->

        Create alert defintions from a file producted by the getAlertsDefinitionsByAdapterKind routine

        ALERTCONFIGFILE:  JSON file of alerts to create

        '''

        with open(alertConfigFile) as jsonFile:
            alertDefinitions = json.load(jsonFile)

        for alertDefinition in alertDefinitions["alertDefinitions"]:
            # Must make sure "id" does not exist for newly created alerts
            if 'id' in alertDefinition:
                del alertDefinition['id']
            self.createAlertDefinition(alertJSON=alertDefinition)

    def createAlertDefinition(self, alertJSON):
        url = 'https://' + self.config['host'] + '/suite-api/api/alertdefinitions'
        r = requests.post(url,  data=json.dumps(alertJSON), headers=clilib.get_token_header(self.token['token']), verify=False)
        if r.status_code == 201:
            print(alertJSON["name"] + ' alert successfully created.')
            print("Return Code: " + str(r.status_code))
        else:
            print(alertJSON["name"] + ' creation failed!')
            print(str(r.status_code))
            print(r.text)

    def deleteAlertDefinitions(self, alertConfigFile):
        '''->

        Delete alert defintions from a file producted by the getAlertsDefinitionsByAdapterKind routine

        ALERTCONFIGFILE:  JSON file of alerts to delete

        '''

        with open(alertConfigFile) as jsonFile:
            alertDefinitions = json.load(jsonFile)

        for alertDefinition in alertDefinitions["alertDefinitions"]:
            self.deleteAlertDefinition(alertDefinitionKey=alertDefinition['id'])

    def deleteAlertDefinition(self, alertDefinitionKey):
        url = 'https://' + self.config['host'] + '/suite-api/api/alertdefinitions/' + alertDefinitionKey
        r = requests.delete(url, headers=clilib.get_token_header(self.token['token']), verify=False)
        if r.status_code < 300:
            print(alertDefinitionKey + ' alert successfully deleted.')
        else:
            r.raise_for_status()

    def createAdapterInstances(self, resourceConfigFile, autostart=False):
        '''->

        Create adapter instances with a CSV file generated by getAdapterConfig or getAdapterConfigs

        RESOURCECONFIGFILE: The CSV file with the new adapter configurations
        AUTOSTART:  If the adapters should be started after creation.  Defaults to false.


        '''
        resourceConfigData = open(resourceConfigFile, newline='')
        resourceConfig = csv.DictReader(resourceConfigData)

        for row in resourceConfig:
            # Suite-API specifically expects a list of dictionary objects, with only two ides of "name" and "value".  Not even asking why...
            resourceConfigItems = []

            for name, value in row.items():
                if (name == 'name') or (name == 'description') or (name == 'resourceKind') or (name == 'adapterKind') or (name == 'adapterkey') or (name == 'credentialId') or (name == 'collectorId'):
                    continue
                resourceConfigItems.append({"name" : name, 'value':value})

            newadapterdata= {
                "name": row['name'],
                "description": row['description'],
                "collectorId": row['collectorId'],
                "adapterKindKey": row['adapterKind'],
                "resourceIdentifiers": resourceConfigItems,
                "credential": {
                    "id": row['credentialId']
                }
            }
            url = 'https://' + self.config['host'] + '/suite-api/api/adapters'
            r = requests.post(url, data=json.dumps(newadapterdata), headers=clilib.get_token_header(self.token['token']), verify=False)
            if r.status_code < 300:
                print(row['name'] + ' Adapter Successfully Installed')
                if autostart == True:
                    returndata=json.loads(r.text)
                    self.startAdapterInstance(adapterId=returndata["id"])
            else:
                try:
                    r.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    error_data = json.loads(e.response.text)
                    if "Resource with same key already exists" in error_data["moreInformation"][1]["value"]:
                        print("Adatper Instance " + row['name'] + "already exists, or shares resources marked unique with another adapter")
                    else:
                        raise
                    


    def deleteAdapterInstances(self, resourceConfigFile):

        resourceConfigData = open(resourceConfigFile, newline='')
        resourceConfig = csv.DictReader(resourceConfigData)

        for row in resourceConfig:
            self.deleteAdapterInstance(adapterkey=row['adapterkey'])


    def deleteAdapterInstance(self, adapterkey):
        # Use adapter search
        adapter = self.getAdapter(adapterkey)
        url = 'https://' + self.config['host'] + '/suite-api/api/adapters/' + adapter["id"]
        r = requests.delete(url, headers=clilib.get_token_header(self.token['token']), verify=False)
        if r.status_code < 300:
            print(adapterkey + ' adapter successfully deleted.')
        else:
            r.raise_for_status()


    def updateAdapterInstances(self, resourceConfigFile, autostart=False):
        '''->

        Update adapter instances with a CSV file generated by getAdapterConfig or getAdapterConfigs

        RESOURCECONFIGFILE: The CSV file with the new adapter configurations
        AUTOSTART:  If the adapters should be started after update.  Defaults to false.

        '''
        resourceConfigData = open(resourceConfigFile, newline='')
        resourceConfig = csv.DictReader(resourceConfigData)

        for row in resourceConfig:
            resourceConfigItems = []

            for name, value in row.items():
                if (name == 'name') or (name == 'description') or (name == 'resourceKind') or (name == 'adapterKind') or (name == 'adapterkey') or (name == 'credentialId') or (name == 'collectorId'):
                    continue
                resourceConfigItems.append({  "identifierType":{ "name" : name,"dataType" : "STRING"}, 'value':value})

            newadapterdata= {
                "resourceKey": {
                    "name": row['name'],
                    "resourceKindKey": row['resourceKind'],
                    "adapterKindKey": row['adapterKind'],
                    "resourceIdentifiers": resourceConfigItems},
                "id": row['adapterkey'],
                "credentialInstanceId": row['credentialId'],
                "description": row['description'],
                "collectorId": row['collectorId']
            }

            url = 'https://' + self.config['host'] + '/suite-api/api/adapters'
            r = requests.put(url, data=json.dumps(newadapterdata), headers=clilib.get_token_header(self.token['token']), verify=False)
            if r.status_code < 300:
                print(row['name'] + ' Adapter Successfully Updated - ' + str(r.status_code))
                if autostart == True:
                    returndata=json.loads(r.text)
                    self.startAdapterInstance(adapterId=returndata["id"])
            else:
                #Not Raising excpetion as we want to continue processing the file
                print(row['name'] + ' Failed!')
                print(str(r.status_code))
                print(r.text)



    def getResourcesOfAdapterKind(self, adapterkey):
        url = "https://" + self.config['host'] + "/suite-api/api/adapterkinds/" + adapterkey + '/resources'
        headers = {
            'authorization': "vRealizeOpsToken " + self.token['token'],
            'accept': "application/json",
            }
        response = requests.request("GET", url, headers=headers, verify=False)
        response_parsed = json.loads(response.text)
        resourceout = []
        for adapter in response_parsed["resourceList"]:
          resourceout.append(adapter["identifier"])
        return resourceout

    def setSolutionLicense(self, solutionId, license):
        '''->
        
        Set solution license

        SOLUTIONID: Id of solution or string search for Solution type.  Id can be found from getSolution action
        LICENSE: License string for the solution

        '''
        data = {
            'solutionLicenses' : [ {
                'licenseKey': license,
            } ]
        }
        url = 'https://' + self.config['host'] + '/suite-api/api/solutions/' + solutionId + '/licenses'
        r = requests.post(url, data=json.dumps(data), headers=clilib.get_token_header(self.token['token']), verify=False)
        if r.status_code < 300:
            print('license key installed')
            return True
        else:
            print('Failed to install license for ' + solutionId)
            print(str(r.status_code))
            return False

    def getAllCredentials(self):
        '''->
       
        Return all credentials defined in the vROps system

        '''
        url = "https://" + self.config['host'] + "/suite-api/api/credentials"

        response = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)
        credssum = {}
        response_parsed = json.loads(response.text)

        csvheader=[]
        csvrows=[]
        csvheader = ["id","name","adapterKind"]

        for credentialInstances in response_parsed['credentialInstances']:
            arow = {}
            arow["id"]=credentialInstances["id"]
            arow["name"]=credentialInstances["name"]
            arow["adapterKind"]=credentialInstances["adapterKindKey"]
            csvrows.append(arow)
        csvwr = csv.DictWriter(sys.stdout, fieldnames=csvheader, quoting=csv.QUOTE_ALL)
        csvwr.writeheader()
        for row in csvrows:
            csvwr.writerow(row)


    def getCredential(self, credentialId):
        '''->
       
        Return an individual credential for vROps adapters, in CSV format.

        CREDENTIALID: The ID of the credential, or a string of the credential name

        '''
        url = "https://" + self.config['host'] + "/suite-api/api/credentials/" + credentialId
        headers = {
            'authorization': "vRealizeOpsToken " + self.token['token'],
            'accept': "application/json",
            }
        response = requests.request("GET", url, headers=headers, verify=False)
        if response.status_code < 300:
            r_parsed = json.loads(response.text)
        else:
            # Search didn't work, try to do search across all adapters
            urlall = "https://" + self.config['host'] + "/suite-api/api/credentials"
            r = requests.request("GET", urlall, headers=clilib.get_token_header(self.token['token']), verify=False)
            rall_parsed = json.loads(r.text)
            found = False
            for instance in rall_parsed["credentialInstances"]:
                if credentialId in instance["name"]:
                    r_parsed = instance
                    found = True
            # if we get to this point, exit entire script...nothing found
            if found == False:
                print("No credential found for " + credentialId)
                sys.exit(1)
        csvheader = []
        csvrow = {}
        csvheader = ["name","adapterKindKey","credentialKindKey"]
        csvrow["name"]=r_parsed["name"]
        csvrow["adapterKindKey"]=r_parsed["adapterKindKey"]
        csvrow["credentialKindKey"]=r_parsed["credentialKindKey"]

        for credfield in r_parsed["fields"]:
            csvheader.append(credfield["name"])
            if "value" in credfield:
                csvrow[credfield["name"]]=credfield["value"]
        csvwr=csv.DictWriter(sys.stdout, fieldnames=csvheader, quoting=csv.QUOTE_ALL)
        csvwr.writeheader()
        csvwr.writerow(csvrow)

    def createCredentials(self, credConfigFile):
        '''->

        Creates credentials based on a CSV file generated by the createCredential Routine

        CREDCONFIGFILE: Credentail CSV file (with passwords added by user)

        '''
        credConfigData = open(credConfigFile, newline='')
        credConfig = csv.DictReader(credConfigData)

        for row in credConfig:
            # Suite-API specifically expects a list of dictionary objects, with only two ides of "name" and "value".  Not even asking why...
            credConfigItems = []

            for name, value in row.items():
                if (name == 'name') or (name == 'adapterKindKey') or (name == 'credentialKindKey'):
                    continue
                credConfigItems.append({"name" : name, 'value':value})

            newcreddata= {
                "name": row['name'],
                "adapterKindKey": row['adapterKindKey'],
                "credentialKindKey": row['credentialKindKey'],
                "fields": credConfigItems,
            }
            url = 'https://' + self.config['host'] + '/suite-api/api/credentials'
            r = requests.post(url, data=json.dumps(newcreddata), headers=clilib.get_token_header(self.token['token']), verify=False)
            if r.status_code < 300:
                returndata  = json.loads(r.text)
                print(row['name'] + ' Credentail Successfully Created with ID ' + returndata["id"])
            else:
                # Not raising exception as we want to process the entire file, if possible
                print(row['name'] + ' Failed!')
                print(str(r.status_code))
                print(r.text)

    def deleteCredential(self, credentialId):
        '''->

        Delete an individual credential

        CREDENTIALID: The ID of the specific credential to delete.  This can get obtained from the getAllCredentials function.

        '''
        url = "https://" + self.config['host'] + "/suite-api/api/credentials/" + credentialId
        headers = {
            'authorization': "vRealizeOpsToken " + self.token['token'],
            'accept': "application/json",
            }
        r = requests.request("DELETE", url, headers=headers, verify=False)
        if r.status_code < 300:
            print(credentialId + " successfully deleted!")
        else:
            r.raise_for_status()

    def getSolutionLicense(self, solutionId):
        '''->

        Get available solution license (for user installed Paks)

        SOLUTIONID: Id of solution or string search for Solution type.  Id can be found from getSolution action

        '''
        url = 'https://' + self.config['host'] + '/suite-api/api/solutions/' + solutionId + '/licenses'
        r = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)
        return json.loads(r.text)

    def getSolution(self):
        '''->
        Get all solutions installed
        '''
        url = 'https://' + self.config['host'] + '/suite-api/api/solutions'
        r = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)
        print("id,name,version,adapterKind")
        for solution in json.loads(r.text)["solution"]:
            # Resolve issues specific with BLue Medora ITM Adapter
            if "name" in solution:
                print(solution["id"] + "," + solution["name"] + "," + str(solution["version"])  + "," + solution["adapterKindKeys"][0])
            else:
                print(solution["id"] + ",,," + solution["adapterKindKeys"][0])

    def getVropsLicense(self):
        '''->
        Get installed VROps license
        '''
        url = 'https://' + self.config['host'] + '/suite-api/api/deployment/licenses'
        r = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)
        return json.loads(r.text)


    def setVropsLicense(self, license_key):
        '''->

        Set the license key for vROps itself

        LICENSE_KEY: The liense key for vROps

        '''
        url = 'https://' + self.config['host'] + '/suite-api/api/deployment/licenses'
        data = {
            'solutionLicenses' : [ {
                'id' : None,
                'licenseKey': license_key,
                'others' : [ ],
                'otherAttributes' : {
                }
            } ]
        }

        r = requests.post(url, data=json.dumps(data), headers=clilib.get_token_header(self.token['token']), verify=False)
        if r.status_code == 200:
            print('license key installed')
            return True
        else:
            print('Failed to license vrops')
            print(str(r.status_code))
            return False

    def uploadPak(self, pakFile, overwritePak=True):
        '''->

        Upload a Pak file to the server.  After this is run, you will need to execute the installPak routine.

        PAKFILE: File of PAK update
        OVERWRITEPAK:  Overwrite existing pak. Default is true

        '''
        if overwritePak == True:
            pak_handling_advice = 'CLOBBER'
        else:
            pak_handling_advice = 'STANDARD'
        url = 'https://' + self.config['host'] + '/casa/upgrade/cluster/pak/reserved/operation/upload'
        files = { 'contents': open(pakFile, 'rb') }
        data = { 'pak_handling_advice': pak_handling_advice }
        print("Started Pak Upload: " + str(pakFile) + ".  This may take up to 20 minutes depending on network speed.")
        r = requests.post(url, data=data, files=files, auth=requests.auth.HTTPBasicAuth(self.config["user"],self.config["pass"]), verify=False)
        if r.status_code < 300:
            print('Upload Successful!')
            return json.loads(r.text)
        else:
            try:
                error_data = json.loads(r.text)
                print(r.text)
            except:
                print('Failed to Install Pak')
                r.raise_for_status()

            if "upgrade.pak.history_present" in error_data["error_message_key"]:
                print('Failed to Install Pak')
                print('Pak was already uploaded, but probably not installed')
                print('Please finish the pak installation by calling vropscli installPak')
                return None
            elif "upgrade.pak.upload_version_older_or_same" in error_data["error_message_key"]: 
                print('Failed to Install Pak')
                print('Pak was already installed at the same or newer version')
                print('If you wish to upgrade, please pass along --overwritePak to this function')
                return None
            else:
                r.raise_for_status()

    def getPakInfo(self, pakID):
        '''->

        Get Pak information.

        PAKID: The pak id, produced when uploadPak is executed.

        '''
        url = 'https://' + self.config['host'] + '/casa/upgrade/cluster/pak/' + pakID + '/information'
        r = requests.get(url, auth=requests.auth.HTTPBasicAuth(self.config["user"],self.config["pass"]), verify=False)
        if r.status_code < 300:
            return json.loads(r.text)
            return True
        else:
            r.raise_for_status()

    def installPak(self, pakId, force_content_update=True):
        '''->

        Install an uploaded Pak File.  

        PAKID:  The ID of the pak file, produced when uploadPak is executed.
        FORCE_CONTENT_UPDATE:  Will overwrite included dashboards, reports, and alert definitions.  Default is true

        '''
        install_data = {}
        if force_content_update == True:
            install_data['force_content_update'] = True 
        else:
            install_data['force_content_update'] = False 
        url = 'https://' + self.config['host'] + '/casa/upgrade/cluster/pak/' + pakId + '/operation/install' 
        r = requests.post(url, headers=clilib.get_headers_plain(), data=json.dumps(install_data), auth=requests.auth.HTTPBasicAuth(self.config["user"],self.config["pass"]), verify=False)
        if r.status_code < 300:
            print('Pak installation started.  Run "vropscli getCurrentActivity" to get current status')
            return True
        else:
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                error_data = json.loads(e.response.text)
                if "Could not find file for PAK ID" in error_data["error_arguments"][0]:
                    print("No file was found for PAK ID " + pakId)
                    print("Please verify the Pak ID that was produced after the uploadPak command (this will be different then the actual filename)")
                else:
                    raise


    def groupInstall(self, pakDir, overwritePak=False, force_content_update=True, verbose=False):
        '''->

        Install all pak files found in a directory
        
        PAKDIR: The full path to the directory that contains the PAK files
        OVERWRITEPAK: Overwrite existing packs, default to false.
        FORCE_CONTENT_UPDATE: Will overwrite included build-in dashboards, reports, and alert definitions.  Default is true.
        VERBOSE: Details output, default to false.

        '''
        # Get list of paks
        paks = []
        for (dirpath, dirnames, filenames) in os.walk(pakDir):
            paks.extend(filenames)
        # Upload and install each pak
        for pak in paks:
            full_path = pakDir + "/" + pak
            r = self.uploadPak(full_path, overwritePak)
            if r != None:
                print(r)
                self.installPak(r["pak_id"], force_content_update)
                while True:
                    status = self.getCurrentActivity()
                    if verbose == True:
                        print(status)
                    if status["current_pak_activity"]["pak_id"] != None:
                        print("Waiting for install to complete. . . ")
                        time.sleep(30)
                    else:
                        print("Pak installed")
                        break
        print("Finished group install")

    def getPakStatus(self, pakID):
        '''->

        Get Pak Installation Status 

        PAKID:  The ID of the pak file, produced when uploadPak is executed.

        '''
        url = 'https://' + self.config['host'] + '/casa/upgrade/cluster/pak/' + pakID + '/status'
        r = requests.get(url, auth=requests.auth.HTTPBasicAuth(self.config["user"],self.config["pass"]), verify=False)
        if r.status_code < 300:
            return json.loads(r.text)
            return True
        else:
            print('Failed to Get Pak Info')
            r.raise_for_status()

    def getCurrentActivity(self):
        '''->

        Get current activity of vROps, including details of the Pak installation process

        '''
        url = 'https://' + self.config['host'] + '/casa/upgrade/cluster/pak/reserved/current_activity'
        r = requests.get(url, auth=requests.auth.HTTPBasicAuth(self.config["user"],self.config["pass"]), verify=False)
        if r.status_code < 300:
            return json.loads(r.text)
            return True
        else:
            r.raise_for_status()

    def getAdapterCollectionStatus(self, adapterId):
        '''->

        Get Current adater collection status

        ADAPTERID:  Id of solution or string search for the adapter name.  Id can be found from getAdapters action

        '''
        # Use adapter search
        adapter = self.getAdapter(adapterId)
        #set the url for the adapter instance
        url = 'https://' + self.config['host'] + '/suite-api/api/resources/' + adapter["id"]
        # Grab the specific adapter "resource"
        resources = requests.get(url, headers=clilib.get_token_header(self.token['token']), verify=False)
        #filter down to the collection status
        #Currently grabs everything within the resourceStatusStates and needs to be filtered down to just resourceStatus
        #If the object is down let the user know
        resourceState = (json.loads(resources.text)["resourceStatusStates"][0]["resourceState"])

        #There is the option for it to be UNKNOWN and it isn't accounted for
        if resourceState == "NOT_EXISTING" or resourceState == "STOPPED":
            print("The adapter is powered off")
            sys.exit(1)
        elif resourceState == "STARTED":
            if "resourceStatus" not in json.loads(resources.text)["resourceStatusStates"][0]:
                print("The adapter is on, but Status is BLANK")
                sys.exit(1)
            else:
                resourceStatus = (json.loads(resources.text)["resourceStatusStates"][0]["resourceStatus"])
                #if the resourceStatus is DATA_RECEIVING let the user know they are collecting data
                if resourceStatus == "DATA_RECEIVING":
                    print("The adapter is on and collecting successfully")
                    sys.exit(0)
                elif resourceStatus == "NO_PARENT_MONITORING":
                    print("The adapter is powered off")
                    sys.exit(1)
                else:
                    print("The adapter in on, but not collecting.  Status is " + resourceStatus)
                    sys.exit(1)
        else:
            print("Unknown adapter state: " + resourceState)
            sys.exit(1)

    def stopAdapterInstance(self, adapterId):
        '''->

        Stop an adapter instance

        ADAPTERID:  Id of solution or string search for the adapter name.  Id can be found from getAdapter action

        '''
        # Use adapter search
        adapter = self.getAdapter(adapterId)
        #set the url for the adapter instance
        url = 'https://' + self.config['host'] + '/suite-api/api/adapters/' + adapter["id"] + '/monitoringstate/stop'
        #A put request to turn off the adapter
        r = requests.put(url, auth=requests.auth.HTTPBasicAuth(self.config['user'], self.config['pass']), verify=False)
        print("Adapter Stopped")

    def startAdapterInstance(self, adapterId):
        '''->

        Start an adapter instance

        ADAPTERID:  Id of solution or string search for the adapter name.  Id can be found from getAdapter action

        '''
        # Use adapter search
        adapter = self.getAdapter(adapterId)
        #set the url for the adapter instance
        url = 'https://' + self.config['host'] + '/suite-api/api/adapters/' + adapter["id"] + '/monitoringstate/start'
        #A put request to turn on the adapter
        r = requests.put(url, auth=requests.auth.HTTPBasicAuth(self.config['user'], self.config['pass']), verify=False)
        print("Adapter Started")

    def createRelationshipsById(self, relationshipsFile):
        '''->

        Create resource relationships from a file

        RELATIONSHIPSFILE:  CSV file of alerts to create. The columns are:
         * Parent UUID
         * Child UUID

         Do not include a header row.

        '''

        with open(relationshipsFile) as relationshipsCsv:
            # The csv#DictReader iterates through the file as we process it, so the file needs to be left open
            relationshipsData = csv.DictReader(relationshipsCsv, ['parent', 'child'])

            successCount = 0

            for relationshipRow in relationshipsData:
                childUuids = [relationshipRow['child']] # TODO: Batch requests for relationships having the same parent for better performance
                (success, r) = clilib.create_relationships_by_ids(self.token['token'], self.config['host'], relationshipRow['parent'], childUuids)

                if (not success):
                    print(f"Failed to create {relationshipRow['parent']} -> {relationshipRow['child']} relationship.")
                    print(f"API Response Status Code: {r.status_code}")
                    print(f"API Response Text: {r.text}")
                    print()
                else:
                    successCount += 1

            if (successCount > 0):
                print(f"{successCount} relationships successfully created.")
            else:
                print('No relationships created.')

    def createRelationshipsByName(self, relationshipsFile, matchMode = "first"):
        '''->

        Create resource relationships from a file

        RELATIONSHIPSFILE:  CSV file of alerts to create. The columns are: 
          * Parent Adapter Type ("VMWARE" for example, for vCenter adapters -- Use the getAdapters verb to list adapter types in your environment)
          * Parent Object Type ("VirtualMachine" for example, for VM's)
          * Parent Object Name
          * Child Adapter Type
          * Child Object Type
          * Child Object Name

          Do not include a header row.

          Example row:
          VMWARE,VirtualMachine,agent-builder,VMWARE,VirtualMachine,3par-vsp

        MATCHMODE: One of...
          * first (default) - Make a relationship to the first object, even if there are multiple objects with that name
          * all - Make relationships to every object found with that name
          * skip - Skip (and log) whenever more than one object is found with that name

          To match an object exactly, the createRelationshipsById verb can be used.
          The matchmode is case-insensitive.

        '''
        lMatchMode = matchMode.lower()
        if (lMatchMode not in ["first", "all", "skip"]):
            print(f"Unknown matchMode <{matchMode}>. 'first', 'all', or 'skip' expected.")
            return

        with open(relationshipsFile) as relationshipsCsv:
            # The csv#DictReader iterates through the file as we process it, so the file needs to be left open
            relationshipsData = csv.DictReader(relationshipsCsv, ['parent-adapter', 'parent-type', 'parent-name', 'child-adapter', 'child-type', 'child-name'])

            successCount = 0

            for relationshipRow in relationshipsData:
                (parentUUIDs, _) = clilib.lookup_object_id_by_name(self.token['token'], self.config['host'], relationshipRow['parent-adapter'], relationshipRow['parent-type'], relationshipRow['parent-name'])
                (childUUIDs, _) = clilib.lookup_object_id_by_name(self.token['token'], self.config['host'], relationshipRow['child-adapter'], relationshipRow['child-type'], relationshipRow['child-name'])
                # Ignoring the partial flag, since there's no reason we should return 100,000+ objects

                if (len(parentUUIDs) == 0):
                    print(f"No object found for {relationshipRow['parent-adapter']},{relationshipRow['parent-type']},{relationshipRow['parent-name']}. Skipping this relationship.")
                    continue
                if (len(childUUIDs) == 0):
                    print(f"No object found for {relationshipRow['child-adapter']},{relationshipRow['child-type']},{relationshipRow['child-name']}. Skipping this relationship.")
                    continue

                if (lMatchMode == "skip"):
                    if (len(parentUUIDs) != 1):
                        print(f"Expected to find only one object for {relationshipRow['parent-adapter']},{relationshipRow['parent-type']},{relationshipRow['parent-name']}. {len(parentUUIDs)} found instead. Skipping this relationship.")
                        continue
                    if (len(childUUIDs) != 1):
                        print(f"Expected to find only one object for {relationshipRow['child-adapter']},{relationshipRow['child-type']},{relationshipRow['child-name']}. {len(childUUIDs)} found instead. Skipping this relationship.")
                        continue

                if (lMatchMode == "first"):
                    parentUUIDs = [parentUUIDs[0]]
                    childUUIDs = [childUUIDs[0]]

                for parentUUID in parentUUIDs:
                    (success, r) = clilib.create_relationships_by_ids(self.token['token'], self.config['host'], parentUUID, childUUIDs)

                    if (not success):
                        print(f"Failed to create {parentUUID} -> {childUUIDs} relationship.")
                        print(f"API Response Status Code: {r.status_code}")
                        print(f"API Response Text: {r.text}")
                        print()
                    else:
                        successCount += len(childUUIDs)
            
            if (successCount > 0):
                print(f"{successCount} relationships successfully created.")
            else:
                print('No relationships created.')

    def saveCliCred(self):
        '''->

        Save Credentials to a local file, $HOME/.vropscli.yml
        WARNING: This file should be protected with OS level permission.  ANYONE with this file will have credentials to 
        your vROps system!!!

        Make sure to pass:
        --user <username>
        --password <password>
        --host <vropshost>

        '''
        fullconfig={
            'default':{
                'user':self.config['user'],
                'passencrypt':clilib.vig(self.config['pass'],clilib.ENCODE,'e'),
                'host':self.config['host']
            }
        }
        configfile=os.path.join(str(Path.home()), ".vropscli.yml")
        with open(os.path.expanduser(configfile),"w") as c:
            yaml.dump(fullconfig, c, default_flow_style=False)
        print(configfile + ' successfully saved!')
        print('WARNING: This file should be protected with OS level permission.  ANYONE with this file will have credentials to your vROps system!!!')

    def version(self):
        print("Blue Medora vROpsCLI")
        print("Version " + VERSION)
        print("Copyright (c) 2018 Blue Medora LLC")
        print("This work is licensed under the terms of the MIT license.") 
        print("For a copy, see <https://opensource.org/licenses/MIT>.") 
        print("")
        print("For more information on Blue Medora, contact sales@bluemedora.com")
        print("For technical assistance with this utility, contact devops@bluemedora.com")


    def __init__(self, user=None, password=None, host=None):
        self.config = {}
        requests.packages.urllib3.disable_warnings()
        if user and password and host:
            self.config['user'] = user
            self.config['pass'] = password
            self.config['host'] = host
            self.token=clilib.getToken(self.config)
        else:
            try:
                # Just Source Config
                self.config=clilib.getConfig()["default"]
                self.token=clilib.getToken(self.config)
            except IOError:
                print("No authentication information found!")
                print("Use --user, --password, and --host to specify on the command line")
                print("You may also setup a saved credential file at " + os.path.join(str(Path.home()), ".vropscli.yml") + " by running the following:")
                print("    vropscli --user <username> --password <password> --host <host> saveCliCred")
                print("Please review the documentation to understand the ramifications of using a credential file")
                sys.exit(1)


if __name__ == '__main__':
  # Using simplistic argument parsing to avoid conflicts with Fire (and currently only used for debug messages
  verbose=False
  for arg in sys.argv:
      if arg == "-v":
          verbose=True
  try:
    fire.Fire(vropscli)
  except requests.exceptions.HTTPError as e:
    if verbose==True:
        print("Error: " + str(e))
        print("Returned data: " + e.response.text)
    else:
        print("Error: " + str(e))
        print("Pass the -v flag for more verbose error messages")
  except Exception as e:
    if verbose==True:
        print("Error: " + str(e))
        traceback.print_exc()       
    else:
        print("Error: " + str(e))
        print("Pass the -v flag for more verbose error messages")
    
  
