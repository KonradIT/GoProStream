## GoPro Instant Streaming v1.0
##
## By @Sonof8Bits (Python code) and @KonradIT (GoPro API hacks)
##
## 1. Connect your desktop or laptop to your GoPro via WIFI.
## 2. Run this script.
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

def get_command_msg(id):
	return "_GPHD_:%u:%u:%d:%1lf\n" % (0, 0, 2, 0)

## Sends Record command to GoPro Camera, must be in Video mode!
RECORD=True

def gopro_live():
	UDP_IP = "10.5.5.9"
	UDP_PORT = 8554
	KEEP_ALIVE_PERIOD = 2500
	KEEP_ALIVE_CMD = 2

	MESSAGE = get_command_msg(KEEP_ALIVE_CMD)
	URL = "http://10.5.5.9:8080/live/amba.m3u8"
	response = urllib.request.urlopen('http://10.5.5.9/gp/gpControl/info').read()
	if b"HD4" in response or b"HD3.2" in response or b"HD5" in response:
		print("HERO4/HERO5/HERO+ camera")
		##
		## HTTP GETs the URL that tells the GoPro to start streaming.
		##
		urllib.request.urlopen("http://10.5.5.9/gp/gpControl/execute?p1=gpStream&a1=proto_v2&c1=restart").read()
		if RECORD:
			urllib.request.urlopen("http://10.5.5.9/gp/gpControl/command/shutter?p=1").read()
		print("UDP target IP:", UDP_IP)
		print("UDP target port:", UDP_PORT)
		print("message:", MESSAGE)
		print("Press ctrl+C to quit this application.\n")

		##
		## Opens the stream over udp in ffplay. This is a known working configuration by Reddit user hoppjerka:
		## https://www.reddit.com/r/gopro/comments/2md8hm/how_to_livestream_from_a_gopro_hero4/cr1b193
		##
		subprocess.Popen("ffplay -loglevel panic -fflags nobuffer -f:v mpegts -probesize 8192 udp://:8554", shell=True)

		if sys.version_info.major >= 3:
			MESSAGE = bytes(MESSAGE, "utf-8")

		while True:
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
			sleep(KEEP_ALIVE_PERIOD/1000)
	else:
		PASSWORD=urllib.request.urlopen("http://10.5.5.9/bacpac/sd").read()
		#Needs testing
		print("HERO3/3+/2 camera")
		urllib.request.urlopen("http://10.5.5.9/camera/PV?t=" + PASSWORD + "&p=%02").read()
		subprocess.Popen("ffplay " + URL, shell=True)

def quit_gopro(signal, frame):
	if RECORD:
		urllib.request.urlopen("http://10.5.5.9/gp/gpControl/command/shutter?p=0").read()
	sys.exit(0)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, quit_gopro)
	gopro_live()
