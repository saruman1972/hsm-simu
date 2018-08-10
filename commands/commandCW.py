#!/usr/bin/python
# -*- coding: gbk -*-

import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_CW(cmdObj):
    """ Generate a VISA CVV for encoding on a card. """
    """ Command Pattern:
        request: Message header + 'CW' + CVK_A + CVK_B + Primary Account Number + Delimiter(;) + Expiration Date + Service Code + End message delimiter + Message Trailer
        response: Message header + 'CX' + Error code + CVV + End Message delimiter + Message Trailer
    """
    
    if len(cmdObj.CVK_AB.value) != 32:
        raise ValueError('CVK length error')
    if cmdObj.CVK_AB.scheme == '':
        CVK_A = decryptKeyUnderLMK('CVK', unhexlify(cmdObj.CVK_AB.value[:16]))
        CVK_B = decryptKeyUnderLMK('CVK', unhexlify(cmdObj.CVK_AB.value[16:]))
    else:
        CVK = decryptKeyUnderLMK('CVK', unhexlify(cmdObj.CVK_AB.value), cmdObj.CVK_AB.scheme)
        CVK_A = CVK[:8]
        CVK_B = CVK[8:]
    # Primary Account Number最后有一个分隔符
    CVV = genCVV(cmdObj.PrimaryAccountNumber.value, cmdObj.ExpirationDate.value, cmdObj.ServiceCode.value, CVK_A, CVK_B)
    
    respObj = CommandObj()
    respObj.ResponseCode = DataVariable('00')
    respObj.CVV = DataVariable(CVV)
    return respObj
