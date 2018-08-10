#!/usr/bin/python
# -*- coding: gbk -*-

import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_KU(cmdObj):
    """ Generate Secure Message with Integrity and Optional Confidentiality and PIN Change """
    """ Command Pattern:
        request: Message header + 'KU' + Mode Flag + Scheme ID + MK-SMI + Primary Account Number + Integrity Session Data + Plaintext Data Length + Plaintext Data + Delimiter(;) + MK-SMC + TK + Confidentiality Session Data + Offset + Cipher Data Length + Cipher Data + Delimiter(;) + Source PIN Encryption Key Type + Source PIN Encryption Key + Source PIN Block Format + Destination PIN Block Format + Primary Account Number + MK-AC + End message delimiter + Message Trailer
        response: Message header + 'KV' + Error code + ARPC + End Message delimiter + Message Trailer
    """
    
    if len(cmdObj.MK_SMI.value) != 32:
        raise ValueError('MK-SMI length error')
    if cmdObj.MK_SMI.scheme == '':
        MK_SMI = decryptKeyUnderLMK('MK-SMI', unhexlify(cmdObj.MK_SMI.value))
    else:
        MK_SMI = decryptKeyUnderLMK('MK-SMI', unhexlify(cmdObj.MK_SMI.value), cmdObj.MK_SMI.scheme)
    # Plain Data最后有一个分隔符
    atc = cmdObj.IntegritySessionData.value[-2:]
    sessionKey = icSessionKey(icKeyDerivation(MK_SMI, hexlify(cmdObj.PAN.value), ''), atc)
    block = padDataBlock(cmdObj.PlainData.value)
    mac = calcMAC(sessionKey, block, '\x00'*8)

    respObj = CommandObj()
    respObj.ResponseCode = DataVariable('00')

    respObj.MAC = DataVariable(mac)

    return respObj
