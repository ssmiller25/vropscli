#!/usr/bin/env python3
import vropsclilib as clilib
import requests
import json
import pprint
import fire
import csv


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
        adapterinfo = self.getAdapter(adapterId)
        settingsinfo = {}
        for setting in adapterinfo["resourceKey"]["resourceIdentifiers"]:
            #settingsinfo.append({"name": setting["identifierType"]["name"], "value": setting["value"]})
            settingsinfo[setting["identifierType"]["name"]]=setting["value"]    
        #pprint.pprint(settingsinfo)
        csvheader = []
        csvrow = []
        csvheader.append("name")
        csvheader.append("description")
        csvrow.append(adapterinfo["resourceKey"]["name"])
        csvrow.append(adapterinfo["description"])
        for configparam in adapterinfo["resourceKey"]["resourceIdentifiers"]:
            csvheader.append(configparam["identifierType"]["name"])
            csvrow.append(configparam["value"])
        print(','.join(csvheader))
        print(','.join(csvrow))

    def createAdapterInstances(self, adapterKind, resourceConfigFile, credentialId, collectorId=1, autostart=False):
        resourceConfigData = open(resourceConfigFile, newline='')
        resourceConfig = csv.DictReader(resourceConfigData)

        for row in resourceConfig:
            # Suite-API specifically expects a list of dictionary objects, with only two ides of "name" and "value".  Not even asking why...
            resourceConfigItems = []

            for name, value in row.items():
                if (name == 'name') or (name == 'description') :
                    continue
                resourceConfigItems.append({'name':name, 'value':value})

            newadapterdata= {
                "name": row['name'],
                "description": row['description'],
                "collectorId": collectorId,
                "adapterKindKey": adapterKind,
                "resourceIdentifiers": resourceConfigItems,
                "credential": {
                    "id": credentialId
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
            print('Pak installation started.  Run "vropscli.py getCurrentActivity" to get current status')
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

    def stopAdapterInstance(self, adapterId):
        #set the url for the adapter instance
        url = 'https://' + self.config['host'] + '/suite-api/api/adapters/' + adapterId + '/monitoringstate/stop'
        #A put request to turn off the adapter
        r = requests.put(url, auth=requests.auth.HTTPBasicAuth(self.config['user'], self.config['pass']), verify=False)
        print("Adapter Stopped")
        return 0

    def startAdapterInstance(self, adapterId):
        #set the url for the adapter instance
        url = 'https://' + self.config['host'] + '/suite-api/api/adapters/' + adapterId + '/monitoringstate/start'
        #A put request to turn on the adapter
        r = requests.put(url, auth=requests.auth.HTTPBasicAuth(self.config['user'], self.config['pass']), verify=False)
        print("Adapter Started")
        return 0

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
