require '../gopro-rb-api/lib/GoPro'
require '../gopro-rb-api/lib/constants.rb'
require 'socket'
MESSAGE="_GPHD_:0:0:2:0.000000"

gpCamera = Camera.new
gpCamera.livestream(Livestream::RESTART)
while true
	s = TCPSocket.new('10.5.5.9', 8554)
	s.send(MESSAGE,0)
	s.close
	puts 'call'
	sleep 2.5
end