import xbmc, xbmcgui, xbmcaddon, xbmcvfs

import requests
try:
    import simplejson as json
except:
    import json
from RPCSocket import RPCSocket

musicprops = ["file", "duration", "year", "genre", "album", 
              "artist", "title", "rating", "lyrics", 
              "playcount", "lastplayed"]
pictureprops = ["title", "file"]
videoprops = ["title", "file", "genre", "year", "episode", "season",
              "top250", "rating", "playcount", "director",
              "mpaa", "plot", "plotoutline", "originaltitle",
              "duration", "studio", "tagline", "writer", "premiered",
              "lastplayed", "album", "votes", "trailer"]

class MirrorPlayer( xbmc.Player ):

    def __init__(self, *args, **kwargs):
        self._totalTime = 999999
        self._lastPos = 0
        self._pid = None
        self._type = ""
        self._webserv = ""
        self._itemId = -1 
        self._playstate = -1
        self._isActive = True
        super(MirrorPlayer, self).__init__(*args, **kwargs)
        
    def withSocket(self, host, port):
        self._webserv = 'http://%s:%d/' % (str(host), int(port))
        try:
            self.socket = RPCSocket(host, 9090, {'Player.OnPlay': self._onPlay, 'Player.OnPause': self._onPause, 'Player.OnStop': self._onStop})
        except:
            xbmcgui.Dialog().ok('Error', 'Unable to connect to the server via TCP', 'Please allow programs on other systems to control XBMC', 'until then, reduced functionality is available')
            self.socket = None
            return False
        return True
    
    def _onPlay(self, socket, data):
        print data
        if not self.isPaused():
            self._playstate = 1
        if self._playstate == 1:
            return False
        id = data['params']['data']['item']['id']
        if int(self._itemId) == int(id):
            self.pause()
        else:
            self.playFromServer()
        
    def _onPause(self, socket, data):
        if self.isPaused():
            self._playstate = 0
        if self._playstate != 0:
            self.pause()
    
    def _onStop(self, socket, data):
        print data
        self._itemId = -1
        self._playstate = -1
        xbmc.executebuiltin("PlayerControl(Stop)")
        if self.socket is None or self.socket.isAlive():
            self._waitForItem()
        
    def isActive(self):
        return self._isActive
            
    def onPlayBackStopped(self):
        if self._playstate == -1:
            return
        xbmc.log('Player stopped')
        if self.socket is not None:
            self.socket.kill()
        self._playstate = 1
        self._isActive = False
        
    def playFromServer(self):
        self._playstate = 1
        current = self._getItem()
        print current
        if 'error' in current:
            xbmc.log(current['error'], xbmc.LOGERROR)
            self._itemId = -1
            self._waitForItem()
        elif current['id'] != self._itemId:
            super(MirrorPlayer, self).play(current['stream'], current['listItem'])
            self._itemId = current['id']  
        
    def onPlayBackStarted( self ):
        xbmc.log('playback started')
        xbmc.executebuiltin("Dialog.Close(busydialog)")   
        self._totalTime = self.getTotalTime()
        
        seek = self._getSeek()
        print seek, seek['speed'] == 0
        if abs(seek['seek'] - self.getTime()) > 5:
            if seek['seek'] > 0:
                self.seekTime(seek['seek'])
            if seek['speed'] == 0:
                self.pause()  
            #TODO detect speed changes from server
        
    def onPlayBackResumed(self):
        xbmc.log('playback resumed')
        self._playstate = 1
    
    def onPlayBackPaused(self):
        xbmc.log('playback paused')
        self._playstate = 0

    def onPlayBackEnded( self ):
        self._playstate = -1 
        if self.socket is None or self.socket.isAlive():
            self._waitForItem()
            
    def isPaused():
        start_time = self.getTime()
        time.sleep(1)
        if self.getTime() != start_time:
            return False
        else:
            return True
        
    def _waitForItem(self):
        if self._playstate != -1:
            return False
        self._pid = None
        self._itemId = -1
        dialog = xbmcgui.DialogProgress()
        dialog.create('Server Status', 'Waiting for content to be played...')
        dialog.update(0)
        count = 0
        while self._playstate == -1 and self._isActive:
            item = self._getItem()
            if count > 20 or dialog.iscanceled():
                self._isActive = False
                break
            elif 'error' not in item:
                self.playFromServer()
                break
            else:
                dialog.update(count * 5)
                xbmc.sleep(500)
                count += 1
        dialog.close()
        if not self._isActive:
            self.socket.kill()
                    
    def _getItem(self):
        if self._pid is None:
            payload = {"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}
            r = requests.post(self._webserv + 'jsonrpc', data=json.dumps(payload))
            d = r.json()
            if 'error' in d:
                return {'error': d['error']}
            if len(d['result']) < 1:
                return {'error': 'No Item Playing'}
            self._type = d['result'][0]['type']
            self._pid = d['result'][0]['playerid']
        
        payload = {"jsonrpc": "2.0", "method": "Player.GetItem", "params": {"properties": videoprops, "playerid": self._pid}, "id": "getItem"}
        r = requests.post(self._webserv + 'jsonrpc', data=json.dumps(payload))
        d = r.json()
        if 'error' in d:
            return {'error': d['error']}
        file = d['result']['item']['file']
        data = d['result']['item']
        id = d['result']['item']['id']
        
        
        li = xbmcgui.ListItem(data['title'])  
        li.setInfo(self._type, data)
        
        if not xbmcvfs.exists(file):
            payload = {"jsonrpc": "2.0", "method": "Files.PrepareDownload", "params": {"path": file}, "id": "prepDownload"}
            r = requests.post(self._webserv + 'jsonrpc', data=json.dumps(payload))
            d = r.json()
            stream = '%s%s' % (self._webserv, d['result']['details']['path'])
        else:
            stream = file

        return {'listItem': li, 'stream': stream, 'id': id}
    
    def _getSeek(self):
        payload = {"jsonrpc": "2.0", "method": "Player.GetProperties", "params": {"properties": ["time", "speed"], "playerid": self._pid}, "id": "getItem"}
        r = requests.post(self._webserv + 'jsonrpc', data=json.dumps(payload))
        d = r.json()
        seek = float(d['result']['time']['milliseconds']) / 1000
        seek += d['result']['time']['seconds']
        seek += d['result']['time']['minutes'] * 60
        seek += d['result']['time']['hours'] * 60 * 60
        return {"seek": seek, "speed": d['result']['speed']}
    
    def __del__(self):
        print 'deleting player...'
        if self.socket is not None:
            self.socket.kill()
