import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_JC(cmdObj):
	""" Translate a PIN from encryption under a TPK to encryption under the LMK. """
	""" Command Pattern:
	    request: Message header + 'JC' + TPK + PIN Block + PIN Block Format Code + Account Number + End message delimiter + Message Trailer
	    response: Message header + 'JD' + Error code + PIN + End Message delimiter + Message Trailer
	"""
	
	TPK = decryptKeyUnderLMK('TPK', unhexlify(cmdObj.TPK.value), cmdObj.TPK.scheme)
	tpk = KeyScheme(TPK)
	pinblock = tpk.decrypt(unhexlify(cmdObj.PINBlock.value))
	clearPIN = extrackPINFromPINBlock(pinblock, cmdObj.AccountNumber.value, cmdObj.PINBlockFormatCode.value)
	cipherPIN = encryptPINUnderLMK(clearPIN, cmdObj.AccountNumber.value)	
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.PIN = DataVariable(cipherPIN)
	return respObj
