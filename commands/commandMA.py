import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_MA(cmdObj):
    """ Generate a MAC on given data. """
    """ Command Pattern:
        request: Message header + 'MA' + TAK + Data + End message delimiter + Message Trailer
        response: Message header + 'MB' + Error code + MAC + End Message delimiter + Message Trailer
    """
    TAK = decryptKeyUnderLMK('TAK', unhexlify(cmdObj.TAK.value), cmdObj.TAK.scheme)
    mac = calcMAC(TAK, cmdObj.Data.value, "\0\0\0\0\0\0\0\0")
    
    respObj = CommandObj()
    respObj.ResponseCode = DataVariable('00')
    respObj.MAC = DataVariable(string.upper(hexlify(mac))[:8])
    return respObj
