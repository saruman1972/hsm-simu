import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_MI(cmdObj):
    """ Translate a TAK from encryption under a ZMK to encryption under the LMK.
        Used to receive a key from another party. """
    """ Command Pattern:
        request: Message header + 'MI' + ZMK + TAK + Atalla Variant + Delimiter + Key Scheme ZMK + Key Scheme LMK + Key Check Value Type + End message delimiter + Message Trailer
        response: Message header + 'MJ' + Error code + TAK + Check Value + End Message delimiter + Message Trailer
    """
    
    (schemeZMK, schemeLMK, kcvLength) = extractKeySchemeAndKcvLength(cmdObj)
    ZMK = decryptKeyUnderLMK('ZMK', unhexlify(cmdObj.ZMK.value), cmdObj.ZMK.scheme)
    takScheme = KeyScheme(ZMK, cmdObj.TAK.scheme)
    clearTAK = takScheme.decrypt(unhexlify(cmdObj.TAK.value))
    
    cipherTAK = encryptKeyUnderLMK('TAK', clearTAK, schemeLMK)
    tak = KeyScheme(clearTAK)
    kcv = hexlify(tak.encrypt("\0\0\0\0\0\0\0\0")).upper()
    
    respObj = CommandObj()
    respObj.ResponseCode = DataVariable('00')
    respObj.TAK = KeyVariable(hexlify(cipherTAK).upper(), schemeLMK)
    respObj.CheckValue = DataVariable(kcv[:kcvLength])
    return respObj
