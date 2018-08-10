import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_A6(cmdObj):
	""" To import a key encrypted under a ZMK. """
	""" Command Pattern:
	    request: Message header + 'A6' + Key Type + ZMK + Key + Key Scheme LMK + Atalla Variant + End message delimiter + Message Trailer
	    response: Message header + 'A7' + Error code + Key + Check Value + End Message delimiter + Message Trailer
	"""
	
	ZMK = decryptKeyUnderLMK('ZMK', unhexlify(cmdObj.ZMK.value), cmdObj.ZMK.scheme)
	keyScheme = KeyScheme(ZMK, cmdObj.Key.scheme)
	clearKey = keyScheme.decrypt(unhexlify(cmdObj.Key.value))
	
	keyType = Configure.KeyTypeTable[cmdObj.KeyType.value]
	cipherKey = encryptKeyUnderLMK(keyType, clearKey, cmdObj.KeySchemeLMK.value)
	key = KeyScheme(clearKey)
	kcv = hexlify(key.encrypt("\0\0\0\0\0\0\0\0")).upper()
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.Key = KeyVariable(hexlify(cipherKey).upper(), cmdObj.KeySchemeLMK.value)
	respObj.CheckValue = DataVariable(kcv[:6])
	return respObj
