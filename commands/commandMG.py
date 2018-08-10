import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_MG(cmdObj):
    """ Translate a TAK from encryption under the LMK to encryption under a ZMK.
        Used to send a key to another party. """
    """ Command Pattern:
        request: Message header + 'MG' + ZMK + TAK + Atalla Variant + Delimiter + Key Scheme ZMK + Key Scheme LMK + Key Check Value Type + End message delimiter + Message Trailer
        response: Message header + 'MH' + Error code + TAK + Check Value + End Message delimiter + Message Trailer
    """
    
    (schemeZMK, schemeLMK, kcvLength) = extractKeySchemeAndKcvLength(cmdObj)
    ZMK = decryptKeyUnderLMK('ZMK', unhexlify(cmdObj.ZMK.value), cmdObj.ZMK.scheme)
    clearTAK = decryptKeyUnderLMK('TAK', unhexlify(cmdObj.TAK.value), cmdObj.TAK.scheme)
    zmkScheme = KeyScheme(ZMK, schemeZMK)
    cipherTAK = zmkScheme.encrypt(clearTAK)
    
    tak = KeyScheme(clearTAK)
    kcv = hexlify(tak.encrypt("\0\0\0\0\0\0\0\0")).upper()
    
    respObj = CommandObj()
    respObj.ResponseCode = DataVariable('00')
    respObj.TAK = KeyVariable(hexlify(cipherTAK).upper(), schemeZMK)
    respObj.CheckValue = DataVariable(kcv[:kcvLength])
    return respObj
