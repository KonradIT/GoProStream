## GoPro Instant Streaming v1.0_r1
##
## By @Sonof8Bits and @KonradIT
##
## WOL touch by @5perseo, code updated by @podfish
##
## 1. Connect your desktop or laptop to your GoPro via WIFI.
## 2. Set the parameters below.
## 3. Run this script.
##
## Supported cameras:
## GoPro HERO5 (incl. Session), HERO4 (incl. Session), HERO+, HERO3+, HERO3, HERO2 w/ WiFi BacPac.
##
## That's all! When done, press CTRL+C to quit this application.
## 

import sys
import socket
#from urllib.request import urlopen --> module import error
# https://stackoverflow.com/questions/2792650/python3-error-import-error-no-module-name-urllib2
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
import subprocess
from time import sleep
import signal
import json
import re
import http

def get_command_msg(id):
	return "_GPHD_:%u:%u:%d:%1lf\n" % (0, 0, 2, 0)

## Parameters:
##
VERBOSE=False
## Sends Record command to GoPro Camera, must be in Video mode!
RECORD=False
##
## Saves the feed to a custom location
SAVE=False
SAVE_FILENAME="goprofeed3"
SAVE_FORMAT="ts"
SAVE_LOCATION="/tmp/"
## for wake_on_lan
GOPRO_IP = '10.5.5.9'
GOPRO_MAC = 'DEADBEEF0000'


def gopro_live():
	UDP_IP = "10.5.5.9"
	UDP_PORT = 8554
	KEEP_ALIVE_PERIOD = 2500
	KEEP_ALIVE_CMD = 2

	MESSAGE = get_command_msg(KEEP_ALIVE_CMD)
	URL = "http://10.5.5.9:8080/live/amba.m3u8"
	try:
        # original code - response_raw = urllib.request.urlopen('http://10.5.5.9/gp/gpControl').read().decode('utf-8')
		response_raw = urlopen('http://10.5.5.9/gp/gpControl').read().decode('utf-8')
		jsondata=json.loads(response_raw)
		response=jsondata["info"]["firmware_version"]
		import re
		match = re.match(r"([a-z]+)([0-9]+)", response, re.I)
		if match:
    			model=match.groups()[0]
		
	except http.client.BadStatusLine:
		response = urlopen('http://10.5.5.9/camera/cv').read().decode('utf-8')
	if model=="HD4" or model=="HD3.2" or model=="HD5" or model=="H" or model=="HX" or model=="HD6":
		print("branch HD4")
		print(jsondata["info"]["model_name"]+"\n"+jsondata["info"]["firmware_version"])
		##
		## HTTP GETs the URL that tells the GoPro to start streaming.
		##
		urlopen("http://10.5.5.9/gp/gpControl/execute?p1=gpStream&a1=proto_v2&c1=restart").read()
		if RECORD:
			urlopen("http://10.5.5.9/gp/gpControl/command/shutter?p=1").read()
		print("UDP target IP:", UDP_IP)
		print("UDP target port:", UDP_PORT)
		print("message:", MESSAGE)
		print("Recording on camera: " + str(RECORD))

		## GoPro HERO4 Session needs status 31 to be greater or equal than 1 in order to start the live feed.
		if model=="HX" or model=="H":
			connectedStatus=False
			while connectedStatus == False:
				req=urlopen("http://10.5.5.9/gp/gpControl/status")
				data = req.read()
				encoding = req.info().get_content_charset('utf-8')
				json_data = json.loads(data.decode(encoding))
				if json_data["status"]["31"] >= 1:
					connectedStatus=True
		##
		## Opens the stream over udp in ffplay. This is a known working configuration by Reddit user hoppjerka:
		## https://www.reddit.com/r/gopro/comments/2md8hm/how_to_livestream_from_a_gopro_hero4/cr1b193
		##
		loglevel_verbose=""
		if VERBOSE==False:
			loglevel_verbose = "-loglevel panic"
		if SAVE == False:
			subprocess.Popen("ffplay " + loglevel_verbose + " -fflags nobuffer -f:v mpegts -probesize 8192 udp://10.5.5.100:8554", shell=True)
		else:
			if SAVE_FORMAT=="ts":
				TS_PARAMS = " -acodec copy -vcodec copy "
			else:
				TS_PARAMS = ""
			SAVELOCATION = SAVE_LOCATION + SAVE_FILENAME + "." + SAVE_FORMAT
			print("Recording locally: " + str(SAVE))
			print("Recording stored in: " + SAVELOCATION)
			print("Note: Preview is not available when saving the stream.")
			subprocess.Popen("ffmpeg -i 'udp://:10.5.5.100:8554' -fflags nobuffer -f:v mpegts -probesize 8192 " + TS_PARAMS + SAVELOCATION, shell=True)
		if sys.version_info.major >= 3:
			MESSAGE = bytes(MESSAGE, "utf-8")
		print("Press ctrl+C to quit this application.\n")
		while True:
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
			sleep(KEEP_ALIVE_PERIOD/1000)
	else:
		print("branch hero3"+response)
		if "Hero3" in response or "HERO3+" in response:
			print("branch hero3")
			PASSWORD=urlopen("http://10.5.5.9/bacpac/sd").read()
			print("HERO3/3+/2 camera")
			Password =  str(PASSWORD, 'utf-8')
			text=re.sub(r'\W+', '', Password)
			urlopen("http://10.5.5.9/camera/PV?t=" + text + "&p=%02")
			subprocess.Popen("ffplay " + URL, shell=True)

def quit_gopro(signal, frame):
	if RECORD:
		urlopen("http://10.5.5.9/gp/gpControl/command/shutter?p=0").read()
	sys.exit(0)

def wake_on_lan(macaddress):
	"""switches on remote computers using WOL. """
	
	#check macaddress format and try to compensate
	if len(macaddress) == 12:
		pass
	elif len(macaddress) == 12 + 5:
		sep = macaddress[2]
		macaddress = macaddress.replace(sep, '')
	else:
		raise ValueError('Incorrect MAC Address Format')
	#Pad the sync stream
	data = ''.join(['FFFFFFFFFFFF', macaddress * 20])
	send_data = bytes.fromhex(data)
			
	# Broadcast to lan
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	sock.sendto(send_data, (GOPRO_IP, 9))

if __name__ == '__main__':
	wake_on_lan(GOPRO_MAC)
	signal.signal(signal.SIGINT, quit_gopro)
	gopro_live()
