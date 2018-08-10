import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_DE(cmdObj):
	""" Generate a PIN offset using the IBM method. """
	""" Command Pattern:
	    request: Message header + 'EE' + PVK + PIN + Check length + Account Number + Decimalization Table + PIN Validation data + End message delimiter + Message Trailer
	    response: Message header + 'EF' + Error code + Offset + End Message delimiter + Message Trailer
	"""
	PVK = decryptKeyUnderLMK('PVK', unhexlify(cmdObj.PVK.value), cmdObj.PVK.scheme)
	PIN = genPINUsingIBMMetheod(PVK, cmdObj.AccountNumber.value, cmdObj.PINValidationData.value, cmdObj.DecimalizationTable.value)
	print "PIN=", PIN
	clearPIN = decryptPINUnderLMK(cmdObj.PIN.value, cmdObj.AccountNumber.value)
	Offset = genOffset(PIN, clearPIN)
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.Offset = DataVariable(Offset)
	return respObj
