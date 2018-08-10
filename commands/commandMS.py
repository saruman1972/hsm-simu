import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *
import string

def command_MS(cmdObj):
    """ To generate a MAB for a large message using either a TAK or a ZAK. If the
        key is single length use ANSI X9.9 MAC generation or if the key is double
        length use ANSI X9.19 MAC generation. """
    """ Command Pattern:
        request: Message header + 'MS' + Message Block Number + Key Type + Key Length + Message Length + Key + IV + Message Length + Message Block + End message delimiter + Message Trailer
        response: Message header + 'MT' + Error code + MAB + End Message delimiter + Message Trailer
    """
    
    if cmdObj.KeyType.value == '0':
        KeyType = 'TAK'
    elif cmdObj.KeyType.value == '1':
        KeyType = 'ZAK'
    else:
        raise ValueError('invalid key type [' + cmdObj.KeyType.value + ']')
    KEY = decryptKeyUnderLMK(KeyType, unhexlify(cmdObj.Key.value), cmdObj.Key.scheme)

    if cmdObj.KeyLength.value == '0':
        keyLength = 8
    elif cmdObj.KeyLength.value == '1':
        keyLength = 16
    else:
        raise ValueError('invalid key length [' + cmdObj.KeyLength.value + ']')
    if len(KEY) != keyLength:
        raise ValueError('key length error')

    if cmdObj.MessageType.value == '0':
        messageBlock = cmdObj.MessageBlock.value
    elif cmdObj.MessageType.value == '1':
        messageBlock = unhexlify(cmdObj.MessageBlock.value)
    else:
        raise ValueError('invalid message type [' + cmdObj.MessageType.value + ']')

    if (cmdObj.MessageBlockNumber.value == '0'):        # The only block.
        mac = calcMAC(KEY, messageBlock, "\0\0\0\0\0\0\0\0")
    elif (cmdObj.MessageBlockNumber.value == '1'):    # The first block.
        mac = calcMAC(KEY, messageBlock, "\0\0\0\0\0\0\0\0")
    elif (cmdObj.MessageBlockNumber.value == '2'):    # A middle block.
        mac = calcMAC(KEY, messageBlock, unhexlify(cmdObj.IV.value))
    elif (cmdObj.MessageBlockNumber.value == '3'):    # The last block.
        mac = calcMAC(KEY, messageBlock, unhexlify(cmdObj.IV.value))
    else:
        raise ValueError('invalid message block number [' + cmdObj.MessageBlockNumber.value + ']')
    
    respObj = CommandObj()
    respObj.ResponseCode = DataVariable('00')
    respObj.MAB = DataVariable(string.upper(hexlify(mac)))
    return respObj
