# Kodi Mirror
A Kodi plugin that allows you to mirror the content from another Kodi installation.

## Setup
1. On the server Kodi installation, allow control access via HTTP and 'Remote Control'
	- Settings -> Services -> Webserver -> [Check] Allow access of XBMC/Kodi via HTTP (Necessary)
	- Settings -> Services -> Remote control -> [Check] Allow programs on other systems to control XBMC/Kodi (Recommended)
2. Note down the server IP and webserver port.
3. Install the Kodi Mirror plugin on the client installations.
4. Click 'Add Server' within the plugin and input the IP and port as noted above.
5. Watch

## Settings
- Timeout: How long to try and get the playing content from the server.
- Max Latency: The maximum time difference of the currently playing media that is allowed. (This would need to be larger the slower your network is)

### Remote Access
In theory, this should allow for remote mirror access. Two ports will need to be forwarded to the server: 9090 and the webserver port.
9090 is the default port for the TCP Socket API, this can be changed via advanced settings, but currently this plugin does not support it.
This option has not been tested, if you happen to try it out, let me know how it works out: wilingua@gmail.com

## Author
James Swindle
wilingua@gmail.com
