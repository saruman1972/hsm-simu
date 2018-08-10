import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *
import string

def command_MQ(cmdObj):
    """ Generate a MAC (MAB) for a large message. """
    """ Command Pattern:
        request: Message header + 'MQ' + Message Block Number + TAK + IV + Message Length + Message Block + End message delimiter + Message Trailer
        response: Message header + 'MR' + Error code + MAB + End Message delimiter + Message Trailer
    """
    
    TAK = decryptKeyUnderLMK('TAK', unhexlify(cmdObj.TAK.value), cmdObj.TAK.scheme)

    if (cmdObj.MessageBlockNumber.value == '0'):    # The only block.
        mac = calcMAC(TAK, cmdObj.MessageBlock.value, "\0\0\0\0\0\0\0\0")
    elif (cmdObj.MessageBlockNumber.value == '1'):    # The first block.
        mac = calcMAC(TAK, cmdObj.MessageBlock.value, "\0\0\0\0\0\0\0\0")
    elif (cmdObj.MessageBlockNumber.value == '2'):    # A middle block.
        mac = calcMAC(TAK, cmdObj.MessageBlock.value, unhexlify(cmdObj.IV.value))
    elif (cmdObj.MessageBlockNumber.value == '3'):    # The last block.
        mac = calcMAC(TAK, cmdObj.MessageBlock.value, unhexlify(cmdObj.IV.value))
    else:
        raise ValueError('invalid message block number [' + cmdObj.MessageBlockNumber.value + ']')
    
    respObj = CommandObj()
    respObj.ResponseCode = DataVariable('00')
    respObj.MAB = DataVariable(string.upper(hexlify(mac)))
    return respObj
