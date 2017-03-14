## GoPro Instant Streaming v1.0
##
## By @Sonof8Bits and @KonradIT
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
import urllib.request
import subprocess
from time import sleep
import signal
import json
import re

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
SAVE_FORMAT="mp4"
SAVE_LOCATION="/home/konrad/Videos/"

def gopro_live():
	UDP_IP = "10.5.5.9"
	UDP_PORT = 8554
	KEEP_ALIVE_PERIOD = 2500
	KEEP_ALIVE_CMD = 2

	MESSAGE = get_command_msg(KEEP_ALIVE_CMD)
	URL = "http://10.5.5.9:8080/live/amba.m3u8"
	response_raw = urllib.request.urlopen('http://10.5.5.9/gp/gpControl').read().decode('utf-8')
	jsondata=json.loads(response_raw)
	response=jsondata["info"]["firmware_version"]
	if "HD4" in response or "HD3.2" in response or "HD5" in response or "HX" in response:
		print(jsondata["info"]["model_name"]+"\n"+jsondata["info"]["firmware_version"])
		##
		## HTTP GETs the URL that tells the GoPro to start streaming.
		##
		urllib.request.urlopen("http://10.5.5.9/gp/gpControl/execute?p1=gpStream&a1=proto_v2&c1=restart").read()
		if RECORD:
			urllib.request.urlopen("http://10.5.5.9/gp/gpControl/command/shutter?p=1").read()
		print("UDP target IP:", UDP_IP)
		print("UDP target port:", UDP_PORT)
		print("message:", MESSAGE)
		print("Recording on camera: " + str(RECORD))

		## GoPro HERO4 Session needs status 31 to be greater or equal than 1 in order to start the live feed.
		if "HX" in response:
			connectedStatus=False
			while connectedStatus == False:
				req=urllib.request.urlopen("http://10.5.5.9/gp/gpControl/status")
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
			subprocess.Popen("ffplay " + loglevel_verbose + " -fflags nobuffer -f:v mpegts -probesize 8192 udp://:8554", shell=True)
		else:
			print("Recording locally: " + str(SAVE))
			print("Recording stored in: " + SAVE_LOCATION + SAVE_FILENAME + "." + SAVE_FORMAT)
			print("Note: Preview is not available when saving the stream.")
			SAVELOCATION=SAVE_LOCATION + SAVE_FILENAME + "." + SAVE_FORMAT
			subprocess.Popen("ffmpeg -i 'udp://:8554' -fflags nobuffer -f:v mpegts -probesize 8192 " + SAVELOCATION, shell=True)
		if sys.version_info.major >= 3:
			MESSAGE = bytes(MESSAGE, "utf-8")
		print("Press ctrl+C to quit this application.\n")
		while True:
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
			sleep(KEEP_ALIVE_PERIOD/1000)
	else:
		response = urllib.request.urlopen('http://10.5.5.9/camera/cv').read()
		if b"Hero3" in response:
			PASSWORD=urllib.request.urlopen("http://10.5.5.9/bacpac/sd").read()
			print("HERO3/3+/2 camera")
			Password =  str(PASSWORD, 'utf-8')
			text=re.sub(r'\W+', '', Password)
			urllib.request.urlopen("http://10.5.5.9/camera/PV?t=" + text + "&p=%02")
			subprocess.Popen("ffplay " + URL, shell=True)
		


def quit_gopro(signal, frame):
	if RECORD:
		urllib.request.urlopen("http://10.5.5.9/gp/gpControl/command/shutter?p=0").read()
	sys.exit(0)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, quit_gopro)
	gopro_live()
