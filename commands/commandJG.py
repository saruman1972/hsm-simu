import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_JG(cmdObj):
	""" Translate a PIN from encryption under a ZPK to encryption under the LMK. """
	""" Command Pattern:
	    request: Message header + 'JG' + ZPK + PIN Block Format Code + Account Number + PIN + End message delimiter + Message Trailer
	    response: Message header + 'JH' + Error code + PIN Block + End Message delimiter + Message Trailer
	"""
	
	ZPK = decryptKeyUnderLMK('ZPK', unhexlify(cmdObj.ZPK.value), cmdObj.ZPK.scheme)
	zpk = KeyScheme(ZPK)
	clearPIN = decryptPINUnderLMK(cmdObj.PIN.value, cmdObj.AccountNumber.value)	
	pinblock = genPINBlock(clearPIN, cmdObj.AccountNumber.value, cmdObj.PINBlockFormatCode.value)
	pinblock = zpk.encrypt(pinblock)
	pinblock = hexlify(pinblock)
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.PINBlock = DataVariable(pinblock.upper())
	return respObj
