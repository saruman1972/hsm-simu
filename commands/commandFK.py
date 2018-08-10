import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_FK(cmdObj):
	""" Translate a ZEK or ZAK from ZMK to LMK. """
	""" Command Pattern:
	    request: Message header + 'FK' + Flag + ZMK + ZEK/ZAK + Atalla Variant + Delimiter + Key Scheme ZMK + Key Scheme LMK + Key Check Value Type + End message delimiter + Message Trailer
	    response: Message header + 'FL' + Error code + ZEK/ZAK unser LMK + Check Value + End Message delimiter + Message Trailer
	"""
	
	if cmdObj.Flag == '0':
		keyType = 'ZEK'
	elif cmdObj.Flag == '1':
		keyType = 'ZAK'
	else:
		raise ValueError('ZEK/ZAK Flag error')
	
	(schemeZMK, schemeLMK, kcvLength) = extractKeySchemeAndKcvLength(cmdObj)
	ZMK = decryptKeyUnderLMK('ZMK', unhexlify(cmdObj.ZMK.value), cmdObj.ZMK.scheme)
	zek_zakScheme = KeyScheme(ZMK, cmdObj.ZEKZAK.scheme)
	clearZEK_ZAK = zek_zapScheme.decrypt(unhexlify(cmdObj.ZEKZAK.value))
	
	cipherZEK_ZAK = encryptKeyUnderLMK(keyType, clearZEK_ZAK, schemeLMK)
	zek_zak = KeyScheme(clearZEK_ZAK)
	kcv = hexlify(zek_zak.encrypt("\0\0\0\0\0\0\0\0")).upper()
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.ZEKZAKUnderLMK = KeyVariable(hexlify(cipherZEK_ZAK).upper(), schemeLMK)
	respObj.CheckValue = DataVariable(kcv[:kcvLength])
	return respObj
