import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_FI(cmdObj):
	""" Generate a ZEK or ZAK. """
	""" Command Pattern:
	    request: Message header + 'FI' + Flag + ZMK + Atalla Variant + Delimiter + Key Scheme ZMK + Key Scheme LMK + Key Check Value Type + End message delimiter + Message Trailer
	    response: Message header + 'FI' + Error code + ZEK/ZAK under ZMK + ZEK/ZAK under LMK + Check Value + End Message delimiter + Message Trailer
	"""
	
	if cmdObj.Flag == '0':
		keyType = 'ZEK'
	elif cmdObj.Flag == '1':
		keyType = 'ZAK'
	else:
		raise ValueError('ZEK/ZAK Flag error')
	
	(schemeZMK, schemeLMK, kcvLength) = extractKeySchemeAndKcvLength(cmdObj)
	clearZEK_ZAK = genRandomKey(Configure.CFG_KEY_LENGTH/2)
	ZMK = decryptKeyUnderLMK('ZMK', unhexlify(cmdObj.ZMK.value), cmdObj.ZMK.scheme)
	cipherKeyUnderLMK = encryptKeyUnderLMK(keyType, clearZEK_ZAK, schemeLMK)
	zmkScheme = KeyScheme(ZMK, schemeZMK)
	cipherKeyUnderZMK = zmkScheme.encrypt(clearZEK_ZAK)
	
	zek_zak = KeyScheme(clearZEK_ZAK)
	kcv = hexlify(zek_zak.encrypt("\0\0\0\0\0\0\0\0")).upper()
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.ZEKZAKUnderZMK = KeyVariable(hexlify(cipherKeyUnderZMK).upper(), schemeZMK)
	respObj.ZEKZAKUnderLMK = KeyVariable(hexlify(cipherKeyUnderLMK).upper(), schemeLMK)
	respObj.CheckValue = DataVariable(kcv[:kcvLength])
	return respObj
