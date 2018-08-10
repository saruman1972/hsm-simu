import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_BA(cmdObj):
	""" Encrypt a clear text PIN. """
	""" Command Pattern:
	    request: Message header + 'NG' + PIN + Account Number + End message delimiter + Message Trailer
	    response: Message header + 'NH' + Error code + PIN + End Message delimiter + Message Trailer
	"""

	PIN = encryptPINUnderLMK(cmdObj.PIN.value, cmdObj.AccountNumber.value)
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.PIN = DataVariable(PIN)
	return respObj
