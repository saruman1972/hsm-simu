import re
from binascii import *
import pyDes
import Configure
from Command import CommandObj, DataVariable
from Utility import *

def command_EA(cmdObj):
    """ Verify a PIN from interchange using the IBM 3624 method. """
    """ Command Pattern:
        request: Message header + 'EA' + ZPK + PVK + Max PIN Length + PIN Block + PIN Block Format Code + Check length + Account Number + Decimalization Table + PIN Validation data + Offset + End message delimiter + Message Trailer
        response: Message header + 'EB' + Error code + End Message delimiter + Message Trailer
    """

    respObj = CommandObj()

    ZPK = decryptKeyUnderLMK('ZPK', unhexlify(cmdObj.ZPK.value), cmdObj.ZPK.scheme)
    zpk = KeyScheme(ZPK)
    pinblock = zpk.decrypt(unhexlify(cmdObj.PINBlock.value))
    (enteredPIN,rslt) = extrackPINFromPINBlock(pinblock, cmdObj.AccountNumber.value, cmdObj.PINBlockFormatCode.value)
    if rslt != '00':
        respObj.ResponseCode = DataVariable(rslt)
        return respObj
    print "enteredPIN=", enteredPIN
    if (len(enteredPIN) < string.atoi(cmdObj.CheckLength.value)) or (len(enteredPIN) > string.atoi(cmdObj.MaxPINLength.value)):
        respObj.ResponseCode = DataVariable('24')
        return respObj

    PVK = decryptKeyUnderLMK('PVK', unhexlify(cmdObj.PVK.value), cmdObj.PVK.scheme)
    derivedPIN = genPINUsingIBMMetheod(PVK, cmdObj.AccountNumber.value, cmdObj.PINValidationData.value, cmdObj.DecimalizationTable.value)
    print "PIN=", derivedPIN
    finalPIN = genFinalPIN(derivedPIN, cmdObj.Offset.value)

    if (enteredPIN == finalPIN):
        respObj.ResponseCode = DataVariable('00')
    else:
        respObj.ResponseCode = DataVariable('01')
    return respObj
