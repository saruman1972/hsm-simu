import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_CC(cmdObj):
    """ Translate a PIN block from encryption under one ZPK to encryption under
        another ZPK and from one format to another. If the same ZPK is defined, only
        the PIN block is translated, and if the same PIN block format is defined, only
        the key is translated. """
    """ Command Pattern:
        request: Message header + 'CC' + Source ZPK + Destination ZPK + Maximum PIN Length + Source PIN Block + Source PIN Block Format + Destination PIN Block Format + Account Number + End message delimiter + Message Trailer
        response: Message header + 'CD' + Error code + PIN Length + Destination PIN Block + Destination PIN Block Format + End Message delimiter + Message Trailer
    """
    
    SourceZPK = decryptKeyUnderLMK('ZPK', unhexlify(cmdObj.SourceZPK.value), cmdObj.SourceZPK.scheme)
    src_zpk = KeyScheme(SourceZPK)
    DestinationZPK = decryptKeyUnderLMK('ZPK', unhexlify(cmdObj.DestinationZPK.value), cmdObj.DestinationZPK.scheme)
    dst_zpk = KeyScheme(DestinationZPK)
    
    src_pinblock = src_zpk.decrypt(unhexlify(cmdObj.SourcePINBlock.value))
    (clearPIN,rlt) = extrackPINFromPINBlock(src_pinblock, cmdObj.AccountNumber.value, cmdObj.SourcePINBlockFormat.value)
    print "clearPIN="+clearPIN
    dst_pinblock = genPINBlock(clearPIN, cmdObj.AccountNumber.value, cmdObj.DestinationPINBlockFormat.value)
    dst_pinblock = hexlify(dst_zpk.encrypt(dst_pinblock))
    
    respObj = CommandObj()
    respObj.ResponseCode = DataVariable('00')
    respObj.PINLength = DataVariable("%02d" % len(clearPIN))
    respObj.DestinationPINBlock = DataVariable(string.upper(dst_pinblock))
    respObj.DestinationPINBlockFormat = DataVariable(cmdObj.DestinationPINBlockFormat.value)
    return respObj
