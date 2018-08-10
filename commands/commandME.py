#!/usr/bin/python
# -*- coding: gbk -*-

import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_ME(cmdObj):
    """ Verify a MAC and, if successful, generate a MAC on the same data with adifferent key. """
    """ Command Pattern:
        request: Message header + 'ME' + Source TAK + Destiniation TAK + MAC + Data + End message delimiter + Message Trailer
        response: Message header + 'MF' + Error code + MAC + End Message delimiter + Message Trailer
    """
    SourceTAK = decryptKeyUnderLMK('TAK', unhexlify(cmdObj.SourceTAK.value), cmdObj.SourceTAK.scheme)
    DestinationTAK = decryptKeyUnderLMK('TAK', unhexlify(cmdObj.DestinationTAK.value), cmdObj.DestinationTAK.scheme)
    mac = calcMAC(SourceTAK, cmdObj.Data.value, "\0\0\0\0\0\0\0\0")
    finalMAC = string.upper(hexlify(mac))[:8]
    
    respObj = CommandObj()
    if cmdObj.MAC.value == finalMAC:
        respObj.ResponseCode = DataVariable('00')
        mac = calcMAC(DestinationTAK, cmdObj.Data.value, "\0\0\0\0\0\0\0\0")
        respObj.MAC = DataVariable(string.upper(hexlify(mac))[:8])
    else:    # 校验失败不返回MAC
        respObj.ResponseCode = DataVariable('01')
        respObj.MAC = DataVariable('00000000')
    return respObj
