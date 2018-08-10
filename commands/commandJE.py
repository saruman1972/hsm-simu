import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_JE(cmdObj):
    """ Translate a PIN from encryption under a ZPK to encryption under the LMK. """
    """ Command Pattern:
        request: Message header + 'JE' + ZPK + PIN Block + PIN Block Format Code + Account Number + End message delimiter + Message Trailer
        response: Message header + 'JF' + Error code + PIN + End Message delimiter + Message Trailer
    """

    respObj = CommandObj()

    ZPK = decryptKeyUnderLMK('ZPK', unhexlify(cmdObj.ZPK.value), cmdObj.ZPK.scheme)
    zpk = KeyScheme(ZPK)
    pinblock = zpk.decrypt(unhexlify(cmdObj.PINBlock.value))
    (clearPIN,rslt) = extrackPINFromPINBlock(pinblock, cmdObj.AccountNumber.value, cmdObj.PINBlockFormatCode.value)
    if rslt != '00':
        respObj.ResponseCode = DataVariable(rslt)
        return respObj
    print "clearPIN=", clearPIN
    if (len(clearPIN) < 4) or (len(clearPIN) > 12):
        respObj.ResponseCode = DataVariable('24')
        return respObj
    cipherPIN = encryptPINUnderLMK(clearPIN, cmdObj.AccountNumber.value)

    respObj = CommandObj()
    respObj.ResponseCode = DataVariable('00')
    respObj.PIN = DataVariable(cipherPIN)
    return respObj
