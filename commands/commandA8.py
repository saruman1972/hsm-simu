import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_A8(cmdObj):
	""" To encrypt a key under a ZMK for export. """
	""" Command Pattern:
	    request: Message header + 'A8' + Key Type + ZMK + Key + Key Scheme ZMK + Atalla Variant + End message delimiter + Message Trailer
	    response: Message header + 'A9' + Error code + Key + Check Value + End Message delimiter + Message Trailer
	"""
	
	keyType = Configure.KeyTypeTable[cmdObj.KeyType.value]
	ZMK = decryptKeyUnderLMK('ZMK', unhexlify(cmdObj.ZMK.value), cmdObj.ZMK.scheme)
	clearKey = decryptKeyUnderLMK(keyType, unhexlify(cmdObj.Key.value), cmdObj.Key.scheme)
	zmkScheme = KeyScheme(ZMK, cmdObj.KeySchemeZMK.value)
	cipherKey = zmkScheme.encrypt(clearKey)
	
	key = KeyScheme(clearKey)
	kcv = hexlify(key.encrypt("\0\0\0\0\0\0\0\0")).upper()
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.Key = KeyVariable(hexlify(cipherKey).upper(), cmdObj.KeySchemeZMK.value)
	respObj.CheckValue = DataVariable(kcv[:6])
	return respObj
