import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_DA(cmdObj):
	""" Verify a PIN from a local ATM (or PIN pad etc.) using the IBM 3624 method. """
	""" Command Pattern:
	    request: Message header + 'EA' + TPK + PVK + Max PIN Length + PIN Block + PIN Block Format Code + Check length + Account Number + Decimalization Table + PIN Validation data + Offset + End message delimiter + Message Trailer
	    response: Message header + 'EB' + Error code + End Message delimiter + Message Trailer
	"""
	
	TPK = decryptKeyUnderLMK('TPK', unhexlify(cmdObj.TPK.value), cmdObj.TPK.scheme)
	tpk = KeyScheme(TPK)
	pinblock = tpk.decrypt(unhexlify(cmdObj.PINBlock.value))
	enteredPIN = extractPINFromPINBlock(pinblock, cmdObj.AccountNumber.value, cmdObj.PINBlockFormatCode.value)
	if (len(enterdPIN) > string.atoi(cmdObj.MaxPINLength.value)):
		raise ValueError('invalid pin length')
	
	PVK = decryptKeyUnderLMK('PVK', unhexlify(cmdObj.PVK.value), cmdObj.PVK.scheme)
	derivedPIN = genPINUsingIBMMetheod(PVK, cmdObj.AccountNumber.value, cmdObj.PINValidationData.value, cmdObj.DecimalizationTable.value)
	print "PIN=", derivedPIN
	finalPIN = genFinalPIN(derivedPIN, cmdObj.Offset.value)
	
	respObj = CommandObj()
	if (enteredPIN == finalPIN):
		respObj.ResponseCode = DataVariable('00')
	else:
		respObj.ResponseCode = DataVariable('01')
	return respObj
