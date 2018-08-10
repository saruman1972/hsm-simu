import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_FM(cmdObj):
	""" Translate a ZEK or ZAK from LMK to ZMK. """
	""" Command Pattern:
	    request: Message header + 'FM' + Flag + ZMK + ZEK/ZAK + Atalla Variant + Delimiter + Key Scheme ZMK + Key Scheme LMK + Key Check Value Type + End message delimiter + Message Trailer
	    response: Message header + 'FN' + Error code + ZEK/ZAK under ZMK + Check Value + End Message delimiter + Message Trailer
	"""
	
	if cmdObj.Flag == '0':
		keyType = 'ZEK'
	elif cmdObj.Flag == '1':
		keyType = 'ZAK'
	else:
		raise ValueError('ZEK/ZAK Flag error')
	
	(schemeZMK, schemeLMK, kcvLength) = extractKeySchemeAndKcvLength(cmdObj)
	ZMK = decryptKeyUnderLMK('ZMK', unhexlify(cmdObj.ZMK.value), cmdObj.ZMK.scheme)
	clearZEK_ZAK = decryptKeyUnderLMK(keyType, unhexlify(cmdObj.ZEKZAK.value), cmdObj.ZEKZAK.scheme)
	zmkScheme = KeyScheme(ZMK, schemeZMK)
	cipherZEK_ZAK = zmkScheme.encrypt(clearZEK_ZAK)
	
	zek_zak = KeyScheme(clearZEK_ZAK)
	kcv = hexlify(zek_zak.encrypt("\0\0\0\0\0\0\0\0")).upper()
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.ZEKZAKUnderZMK = KeyVariable(hexlify(cipherZEK_ZAK).upper(), schemeZMK)
	respObj.CheckValue = DataVariable(kcv[:kcvLength])
	return respObj
