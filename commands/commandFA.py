import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_FA(cmdObj):
    """ Translate a ZPK from encryption under a ZMK to encryption under the LMK.
        Used to receive a ZPK from another party. """
    """ Command Pattern:
        request: Message header + 'FA' + ZMK + ZPK + Atalla Variant + Delimiter + Key Scheme ZMK + Key Scheme LMK + Key Check Value Type + End message delimiter + Message Trailer
        response: Message header + 'FB' + Error code + ZPK + Check Value + End Message delimiter + Message Trailer
    """
    
    (schemeZMK, schemeLMK, kcvLength) = extractKeySchemeAndKcvLength(cmdObj)
    ZMK = decryptKeyUnderLMK('ZMK', unhexlify(cmdObj.ZMK.value), cmdObj.ZMK.scheme)
    zpkScheme = KeyScheme(ZMK, cmdObj.ZPK.scheme)
    clearZPK = zpkScheme.decrypt(unhexlify(cmdObj.ZPK.value))
    
    cipherZPK = encryptKeyUnderLMK('ZPK', clearZPK, schemeLMK)
    zpk = KeyScheme(clearZPK)
    kcv = hexlify(zpk.encrypt("\0\0\0\0\0\0\0\0")).upper()
    
    respObj = CommandObj()
    respObj.ResponseCode = DataVariable('00')
    respObj.ZPK = KeyVariable(hexlify(cipherZPK).upper(), schemeLMK)
    respObj.CheckValue = DataVariable(kcv[:kcvLength])
    return respObj
