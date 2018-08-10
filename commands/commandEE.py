import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_EE(cmdObj):
	""" Derive a PIN Using IBM Method """
	""" Command Pattern:
	    request: Message header + 'EE' + PVK + Offset + Check length + Account Number + Decimalization Table + PIN Validation data + End message delimiter + Message Trailer
	    response: Message header + 'EF' + Error code + PIN + End Message delimiter + Message Trailer
	"""
	PVK = decryptKeyUnderLMK('PVK', unhexlify(cmdObj.PVK.value), cmdObj.PVK.scheme)
	PIN = genPINUsingIBMMetheod(PVK, cmdObj.AccountNumber.value, cmdObj.PINValidationData.value, cmdObj.DecimalizationTable.value)
	finalPIN = genFinalPIN(PIN, cmdObj.Offset.value)
	cypherPIN = encryptPINUnderLMK(finalPIN, cmdObj.AccountNumber.value)
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.PIN = DataVariable(cypherPIN)
	return respObj
