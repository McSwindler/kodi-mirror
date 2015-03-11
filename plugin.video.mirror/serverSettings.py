try:
    import simplejson as json
except:
    import json
from multiprocessing import Pool
import os
from os.path import basename
import shutil
import time
from urlparse import urlparse

import requests

import xbmc
import xbmcaddon


_path = xbmc.translatePath(xbmcaddon.Addon('plugin.video.mirror').getAddonInfo('profile')).decode("utf-8")

if not os.path.exists(_path):
    os.makedirs(_path)
    
_serversFile = _path + '/servers.json'
    
def readServers():
    try:
        file = open(_serversFile, 'r')
        data = json.load(file)
        file.close()
        return data
    except:
        return []

def addServer(server):
    servers = readServers()
    servers.append(server)
    file = open(_serversFile, 'w')
    json.dump(servers, file)
    file.close()

def removeServer(id):
    servers = readServers()
    newList = []
    for server in servers:
        if 'id' in server and server['id'] != id:
            newList.append(server)
    
    file = open(_serversFile, 'w')
    json.dump(newList, file)
    file.close()    

def getServer(id):
    servers = readServers()
    for server in servers:
        if 'id' in server and server['id'] == id:
            return server    
    return None