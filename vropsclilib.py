#!/usr/bin/env python3

import requests
import logging
import re
import sys
import time
import datetime
import json 
from math import ceil
from yaml import load
from sys import exit
from os import path

def getConfig():
    '''
    Function returns a yaml object of the default config file
    File should live in '~/.config/vropstp.yml'
    '''
    configfile="~/.config/vrops-cli.yml"
    try:
        with open(path.expanduser(configfile),"r") as c:
            config = load(c)
        return config
    except:
        print("Failed to read config file: " + path.expanduser(configfile) )
        print("Did you copy the example file from the repo to your home directory?")
        exit(1)

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
    response = requests.request("POST", url, data=payload, headers=headers, verify=0)
    return json.loads(response.text)

def get_headers():
    return {
        'content-type': 'application/json;charset=UTF-8',
        'Accept': 'application/json;charset=UTF-8'
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


