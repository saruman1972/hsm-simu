import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_FE(cmdObj):
	""" Translate a TMK, TPK or PVK from encryption under the LMK to encryption
		under a ZMK. """
	""" Command Pattern:
	    request: Message header + 'FE' + ZMK + TMK_TPK_PVK + Atalla Variant + Delimiter + Key Scheme ZMK + Key Scheme LMK + Key Check Value Type + End message delimiter + Message Trailer
	    response: Message header + 'FF' + Error code + TMK_TPK_PVK + Check Value + End Message delimiter + Message Trailer
	"""
	
	(schemeZMK, schemeLMK, kcvLength) = extractKeySchemeAndKcvLength(cmdObj)
	ZMK = decryptKeyUnderLMK('ZMK', unhexlify(cmdObj.ZMK.value), cmdObj.ZMK.scheme)
	clearTMK_TPK_PVK = decryptKeyUnderLMK('PVK', unhexlify(cmdObj.TMK_TPK_PVK.value), cmdObj.TMK_TPK_PVK.scheme)
	zmkScheme = KeyScheme(ZMK, schemeZMK)
	cipherTMK_TPK_PVK = zmkScheme.encrypt(clearTMK_TPK_PVK)
	
	tmk_tpk_pvk = KeyScheme(clearTMK_TPK_PVK)
	kcv = hexlify(tmk_tpk_pvk.encrypt("\0\0\0\0\0\0\0\0")).upper()
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.TMK_TPK_PVK = KeyVariable(hexlify(cipherTMK_TPK_PVK).upper(), schemeZMK)
	respObj.CheckValue = DataVariable(kcv[:kcvLength])
	return respObj
