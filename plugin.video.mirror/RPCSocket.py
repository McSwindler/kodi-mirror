import sys
import socket
import threading
try:
    import simplejson as json
except:
    import json
class RPCSocket:
    def __init__(self, host, port, callbacks=None):
        if host is not None and port is not None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._callbacks = callbacks
            self._keepAlive = True
            self._connect(host, port)

    def _connect(self, host, port):
#        while True:
        self.sock.settimeout(100)
        self.sock.connect((host, port))
        self.sock.settimeout(None)
        threading.Thread(target=self._wait).start()    
            
    def setCallback(self, method, callback):
        if self._callbacks is None:
            self._callbacks = {}
        self._callbacks[str(method)] = callback
        
    def _wait(self):
        datas = []
        data = ""
        while self._keepAlive:
            try:
                a = self.sock.recv(1)
            except:
                break
            if not a:
                break
            data += a
            try:
                js = json.loads(data)
                data = ""
            except:
                continue
            if self._callbacks is not None and js:
                if 'id' in js and str(js['id']) in self._callbacks:
                    self._callbacks[str(js['id'])](self, js)
                elif 'method' in js and js['method'] in self._callbacks:
                    self._callbacks[js['method']](self, js)
                    
    def isAlive(self):
        return self._keepAlive

    def send(self, payload, callback=None):
            if callback is not None:
                self.setCallback(payload['id'], callback)
            sent = self.sock.send(json.dumps(payload))
            if sent == 0:
                raise RuntimeError("socket connection broken")
    def kill(self):
        try:
            self.sock.shutdown(1)
            self.sock.close()
        finally:
            self._keepAlive = False