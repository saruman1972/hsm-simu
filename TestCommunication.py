from socket import *
from binascii import *
import time
from Communication import *

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
        print "response(X)=" + hexlify(msg)
        print "press <q> to quit, others continue"
        key = raw_input()
        if ((key == 'q') or (key == 'Q')):
            break
    sndSocket.close()
    pass

def serverDemo(port, message):
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((gethostbyname(gethostname()), port))
    s.listen(1)        # only 1 connection permited simultaneously

    timeout = 1.0                # timeout = 1sec
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


message = '1234CWF72E9942D953183477039F757ABE1DBB3568274934067611;1010106'
# verify ARQC
message = '1234KQ02843FDA0B15CA1618843FDA0B15CA1618\x12\x34\x56\x78\x90\x12\x34\x56\x01\x23000009\x12\x34\x56\x78\x90\x12\x34\x56\x78;\xD7\x32\x52\x60\x05\x6B\x3F\xD3'
# generate ARPC
message = '1234KQ22843FDA0B15CA1618843FDA0B15CA1618\x12\x34\x56\x78\x90\x12\x34\x56\x01\x230000\xD7\x32\x52\x60\x05\x6B\x3F\xD300'
# generate MAC
message = '1234KU02FC9142CB51FEF5D6FC9142CB51FEF5D6\x12\x34\x56\x78\x90\x12\x34\x56\x00\x00\x00\x00\x00\x00\x12\x340008\x12\x34\x56\x78\x90\x12\x34\x56;'
message = '303030304B51303258' + hexlify('440373F965AC246FE292520FBBA0856E') + '214950226062320101C200000000323500000000000000000000000001560000180000000011080401000000007D0001C203A0B8063BF464604CE8DAB845'
message = '303030304B51303258' + hexlify('843FDA0B15CA1618843FDA0B15CA1618') + '21495022606232010002000000003235000000000000000000000000015600001234560156110805000041561712340002abcdabcd3Bc5b284508f5f9243'
message = '303030304B51303258' + hexlify('843FDA0B15CA1618843FDA0B15CA1618') + '214950226062320101C200000000323500000000000000000000000001560000180000000011080501000000007D0001C203A0B8063BEDF6406F1AD67629'

message = unhexlify(message)

#message = '1234KQ20843FDA0B15CA1618843FDA0B15CA16181234567890123456012300000000000000000000'
#message = '1234EE3B3A0EC90E9C558B111111FFFFFF06673010402800123456789012345667301040280N'
#message = '    GCDA05B7A979CBD9A1DA05B7A979CBD9A1U063A0E7C0F2124E54BFA531C4095771D'
#message = '    CWF72E9942D953183477039F757ABE1DBB4026742559049274;0707106'
#message = '1234DEXFCBA7CF5972CF0DDFCBA7CF5972CF0DD1E4761D49E05A55F0667103636768501234567890123456127N3469134'
# should return '    GD0056CC09E7CFDC4CEF56CC09E7CFDC4CEF63A0E7C0F2124E54BFA531C4095771D'
nbytes = len(message)
head = chr(nbytes/256) + chr(nbytes%256)
#head += chr(0x00)*2
#clientDemo(gethostbyname(gethostname()), 6666, head+message)
#serverDemo(30012, message)
#clientDemo(gethostbyname(gethostname()), 8888, head+message)
clientDemo('10.168.2.231', 6666, head+message)

