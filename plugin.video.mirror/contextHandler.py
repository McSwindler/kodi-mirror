import sys
import urlparse
import serverSettings

args = urlparse.parse_qs(sys.argv[1])
def _getParam(name, isSingle = True):
    val = args.get(name, None)
    if val is not None and isSingle:
        val = val[0]
    return val

mode = _getParam('mode')
item = _getParam('id')

if mode == 'remove':
    serverSettings.removeServer(item)
    xbmc.executebuiltin("Container.Refresh")