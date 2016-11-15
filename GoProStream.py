## GoPro Instant Streaming v1.0
##
## By @Sonof8Bits (Python code) and @KonradIT (GoPro API hacks)
##
## 1. Connect your desktop or laptop to your GoPro via WIFI.
## 2. Run this script.
##
## That's all! When done, press CTRL+C to quit this application.
##

import sys
import socket
import urllib.request
import subprocess
from time import sleep

def get_command_msg(id):
	return "_GPHD_:%u:%u:%d:%1lf\n" % (0, 0, 2, 0)
	
UDP_IP = "10.5.5.9"
UDP_PORT = 8554
KEEP_ALIVE_PERIOD = 2500
KEEP_ALIVE_CMD = 2
MESSAGE = get_command_msg(KEEP_ALIVE_CMD)
URL = "http://10.5.5.9:8080/live/amba.m3u8"
CAMERA = input("Camera connected is a HERO4/HERO+/HERO5? [y/n]: ")
if(CAMERA == "y"):
	##
	## HTTP GETs the URL that tells the GoPro to start streaming.
	##
	urllib.request.urlopen("http://10.5.5.9/gp/gpControl/execute?p1=gpStream&a1=proto_v2&c1=restart").read()

	print("UDP target IP:", UDP_IP)
	print("UDP target port:", UDP_PORT)
	print("message:", MESSAGE)
	print("Press ctrl+C to quit this application.\n")

	##
	## Opens the stream over udp in ffplay. This is a known working configuration by Reddit user hoppjerka:
	## https://www.reddit.com/r/gopro/comments/2md8hm/how_to_livestream_from_a_gopro_hero4/cr1b193
	##
	subprocess.Popen("ffplay -fflags nobuffer -f:v mpegts -probesize 8192 udp://:8554", shell=True)

	if sys.version_info.major >= 3:
		MESSAGE = bytes(MESSAGE, "utf-8")

	while True:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
		sleep(KEEP_ALIVE_PERIOD/1000)
else:
	PASSWORD=urllib.request.urlopen("http://10.5.5.9/bacpac/sd").read()
	print(PASSWORD)
	#urllib.request.urlopen("http://10.5.5.9/camera/PV?t=" + PASSWORD + "&p=%02").read()
	#subprocess.Popen("ffplay -fflags nobuffer -f:v mpegts -probesize " + URL, shell=True)

