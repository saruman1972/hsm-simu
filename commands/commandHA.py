import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_HA(cmdObj):
	""" Generate a random key, and encrypt it under a TMK (TPK or PVK) and under
		LMK pair 16-17. """
	""" Command Pattern:
	    request: Message header + 'HA' + TMK + Atalla Variant + Delimiter + Key Scheme TMK + Key Scheme LMK + Key Check Value Type + End message delimiter + Message Trailer
	    response: Message header + 'HB' + Error code + ZPK under ZMK + ZPK under LMK + Check Value + End Message delimiter + Message Trailer
	"""
	
	(schemeTMK, schemeLMK, kcvLength) = extractTMKSchemeAndKcvLength(cmdObj)
	clearZPK = genRandomKey(Configure.CFG_KEY_LENGTH/2)
	TMK = decryptKeyUnderLMK('TMK', unhexlify(cmdObj.TMK.value), cmdObj.TMK.scheme)
	cipherTAKUnderLMK = encryptKeyUnderLMK('TAK', clearTAK, schemeLMK)
	tmkScheme = KeyScheme(TMK, schemeTMK)
	cipherTAKUnderTMK = tmkScheme.encrypt(clearTAK)
	
	tak = KeyScheme(clearTAK)
	kcv = hexlify(tak.encrypt("\0\0\0\0\0\0\0\0")).upper()
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.TAKUnderTMK = KeyVariable(hexlify(cipherTAKUnderTMK).upper(), schemeTMK)
	respObj.TAKUnderLMK = KeyVariable(hexlify(cipherTAKUnderLMK).upper(), schemeLMK)
	respObj.CheckValue = DataVariable(kcv[:kcvLength])
	return respObj
