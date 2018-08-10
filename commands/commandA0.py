import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_A0(cmdObj):
	""" To generate a key and optionally encrypt key under ZMK for transmission."""
	""" Command Pattern:
	    request: Message header + 'A0' + Mode + Key Type + Key Scheme LMK + ZMK + Key Scheme ZMK + Atalla Variant + End message delimiter + Message Trailer
	    response: Message header + 'A1' + Error code + Key under LMK + Key under ZMK + Check Value + End Message delimiter + Message Trailer
	"""
	
	clearKey = genRandomKey(Configure.CFG_KEY_LENGTH/2)
	keyType = Configure.KeyTypeTable[cmdObj.KeyType.value]
	cipherKeyUnderLMK = encryptKeyUnderLMK(keyType, clearKey, cmdObj.KeySchemeLMK.value)
	
	if cmdObj.Mode.value == '1':
		ZMK = decryptKeyUnderLMK('ZMK', unhexlify(cmdObj.ZMK.value), cmdObj.ZMK.scheme)
		zmkScheme = KeyScheme(ZMK, cmdObj.KeySchemeZMK.value)
		cipherKeyUnderZMK = zmkScheme.encrypt(clearKey)
	
	key = KeyScheme(clearKey)
	kcv = hexlify(key.encrypt("\0\0\0\0\0\0\0\0")).upper()
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.KeyUnderLMK = KeyVariable(hexlify(cipherKeyUnderLMK).upper(), cmdObj.KeySchemeLMK.value)
	if cmdObj.Mode.value == '1':
		respObj.KeyUnderZMK = KeyVariable(hexlify(cipherKeyUnderZMK).upper(), cmdObj.KeySchemeZMK.value)
	else:
		respObj.KeyUnderZMK = DataVariable('')
	respObj.CheckValue = DataVariable(kcv[:6])
	return respObj
