import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_GC(cmdObj):
	""" Translate a ZPK from encryption under the LMK to encryption under a ZMK.
		Used to transmit a ZPK to another party. """
	""" Command Pattern:
	    request: Message header + 'GC' + ZMK + ZPK + Atalla Variant + Delimiter + Key Scheme ZMK + Key Scheme LMK + Key Check Value Type + End message delimiter + Message Trailer
	    response: Message header + 'GD' + Error code + ZPK + Check Value + End Message delimiter + Message Trailer
	"""
	
	(schemeZMK, schemeLMK, kcvLength) = extractKeySchemeAndKcvLength(cmdObj)
	ZMK = decryptKeyUnderLMK('ZMK', unhexlify(cmdObj.ZMK.value), cmdObj.ZMK.scheme)
	clearZPK = decryptKeyUnderLMK('ZPK', unhexlify(cmdObj.ZPK.value), cmdObj.ZPK.scheme)
	zmkScheme = KeyScheme(ZMK, schemeZMK)
	cipherZPK = zmkScheme.encrypt(clearZPK)
	
	zpk = KeyScheme(clearZPK)
	kcv = hexlify(zpk.encrypt("\0\0\0\0\0\0\0\0")).upper()
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.ZPK = KeyVariable(hexlify(cipherZPK).upper(), schemeZMK)
	respObj.CheckValue = DataVariable(kcv[:kcvLength])
	return respObj
