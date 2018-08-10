import traceback
from socket import *
from select import *
import string
import threading
import time
from binascii import *
import wx
from Command import MessageProcessor
import Configure

class Communication:
    """ communication abstract base class, should be inherited """

    def __init__(self, messageProcessor=None, log=None, address=None):
        self.messageProcessor = messageProcessor
        self.log = log
        if address == None:
#            self.address = gethostbyname(gethostname())
            self.address = ""
        else:
            self.address = address
        self.active = False
        self.serverThread = None
        self.workThreads = []

    def quit(self):
        print "Communication quiting"
        self.active = False
        if (self.serverThread != None):
            self.serverThread.quit()
        for workThread in self.workThreads:
            workThread.quit()

    def openCommunication(self):
        self.active = True

        # duplex communication client should only open server socket
        localPort = Configure.CFG_COMMUNICATION_PORT
        self.serverThread = ServerThread(self, localPort, self.address)
        self.serverThread.start()

    def setReceiveSocket(self, rcvSocket):
        # connect ok, start the working daemon
        workThread = WorkingThread(self, rcvSocket, self.messageProcessor)
        self.workThreads.append(workThread)
        workThread.start()

    def removeWorkThread(self, workThread):
        for i in range(len(self.workThreads)):
            if (self.workThreads[i] == workThread):
                del self.workThreads[i]
                return

    def logIncomingMessage(self, message):
        if (self.log != None):
            message = 'Message Received:===============================\n' + message + '\n================================='
            self.log.addMessage(message)

    def logOutgoingMessage(self, message):
        if (self.log != None):
            message = 'Message Send:**************************\n' + message + '\n***********************************'
            self.log.addMessage(message)




class WorkingThread(threading.Thread):
    def __init__(self, comm, workSocket, messageProcessor=None, receive_timeout=10, select_timeout=1):
        threading.Thread.__init__(self)
        self.comm = comm
        self.messageProcessor = messageProcessor
        self.workSocket = workSocket
        self.receive_timeout = receive_timeout
        self.select_timeout = select_timeout
        self.active = True

    def quit(self):
        self.active = False
        print "Working Thread quiting"

    def run(self):
        try:
            while self.active:
                req_msg = self.receive()
                self.comm.logIncomingMessage(req_msg)
                print self.messageProcessor
                if (self.messageProcessor != None):
                    try:
                        rsp_msg = self.messageProcessor.ProcessMessage(req_msg)
                        self.send(rsp_msg)
                        self.comm.logOutgoingMessage(rsp_msg)
                    except ValueError, e:
                        print "ValueError:",e
        except Exception, e:        # socket broken
            print traceback.format_exc()

        # fall through here to terminate the current thread
        # new thread will be created after the communication reestablished
        print self,"Working Thread Terminated"
        self.workSocket.close()
        self.comm.removeWorkThread(self)

    def receive(self):
        while self.active:
            (rlist,wlist,elist) = select([self.workSocket], [], [], self.select_timeout)
            if (len(rlist) > 0):
                # message arrived, read it
                break

        # message take 4 bytes, but only use the leading 2 bytes
        data = self.workSocket.recv(2)
        if (data == ""):    # socket has broken
            raise ValueException('socket has broken')
        msgLen = ord(data[0])*256 + ord(data[1])

        curLen = 0
        msg = ""
        startT = time.time()
        while (self.active and (curLen < msgLen)):
            t = time.time()
            if (t - startT > self.receive_timeout):
                break;

            (rlist,wlist,elist) = select([self.workSocket], [], [], self.select_timeout)
            if (len(rlist) == 0):    # not ready yet, continue looping
                continue
            curMsg = self.workSocket.recv(msgLen-curLen)
            if (curMsg == None):    # socket has broken
                raise ValueExceptino('socket has broken')
            msg += curMsg
            curLen += len(curMsg)

        return msg

    def send(self, message):
        nbytes = len(message)
        data = chr(nbytes/256) + chr(nbytes%256)   # + chr(0x00)*2
        self.workSocket.send(data)
        while (self.active and (nbytes > 0)):
            byte_snds = self.workSocket.send(message)
            if (byte_snds == 0):        # socket has broken
                raise ValueException('socket has broken')
            message = message[byte_snds:]
            nbytes -= byte_snds


class ServerThread(threading.Thread):
    """ socket client class, monitor the creation of connection """

    def __init__(self, comm, port, address, timeout=1.0):
        threading.Thread.__init__(self)
        self.comm = comm
        self.port = port
        self.address = address
        self.timeout = timeout
        self.active = True

    def quit(self):
        self.active = False
        print "Server Thread quiting"

    def run(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
#        self.socket.bind((gethostbyname(gethostname()), htons(self.port)))
        self.socket.bind((self.address, self.port))
        self.socket.listen(5)

        while self.active:
            connectOk = False
            while (self.active and (connectOk == False)):
                (rlist,wlist,elist) = select([self.socket], [], [], self.timeout)
                if (len(rlist) == 0):    # no incoming connection, continue looping
                    continue

                (rcvSocket, addressInfo) = self.socket.accept()
                connectOk = True
                self.comm.setReceiveSocket(rcvSocket)

                # show status
#                if (self.comm.log != None):
#                    self.comm.log.addMsg("connected with " + addressInfo[0])
                print "connected with " + addressInfo[0]

        self.socket.close()
        print "Server Thread Terminated"















if (__name__ == "__main__"):
    class Logger:
        def __init__(self):
            pass

        def addMsg(self, message):
            print message

    logger = Logger()
    mp = MessageProcessor('CommandPattern.xml')
    comm = Communication(mp, log=logger)

    comm.openCommunication()

