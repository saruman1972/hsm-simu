import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_CA(cmdObj):
	""" Translate a PIN block from encryption under a TPK to encryption under a ZPK
		and from one format to another. If the same PIN block format is defined, only
		the key is translated. """
	""" Command Pattern:
	    request: Message header + 'CA' + Source TPK + Destination ZPK + Maximum PIN Length + Source PIN Block + Source PIN Block Format + Destination PIN Block Format + Account Number + End message delimiter + Message Trailer
	    response: Message header + 'CB' + Error code + PIN Length + Destination PIN Block + Destination PIN Block Format + End Message delimiter + Message Trailer
	"""
	
	SourceTPK = decryptKeyUnderLMK('TPK', unhexlify(cmdObj.SourceTPK.value), cmdObj.SourceTPK.scheme)
	src_tpk = KeyScheme(SourceTPK)
	DestinationZPK = decryptKeyUnderLMK('ZPK', unhexlify(cmdObj.DestinationZPK.value), cmdObj.DestinationZPK.scheme)
	dst_zpk = KeyScheme(DestinationZPK)
	
	src_pinblock = src_tpk.decrypt(unhexlify(cmdObj.SourcePINBlock.value))
	clearPIN = extrackPINFromPINBlock(src_pinblock, cmdObj.AccountNumber.value, cmdObj.SourcePINBlockFormat.value)
	dst_pinblock = genPINBlock(clearPIN, cmdObj.AccountNumber.value, cmdObj.DestinationPINBlockFormat.value)
	dst_pinblock = hexlify(dst_zpk.encrypt(dst_pinblock))
	
	respObj = CommandObj()
	respObj.ResponseCode = DataVariable('00')
	respObj.PINLength = DataVariable("%02d" % len(clearPIN))
	respObj.DestinationPINBlock = DataVariable(dst_pinblock)
	respObj.DestinationPINBlockFormat = DataVariable(cmdObj.DestinationPINBlockFormat.value)
	return respObj
