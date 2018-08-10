import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_NG(cmdObj):
	""" Decrypted an encrypted PIN and return a reference number. """
	""" Command Pattern:
	    request: Message header + 'NG' + Account Number + PIN + End message delimiter + Message Trailer
	    response: Message header + 'NH' + Error code + PIN + End Message delimiter + Message Trailer
	"""

	PIN = decryptPINUnderLMK(cmdObj.PIN.value, cmdObj.AccountNumber.value)
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.PIN = DataVariable(PIN)
	return respObj
