from socket import *
from binascii import *
import time

def clientDemo(ip, port, message):
	sndSocket = socket(AF_INET, SOCK_STREAM)
	connectOk = False
	sndSocket.connect((ip, port))
	while True:
		sndSocket.send(message)
		head = sndSocket.recv(2)
		if (head == ""):
			print "got nothing"
			break
		msgLen = ord(head[0])*256 + ord(head[1])
		msg = sndSocket.recv(msgLen)
		print "response=" + msg
		print "press <q> to quit, others continue"
		key = raw_input()
		if ((key == 'q') or (key == 'Q')):
			break
	sndSocket.close()
	pass

def serverDemo(port, message):
	s = socket(AF_INET, SOCK_STREAM)
	s.bind((gethostbyname(gethostname()), port))
	s.listen(1)		# only 1 connection permited simultaneously
		
	timeout = 1.0				# timeout = 1sec
	while True:
		print "press <q> to quit the test, others continue"
		key = raw_input()
		if ((key == 'q') or (key == 'Q')):
			break
			
		print "begin"
		(rcvSocket, addressInfo) = s.accept()
		while True:
			print "press <q> to quit the loop, others continue"
			key = raw_input()
			if ((key == 'q') or (key == 'Q')):
				break
			rcvSocket.send(message)
		rcvSocket.close()
	s.close()
	pass
	

message = '1234CW320D4D18109327D69C994F0AA348A7583568274934067611;1010106'
message = '1234EE3B3A0EC90E9C558B111111FFFFFF06673010402800123456789012345667301040280N'
message = '    GCDA05B7A979CBD9A1DA05B7A979CBD9A1U063A0E7C0F2124E54BFA531C4095771D'
message = '    CWF72E9942D953183477039F757ABE1DBB4026742559049274;0707106'
message = 'XE234531D5EC4317AE2AB0939F7DE1EEFA2999999FFFFFF0601234567890123450001523471DDDDDD2C33A934FAA783878E6A0001890C7D62601413000152347'
message = '682C33A934FAA783878E6A0001890C7D62601674E0E9F12782CD5413000152347'
# should return '    GD0056CC09E7CFDC4CEF56CC09E7CFDC4CEF63A0E7C0F2124E54BFA531C4095771D'
nbytes = len(message)
head = chr(nbytes/256) + chr(nbytes%256)
#head += chr(0x00)*2
print head+message
#clientDemo(gethostbyname(gethostname()), 6666, head+message)
clientDemo('172.16.57.110', 8, head+message)
#serverDemo(30012, message)

