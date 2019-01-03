#!/usr/bin/env python3

# vropscli: Tool for interacting with vROps API from the command line
# Copyright (c) 2018 Blue Medora LLC
# This work is licensed under the terms of the MIT license.
#  For a copy, see <https://opensource.org/licenses/MIT>.

import requests
import logging
import re
import sys
import time
import json
import base64
from math import ceil
from yaml import load,dump
from sys import exit
from os import path
from pathlib import Path


ENCODE='fjciek29Dvi@Cji $icjkedCCDjd'

# Vigenere ciphere for passwords in text file
def vig(txt, key, typ='d'):
    k_len = len(key)
    k_ints = [ord(i) for i in key]
    txt_ints = [ord(i) for i in txt]
    ret_txt = ''
    for i in range(len(txt_ints)):
        adder = k_ints[i % k_len]
        if typ == 'd':
            adder *= -1

        v = (txt_ints[i] - 32 + adder) % 95

        ret_txt += chr(v + 32)

    #print ret_txt
    return ret_txt

def getConfig():
    '''
    Function returns a yaml object of the default config file
    File should live in '~/.vropscli.yml'
    '''
    configfile=path.join(str(Path.home()), ".vropscli.yml")
    with open(path.expanduser(configfile),"r") as c:
        config = load(c)
    # Test for encrypted password, and if not then add it.
    for sectionkey,section in config.items():
        if not "passencrypt" in section:
            try:
                config[sectionkey]["passencrypt"] = vig(config[sectionkey]["pass"],ENCODE,'e')
                del config[sectionkey]["pass"]
            except KeyError as e:
                print('vropscli could not find the key ' + str(e) + ' while reading the config file.')
                exit(1)
            try:
                with open(path.expanduser(configfile),"w") as newconfig:
                    dump(config, newconfig, default_flow_style=False)
            except:
                print("Failed to save new encryption key for " + sectionkey + " in file " + path.expanduser(configfile))
                exit(1)

    # Now read through each section and add "pass" to the in-memory data structure!
    for sectionkey,section in config.items():
       config[sectionkey]["pass"] = vig(config[sectionkey]["passencrypt"],ENCODE,'d')
    return config

def getToken(conf):
    host=conf['host']
    user=conf['user']
    passwd=conf['pass']
    url = "https://" + host + "/suite-api/api/auth/token/acquire"
    payload = "{\r\n  \"username\" : \"" + user + "\",\r\n  \"authSource\" : \"local\",\r\n  \"password\" : \"" + passwd + "\",\r\n  \"others\" : [ ],\r\n  \"otherAttributes\" : {\r\n  }\r\n}"
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        }
    try:
        response = requests.request("POST", url, data=payload, headers=headers, verify=0, timeout=10)
        if response.status_code < 300:
            return json.loads(response.text)
        else:
            print('Return code: ' + str(r.status_code))
            print('Return text: ')
            print(r.text)
            sys.exit(1)
    except Exception as e:
        print('Error authenticating to vROPs system.  Check the passed hostname or parameters in .vropscli.yml')
        sys.exit(1)

def get_headers():
    return {
        'content-type': 'application/json;charset=UTF-8',
        'Accept': 'application/json;charset=UTF-8'
    }

def get_headers_plain():
    return {
        'content-type': 'application/json',
        'Accept': 'application/json'
    }

def get_token_header(token):
       return {
            'authorization': "vRealizeOpsToken " + token,
            'accept': "application/json;charset=UTF-8",
            'content-type': 'application/json;charset=UTF-8',
        }

def get_status(host, password):
    '''
    Returns the slice status for the node
    '''
    url = 'https://' + host + '/casa/sysadmin/slice/online_state'
    try:
        r = requests.get(url, headers=get_headers(), auth=requests.auth.HTTPBasicAuth('admin', password), verify=False)
    except Exception as e:
        print('get_status() threw an exception')
        return None


    if r.status_code == 200:
        return r.json()
    else:
        return None

def wait_for_casa(host, timeout=40):
    '''
    Returns true once the casa api returns a 401 (not authorized)
    Casa will return a 500 if the api is not running yet

    NOTE: vRops 6.3 tends to take 24 30 second iterations, while
    other versions start casa on boot.
    '''
    url = 'https://' + host + '/casa/stats/adapters/cluster'
    c = 0
    while True:
        c = c + 1
        if c == timeout:
            print('Timed out while waiting for casa to come online')
            return False
        try:
            r = requests.get(url, verify=False)
            if int(r.status_code) == 401:
                print('Casa is online')
                sleep(30) # CASA is online, but dont return right away
                return True
            else:
                print('Waiting for casa to come online')
                sleep(30)
        except:
            print('Exception when trying to GET ' + url)
            return False

def lookup_object_id_by_name(token, host, adapterType, objectType, objectName):
    '''
    Returns a tuple of (collection of vROps objects id's by name, whether this is a partial collection)
    A partial collection is returned if there are too many pages of objects from the API
    '''
    uuids = []
    url = f'https://{host}/suite-api/api/adapterkinds/{adapterType}/resourcekinds/{objectType}/resources?name={objectName}'
    pageLimit = 100
    while (url != None and pageLimit > 0):
        resp = requests.get(url, headers=get_token_header(token), verify=False)
        objData = json.loads(resp.text)

        uuids.extend(map(lambda x: x["identifier"], objData["resourceList"]))

        pageLimit -= 1

        # If the results are paginated, there will be a "next" link
        # Check if one exists, and if so, set that to be our next url; otherwise set to None
        nextHref = next((x["href"] for x in objData["links"] if x["name"] == "next"), None)
        if nextHref is None:
            url = None
        else:
            url = f'https://{host}{nextHref}'

    # In practice, hitting the pageLimit should almost never happen, and is almost certainly an error
    # We only check the pageLimit as a stopgap to prevent infinite loops
    return (uuids, pageLimit == 0)

def create_relationships_by_ids(token, host, parentUuid, childUuids):
    '''
    Adds a relationship between objects identified by UUID
    Returns a tuple of (success flag, response object)
    '''
    url = f'https://{host}/suite-api/api/resources/{parentUuid}/relationships/CHILD'
    reqBody = json.dumps({"uuids": childUuids})

    r = requests.post(url, data=reqBody, headers=get_token_header(token), verify=False)

    return (r.status_code == 204, r)
