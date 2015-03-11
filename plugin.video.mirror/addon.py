import urllib
import urlparse
import operator
import time, random

# Dharma compatibility (import md5)
try:
    import hashlib
except:
    import md5

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

import serverSettings
from MirrorPlayer import MirrorPlayer


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

myaddon = xbmcaddon.Addon()
path = xbmc.translatePath(myaddon.getAddonInfo('profile')).decode("utf-8")

def _build_url(query):
    return base_url + '?' + urllib.urlencode(query)
def _translation(id):
    return myaddon.getLocalizedString(id).encode('utf-8')
def _getParam(name, isSingle = True):
    val = args.get(name, None)
    if val is not None and isSingle:
        val = val[0]
    return val
def _get_SID():
    t1 = time.time()
    t2 = t1 + random.getrandbits(32)
    try: 
        # Eden & + compatible
        base = hashlib.md5( str(t1 +t2) )
    except:
        # Dharma compatible
        base = md5.new( str(t1 +t2) )
    sid = base.hexdigest()
    return sid
    
    
def main():
    servers = serverSettings.readServers()
    for server in servers:
        li = xbmcgui.ListItem(unicode(server['name']))
        
        runner = xbmc.translatePath(myaddon.getAddonInfo('path')).decode("utf-8") + '/contextHandler.py'
        arg = 'mode=remove&id=' + str(server['id'])
        li.addContextMenuItems([(_translation(30001), "XBMC.RunScript(" + runner + ", " + arg + ")")])
        
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=_build_url({'mode': 'server', 'id': str(server['id'])}), listitem=li, isFolder=False)
        
    #Create server    
    li = xbmcgui.ListItem(_translation(30002))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=_build_url({'mode': 'add'}), listitem=li, isFolder=True)
    
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(addon_handle)
    
def addServer():
    dialog = xbmcgui.Dialog()
    keyboard = xbmc.Keyboard("", _translation(32001))
    keyboard.doModal()
    if not keyboard.isConfirmed():
        return False
        
    ip = dialog.input(_translation(32002), "", xbmcgui.INPUT_IPADDRESS)
    if ip is None or ip == "":
        return False
    
    port = dialog.input(_translation(32003), "8080", xbmcgui.INPUT_NUMERIC)
    if port is None or port == "":
        return False
    
    serverdata = {"name": keyboard.getText(), "host": ip, "port": int(port), "id": _get_SID()}
    serverSettings.addServer(serverdata)
    xbmc.executebuiltin("Container.Refresh")
    return True

def startMirror(id):
    server = serverSettings.getServer(id)
    if server is None:
        xbmc.log('No server for id: ' + id, xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Error', 'That server doesn\'t exists')
        return False
    print server
    player = MirrorPlayer()
    player.withSocket(server['host'], int(server['port']))
    player.playFromServer()
    while not xbmc.abortRequested and player.isActive():
        xbmc.sleep(500) 
    xbmc.log('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Trying to delete...')
    del player
    


mode = _getParam('mode')
if mode is None:
    main()
elif mode == 'add':
    addServer()
elif mode == 'server':
    startMirror(_getParam('id'))
                
        