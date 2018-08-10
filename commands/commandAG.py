import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable, KeyVariable
from Utility import *

def command_AG(cmdObj):
	""" Translate a TAK from encryption under the LMK to encryption under a TMK.
		Used to send a key to a terminal. """
	""" Command Pattern:
	    request: Message header + 'AG' + TMK + TAK + Atalla Variant + Delimiter + Key Scheme TMK + Key Scheme LMK + Key Check Value Type + End message delimiter + Message Trailer
	    response: Message header + 'AH' + Error code + TAK + Check Value + End Message delimiter + Message Trailer
	"""
	
	(schemeTMK, schemeLMK, kcvLength) = extractTMKSchemeAndKcvLength(cmdObj)
	TMK = decryptKeyUnderLMK('TMK', unhexlify(cmdObj.TMK.value), cmdObj.TMK.scheme)
	clearTAK = decryptKeyUnderLMK('TAK', unhexlify(cmdObj.TAK.value), cmdObj.TAK.scheme)
	tmkScheme = KeyScheme(TMK, schemeTMK)
	cipherTAK = tmkScheme.encrypt(clearTAK)
	
	tak = KeyScheme(clearTAK)
	kcv = hexlify(tak.encrypt("\0\0\0\0\0\0\0\0")).upper()
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.TAK = KeyVariable(hexlify(cipherTAK).upper(), schemeTMK)
	respObj.CheckValue = DataVariable(kcv[:kcvLength])
	return respObj
