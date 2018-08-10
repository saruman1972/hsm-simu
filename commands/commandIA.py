import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_IA(cmdObj):
	""" Generate a random PIN key and return it to the Host encrypted under a ZMK
		for transmission to another party and under the LMK for storage on the Host
		database."""
	""" Command Pattern:
	    request: Message header + 'IA' + ZMK + Atalla Variant + Delimiter + Key Scheme ZMK + Key Scheme LMK + Key Check Value Type + End message delimiter + Message Trailer
	    response: Message header + 'IB' + Error code + ZPK under ZMK + ZPK under LMK + Check Value + End Message delimiter + Message Trailer
	"""
	
	(schemeZMK, schemeLMK, kcvLength) = extractKeySchemeAndKcvLength(cmdObj)
	clearZPK = genRandomKey(Configure.CFG_KEY_LENGTH/2)
	ZMK = decryptKeyUnderLMK('ZMK', unhexlify(cmdObj.ZMK.value), cmdObj.ZMK.scheme)
	cipherZPKUnderLMK = encryptKeyUnderLMK('ZPK', clearZPK, schemeLMK)
	zmkScheme = KeyScheme(ZMK, schemeZMK)
	cipherZPKUnderZMK = zmkScheme.encrypt(clearZPK)
	
	zpk = KeyScheme(clearZPK)
	kcv = hexlify(zpk.encrypt("\0\0\0\0\0\0\0\0")).upper()
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.ZPKUnderZMK = KeyVariable(hexlify(cipherZPKUnderZMK).upper(), schemeZMK)
	respObj.ZPKUnderLMK = KeyVariable(hexlify(cipherZPKUnderLMK).upper(), schemeLMK)
	respObj.CheckValue = DataVariable(kcv[:kcvLength])
	return respObj
