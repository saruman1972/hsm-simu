#!/usr/bin/python
# -*- coding: gbk -*-

import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_KQ(cmdObj):
    """ ARQC (or TC/AAC) Verification and/or ARPC Generation. """
    """ Command Pattern:
        request: Message header + 'KQ' + Mode Flag + Scheme ID + MK-AC + Primary Account Number + Application Transaction Counter + Unpredictable Number + Transaction Data Length + Transaction Data + Delimiter(;) + ARQC + Authorization Response Code + End message delimiter + Message Trailer
        response: Message header + 'KR' + Error code + ARPC + End Message delimiter + Message Trailer
    """
    
    if len(cmdObj.MK_AC.value) != 32:
        raise ValueError('MK-AC length error')
    if cmdObj.MK_AC.scheme == '':
        MK_AC = decryptKeyUnderLMK('MK-AC', unhexlify(cmdObj.MK_AC.value))
    else:
        MK_AC = decryptKeyUnderLMK('MK-AC', unhexlify(cmdObj.MK_AC.value), cmdObj.MK_AC.scheme)
    # Transaction Data最后有一个分隔符
    sessionKey = icSessionKey(icKeyDerivation(MK_AC, hexlify(cmdObj.PAN.value), ''), cmdObj.ATC.value)
    resp_cd = '00'
    if cmdObj.ModeFlag.value == '0' or cmdObj.ModeFlag.value == '1':
        block = padDataBlock(cmdObj.TransactionData.value)
        ac = calcMAC(sessionKey, block, '\x00'*8)
        if ac == cmdObj.ARQC.value:
            resp_cd = '00'
        else:
            resp_cd = '01'

    respObj = CommandObj()
    respObj.ResponseCode = DataVariable(resp_cd)

    if cmdObj.ModeFlag.value == '1' or cmdObj.ModeFlag.value == '2':
        k = pyDes.triple_des(sessionKey)
        arpc = k.encrypt(blockXOR(cmdObj.ARQC.value, cmdObj.ARC.value+'\x00\x00\x00\x00\x00\x00'))
        respObj.ARPC = DataVariable(arpc)
    else:
        respObj.ARPC = DataVariable('')

    return respObj
