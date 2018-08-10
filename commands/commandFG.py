import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_FG(cmdObj):
	""" Generate a random PIN key and return it to the Host encrypted under a ZMK
		for transmission to another party and under the LMK for storage on the Host
		database."""
	""" Command Pattern:
	    request: Message header + 'FG' + ZMK + Atalla Variant + Delimiter + Key Scheme ZMK + Key Scheme LMK + Key Check Value Type + End message delimiter + Message Trailer
	    response: Message header + 'FH' + Error code + first PVK under ZMK + second PVK under LMK + Check Value + End Message delimiter + Message Trailer
	"""
	
	(schemeZMK, schemeLMK, kcvLength) = extractKeySchemeAndKcvLength(cmdObj)
	clearPVK1 = genRandomKey(Configure.CFG_KEY_LENGTH/2)
	clearPVK2 = genRandomKey(Configure.CFG_KEY_LENGTH/2)
	ZMK = decryptKeyUnderLMK('ZMK', unhexlify(cmdObj.ZMK.value), cmdObj.ZMK.scheme)
	cipherPVKUnderLMK = encryptKeyUnderLMK('PVK', clearPVK2, schemeLMK)
	zmkScheme = KeyScheme(ZMK, schemeZMK)
	cipherPVKUnderZMK = zmkScheme.encrypt(clearPVK1)
	
	pvk1 = KeyScheme(clearPVK1)
	kcv = hexlify(pvk1.encrypt("\0\0\0\0\0\0\0\0")).upper()
	pvk2 = KeyScheme(clearPVK2)
	kcv = hexlify(pvk2.encrypt("\0\0\0\0\0\0\0\0")).upper()
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.PVKUnderZMK = KeyVariable(hexlify(cipherPVKUnderZMK).upper(), schemeZMK)
	respObj.PVKUnderLMK = KeyVariable(hexlify(cipherPVKUnderLMK).upper(), schemeLMK)
	if (kcvLength == Configure.CFG_KCV_LENGTH):
		respObj.CheckValue = DataVariable(kcv1+kcv2)
	else:
		respObj.CheckValue = DataVariable(kcv1[:kcvLength])
	return respObj
