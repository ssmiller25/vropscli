#!/usr/bin/env python3
import vropsclilib as clilib
import requests
import json
import pprint
import fire
import csv
import sys


VERSION="1.0.1"

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
        response_parsed = json.loads(response.text)
        return response_parsed

    def getAdapters(self):
        url = "https://" + self.config['host'] + "/suite-api/api/adapters"

        response = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)
        response_parsed = json.loads(response.text)
        print("id,Name,Type")
        for instance in response_parsed["adapterInstancesInfoDto"]:
            print(instance["id"] + "," + instance["resourceKey"]["name"] + "," + instance["resourceKey"]["adapterKindKey"])

    def getCollectors(self):
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
        #for resource_kinds in rs_parsed['resource-kind']:
        #    print

    def getAdapterConfig(self, adapterId):
        adapterInfo = self.getAdapter(adapterId)
        settingsinfo = {}
        for setting in adapterInfo["resourceKey"]["resourceIdentifiers"]:
            settingsinfo[setting["identifierType"]["name"]]=setting["value"]    
        csvheader = []
        csvrow = []
        #csvheader.append("name")
        #csvheader.append("description")
        csvheader = ["adapterkey","adapterKind","resourceKind","credentialId","collectorId","name","description"]
        #csvrow.append(adapterInfo["resourceKey"]["name"])
        #csvrow.append(adapterInfo["description"])
        csvrow.append(adapterInfo["id"])
        csvrow.append(adapterInfo["resourceKey"]["adapterKindKey"])
        csvrow.append(adapterInfo["resourceKey"]["resourceKindKey"])
        csvrow.append(adapterInfo["credentialInstanceId"])
        csvrow.append(adapterInfo["collectorId"])
        csvrow.append(adapterInfo["resourceKey"]["name"])
        csvrow.append(adapterInfo["description"])

        for configparam in adapterInfo["resourceKey"]["resourceIdentifiers"]:
            csvheader.append(configparam["identifierType"]["name"])
            csvrow.append(configparam["value"])
        print(','.join(csvheader))
        print(','.join(map(str,csvrow)))

    def getAdapterConfigs(self, adapterKindKey):
        url = "https://" + self.config['host'] + "/suite-api/api/adapters/?adapterKindKey=" + adapterKindKey
        response = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)

        csvheader = ["adapterkey","adapterKind","resourceKind","credentialId","collectorId","name","description"]

        settingsinfo = {}
        firstRun = 'true'
        response_parsed = json.loads(response.text)

        for adapterInfo in response_parsed["adapterInstancesInfoDto"]:
            csvrow = []
            csvrow.append(adapterInfo["id"])
            csvrow.append(adapterKindKey)
            csvrow.append(adapterInfo["resourceKey"]["resourceKindKey"])
            csvrow.append(adapterInfo["credentialInstanceId"])
            csvrow.append(adapterInfo["collectorId"])
            csvrow.append(adapterInfo["resourceKey"]["name"])
            csvrow.append(adapterInfo["description"])
      
            for configparam in adapterInfo["resourceKey"]["resourceIdentifiers"]:
                if (firstRun == 'true'): 
                    csvheader.append(configparam["identifierType"]["name"])
                csvrow.append(configparam["value"])
            if (firstRun == 'true'): 
                print(','.join(csvheader))
            print(','.join(map(str, csvrow)))
            firstRun = 'false'    

    def getAlertsDefinitionsByAdapterKind(self, adapterKindKey):
        url = "https://" + self.config['host'] + "/suite-api/api/alertdefinitions?adapterKind=" + adapterKindKey

        response = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)
        response_parsed = json.loads(response.text)
        print("{\"alertDefinitions\": " + json.dumps(response_parsed["alertDefinitions"]) + "}")

    def updateAlertDefinitions(self, alertConfigFile):
        with open(alertConfigFile) as jsonFile:
            alertDefinitions = json.load(jsonFile)

        url = 'https://' + self.config['host'] + '/suite-api/api/alertdefinitions'
        for alertDefinition in alertDefinitions["alertDefinitions"]:
            r = requests.put(url, data=json.dumps(alertDefinition), headers=clilib.get_token_header(self.token['token']), verify=False)

            if r.status_code < 300:
                print(alertDefinition["name"] + ' updated successfully.')
            else:
                print(alertDefinition["name"]  + ' update failed!')
                print(str(r.status_code))
                print(r.text)
                print("Submitted Data")
                print(json.dumps(alertDefinition))

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
        with open(alertConfigFile) as jsonFile:
            alertDefinitions = json.load(jsonFile)

        for alertDefinition in alertDefinitions["alertDefinitions"]:
            self.createAlertDefinition(adapterkey=alertDefinition)

    def createAlertDefinition(self, alertJSON):
        url = 'https://' + self.config['host'] + '/suite-api/api/alertdefinitions/' + alertDefinitionKey
        r = requests.post(url,  data=json.dumps(alertJSON), headers=clilib.get_token_header(self.token['token']), verify=False)
        if r.status_code < 300:
            print(adapterkey + ' alert successfully deleted.')
        else:
            print(adapterkey + ' delete failed!')
            print(str(r.status_code))
            print(r.text)       

    def deleteAlertDefinitions(self, alertConfigFile):
        with open(alertConfigFile) as jsonFile:
            alertDefinitions = json.load(jsonFile)

        for alertDefinition in alertDefinitions["alertDefinitions"]:
            self.deleteAlertDefinition(adapterkey=alertDefinition['id'])

    def deleteAlertDefinition(self, alertDefinitionKey):
        url = 'https://' + self.config['host'] + '/suite-api/api/alertdefinitions/' + alertDefinitionKey
        r = requests.delete(url, headers=clilib.get_token_header(self.token['token']), verify=False)
        if r.status_code < 300:
            print(adapterkey + ' alert successfully deleted.')
        else:
            print(adapterkey + ' delete failed!')
            print(str(r.status_code))
            print(r.text)

    def createAdapterInstances(self, resourceConfigFile, autostart=False):
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
                print(row['name'] + ' Failed!')
                print(str(r.status_code))
                print(r.text)
                print("Submitted Data")
                print(newadapterdata)


    def deleteAdapterInstances(self, resourceConfigFile):

        resourceConfigData = open(resourceConfigFile, newline='')
        resourceConfig = csv.DictReader(resourceConfigData)

        for row in resourceConfig:
            self.deleteAdapterInstance(adapterkey=row['adapterkey'])

        
    def deleteAdapterInstance(self, adapterkey):
        url = 'https://' + self.config['host'] + '/suite-api/api/adapters/' + adapterkey
        r = requests.delete(url, headers=clilib.get_token_header(self.token['token']), verify=False)
        if r.status_code < 300:
            print(adapterkey + ' adapter successfully deleted.')
        else:
            print(adapterkey + ' delete failed!')
            print(str(r.status_code))
            print(r.text)

            
    def updateAdapterInstances(self, resourceConfigFile, autostart=False):
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

            #print(newadapterdata)
            url = 'https://' + self.config['host'] + '/suite-api/api/adapters'
            r = requests.put(url, data=json.dumps(newadapterdata), headers=clilib.get_token_header(self.token['token']), verify=False)
            if r.status_code < 300:
                print(row['name'] + ' Adapter Successfully Updated - ' + str(r.status_code))
                #print(r.text)
                if autostart == True:
                    returndata=json.loads(r.text)
                    self.startAdapterInstance(adapterId=returndata["id"])
            else:
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
        '''
        Set solution license
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

    def getCredentials(self):
        url = "https://" + self.config['host'] + "/suite-api/api/credentials"

        response = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)
        credssum = {}
        response_parsed = json.loads(response.text)
        #return(response_parsed)
        for credentialInstances in response_parsed['credentialInstances']:
            credssum[credentialInstances["id"]]={'id': credentialInstances["id"], 'name': credentialInstances["name"], 'kind': credentialInstances["adapterKindKey"]}
        return credssum

    def getCredential(self, credentialId):
        url = "https://" + self.config['host'] + "/suite-api/api/credentials/" + credentialId 
        headers = {
            'authorization': "vRealizeOpsToken " + self.token['token'],
            'accept': "application/json",
            }
        response = json.loads(requests.request("GET", url, headers=headers, verify=False).text)
        csvheader = []
        csvrow = []
        #csvheader.append("name")
        #csvheader.append("description")
        csvheader = ["name","adapterKindKey","credentialKindKey"]
        #csvrow.append(adapterInfo["resourceKey"]["name"])
        #csvrow.append(adapterInfo["description"])
        csvrow.append(response["name"])
        csvrow.append(response["adapterKindKey"])
        csvrow.append(response["credentialKindKey"])

        for credfield in response["fields"]:
            csvheader.append(credfield["name"])
            if "value" in credfield:
                csvrow.append(credfield["value"])
            else:
                csvrow.append("")
        print(','.join(csvheader))
        print(','.join(map(str,csvrow)))

    def createCredentials(self, credConfigFile):
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
                print(row['name'] + ' Failed!')
                print(str(r.status_code))
                print(r.text)
                print("Submitted Data")
                print(newcreddata)

    def deleteCredential(self, credentialId):
        url = "https://" + self.config['host'] + "/suite-api/api/credentials/" + credentialId 
        headers = {
            'authorization': "vRealizeOpsToken " + self.token['token'],
            'accept': "application/json",
            }
        r = requests.request("DELETE", url, headers=headers, verify=False)
        if r.status_code < 300:
            print(credentialId + " successfully deleted!")
        else:
            print("Error removing " + credentialId)
            print(r.text)

    def getSolutionLicense(self, solutionId):
        '''
        Get available license
        '''
        url = 'https://' + self.config['host'] + '/suite-api/api/solutions/' + solutionId + '/licenses'
        r = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)
        return json.loads(r.text)

    def getSolution(self):
        '''
        Get all solutions installed
        '''
        url = 'https://' + self.config['host'] + '/suite-api/api/solutions'
        r = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)
        return json.loads(r.text)

    def getVropsLicense(self):
        '''
        Get installed VROps license
        '''
        url = 'https://' + self.config['host'] + '/suite-api/api/deployment/licenses'
        r = requests.request("GET", url, headers=clilib.get_token_header(self.token['token']), verify=False)
        return json.loads(r.text)


    def setVropsLicense(self, license_key):
        '''
        vrops license key
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

        #TODO: Make use a token request
        r = requests.post(url, data=json.dumps(data), headers=clilib.get_token_header(self.token['token']), verify=False)
        if r.status_code == 200:
            print('license key installed')
            return True
        else:
            print('Failed to license vrops')
            print(str(r.status_code))
            return False

    def uploadPak(self, pakFile, overwritePak=False):
        '''
        Upload a Pak file to the server
        '''
        if overwritePak == True:
            pak_handling_advice = 'STANDARD'
        else:
            pak_handling_advice = 'CLOBBER'
        url = 'https://' + self.config['host'] + '/casa/upgrade/cluster/pak/reserved/operation/upload'
        files = { 'contents': open(pakFile, 'rb') }
        data = { 'pak_handling_advice': pak_handling_advice }
        print("Startup Pak Upload.  This may take a while")
        r = requests.post(url, data=data, files=files, auth=requests.auth.HTTPBasicAuth(self.config["user"],self.config["pass"]), verify=False)
        if r.status_code < 300:
            print('Upload Successful!')
            return json.loads(r.text)
        else:
            print('Failed to Upload Pak')
            print(str(r.status_code))
            print(r.text)

    def getPakInfo(self, pakID):
        '''
        Get Uploaded Pak Info
        '''
        url = 'https://' + self.config['host'] + '/casa/upgrade/cluster/pak/' + pakID + '/information'
        r = requests.get(url, auth=requests.auth.HTTPBasicAuth(self.config["user"],self.config["pass"]), verify=False)
        if r.status_code < 300:
            return json.loads(r.text)
            return True
        else:
            print('Failed to Get Pak Info')
            print(str(r.status_code))

    def installPak(self, pakId, force_content_update=True):
        '''
        Install an uploaded Pak File
        '''
        if force_content_update == True:
            content_text = 'true'
        else:
            content_text = 'false'
        #data = { 'force_content_update': content_text }
        url = 'https://' + self.config['host'] + '/casa/upgrade/cluster/pak/' + pakId + '/operation/install'
        #r = requests.post(url, headers=clilib.get_headers(), data=data, auth=requests.auth.HTTPBasicAuth(self.config["user"],self.config["pass"]), verify=False)
        r = requests.post(url, headers=clilib.get_headers(), auth=requests.auth.HTTPBasicAuth(self.config["user"],self.config["pass"]), verify=False)
        if r.status_code < 300:
            print('Pak installation started.  Run "vropscli getCurrentActivity" to get current status')
            return True
        else:
            print('Failed to Install Pak')
            print('Return code: ' + str(r.status_code))
            print(r.text)

    def getPakStatus(self, pakID):
        '''
        Get Pak Installation during Upgrade
        '''
        url = 'https://' + self.config['host'] + '/casa/upgrade/cluster/pak/' + pakID + '/status'
        r = requests.get(url, auth=requests.auth.HTTPBasicAuth(self.config["user"],self.config["pass"]), verify=False)
        if r.status_code < 300:
            return json.loads(r.text)
            return True
        else:
            print('Failed to Get Pak Info')

    def getCurrentActivity(self):
        '''
        Get current activity of vROps
        '''
        url = 'https://' + self.config['host'] + '/casa/upgrade/cluster/pak/reserved/current_activity'
        r = requests.get(url, auth=requests.auth.HTTPBasicAuth(self.config["user"],self.config["pass"]), verify=False)
        if r.status_code < 300:
            return json.loads(r.text)
            return True
        else:
            print('Failed to Get Pak Info')

    def getAdapterCollectionStatus(self, adapterID):
        #set the url for the adapter instance
        url = 'https://' + self.config['host'] + '/suite-api/api/resources/' + adapterID 
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
        #set the url for the adapter instance
        url = 'https://' + self.config['host'] + '/suite-api/api/adapters/' + adapterId + '/monitoringstate/stop'
        #A put request to turn off the adapter
        r = requests.put(url, auth=requests.auth.HTTPBasicAuth(self.config['user'], self.config['pass']), verify=False)
        print("Adapter Stopped")

    def startAdapterInstance(self, adapterId):
        #set the url for the adapter instance
        url = 'https://' + self.config['host'] + '/suite-api/api/adapters/' + adapterId + '/monitoringstate/start'
        #A put request to turn on the adapter
        r = requests.put(url, auth=requests.auth.HTTPBasicAuth(self.config['user'], self.config['pass']), verify=False)
        print("Adapter Started")

    def version(self):
        print("Blue Medora vROpsCLI")
        print("Version " + VERSION)
        print("")
        print("For more information on Blue Medora, contact sales@bluemedora.com")
        print("For technical assistance with this utility, contact devops@bluemedora.com")


    def __init__(self):
        requests.packages.urllib3.disable_warnings()
        # Just Source Config
        self.config=clilib.getConfig()["default"]
        self.token=clilib.getToken(self.config)


#scalpel=tpscalpel()

# Testing of resource routine
#for resource in scalpel.getAllResources()["resourceList"]:
#  print(resource["identifier"] + ", " + resource["resourceKey"]["name"] + ", " + resource["resourceKey"]["resourceKindKey"])

# Pull a specific stat
#pprint.pprint(scalpel.getAllStats("7977ad1f-0932-4178-be0b-4b900696b74a", 1484024400000, 1484255700000))

if __name__ == '__main__':
  fire.Fire(vropscli)
