import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_FC(cmdObj):
	""" Translate a TMK, TPK or PVK from encryption under a ZMK to encryption
		under the LMK. """
	""" Command Pattern:
	    request: Message header + 'FC' + ZMK + TMK_TPK_PVK + Atalla Variant + Delimiter + Key Scheme ZMK + Key Scheme LMK + Key Check Value Type + End message delimiter + Message Trailer
	    response: Message header + 'FD' + Error code + TMK_TPK_PVK + Check Value + End Message delimiter + Message Trailer
	"""
	
	(schemeZMK, schemeLMK, kcvLength) = extractKeySchemeAndKcvLength(cmdObj)
	ZMK = decryptKeyUnderLMK('ZMK', unhexlify(cmdObj.ZMK.value), cmdObj.ZMK.scheme)
	tmk_tpk_pvkScheme = KeyScheme(ZMK, cmdObj.TMK_TPK_PVK.scheme)
	clearTMK_TPK_PVK = tmk_tpk_pvkScheme.decrypt(unhexlify(cmdObj.TMK_TPK_PVK.value))
	
	cipherTMK_TPK_PVK = encryptKeyUnderLMK('PVK', clearTMK_TPK_PVK, schemeLMK)
	tmk_tpk_pvk = KeyScheme(clearTMK_TPK_PVK)
	kcv = hexlify(tmk_tpk_pvk.encrypt("\0\0\0\0\0\0\0\0")).upper()
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.TMK_TPK_PVK = KeyVariable(hexlify(cipherTMK_TPK_PVK).upper(), schemeLMK)
	respObj.CheckValue = DataVariable(kcv[:kcvLength])
	return respObj
