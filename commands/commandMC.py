#!/usr/bin/python
# -*- coding: gbk -*-

import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_MC(cmdObj):
    """ Verify a MAC and. """
    """ Command Pattern:
        request: Message header + 'MC' + TAK + MAC + Data + End message delimiter + Message Trailer
        response: Message header + 'MD' + Error code + End Message delimiter + Message Trailer
    """
    TAK = decryptKeyUnderLMK('TAK', unhexlify(cmdObj.TAK.value), cmdObj.TAK.scheme)
    mac = calcMAC(TAK, cmdObj.Data.value, "\0\0\0\0\0\0\0\0")
    finalMAC = string.upper(hexlify(mac))[:8]
    
    respObj = CommandObj()
    if cmdObj.MAC.value == finalMAC:
        respObj.ResponseCode = DataVariable('00')
    else:    # 校验失败
        respObj.ResponseCode = DataVariable('01')
    return respObj
