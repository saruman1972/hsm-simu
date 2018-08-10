#!/usr/bin/python
# -*- coding: gbk -*-

import re
import string
import random
from binascii import *
import pyDes
import Configure
from Command import CommandObj

def padding(var, pad_len, pad_char):
    length = len(var)
    var += pad_char*(pad_len-length)
    return var

def blockXOR(d1, d2, blockLen=8):
    buf = ""
    for i in range(blockLen):
        buf += chr(ord(d1[i]) ^ ord(d2[i]))
    return buf

def binval(hex_char):
    hex_char.lower()
    val = ord(hex_char)
    if (val > 0x39):
        val = val - ord('a') + 10
    else:
        val -= ord('0')
    return val

def asc2dec(ascChar):
    decVal = ord(ascChar) - ord('0')
    return decVal

def dec2asc(dec):
    ascChar = chr(dec + ord('0'))
    return ascChar

def decryptPINUnderLMK(cypherPIN, acctno):
    """ under LMK 02,03 pair """
    lmkFunc = Configure.LMKFunction['PIN']
    pair = lmkFunc['PAIR']
    lmk = pyDes.triple_des(unhexlify(Configure.LMK[pair[0]] + Configure.LMK[pair[1]]))
    avalue = unhexlify(acctno + '0000')
    c = lmk.encrypt(avalue)

    PIN = ""
    for i in range(Configure.CFG_PIN_LENGTH-1):
        if (i == 0):
#            PIN += chr(((((ord(cypherPIN[i]) - ord('0')) - (ord(c[i]) % 10)) + 10) % 10) + ord('0'))
            PIN += dec2asc(((asc2dec(cypherPIN[i]) - (ord(c[i]) % 10)) + 10) % 10)
        else:
#            PIN += chr(((((ord(cypherPIN[i]) - ord('0')) - ((ord(c[i]) + ord(cypherPIN[i-1])) % 10)) + 10) % 10) + ord('0'))
            PIN += dec2asc(((asc2dec(cypherPIN[i]) - ((ord(c[i]) + ord(cypherPIN[i-1])) % 10)) + 10) % 10)

    return PIN

def encryptPINUnderLMK(PIN, acctno):
    """ under LMK 02,03 pair """
    lmkFunc = Configure.LMKFunction['PIN']
    pair = lmkFunc['PAIR']
    lmk = pyDes.triple_des(unhexlify(Configure.LMK[pair[0]] + Configure.LMK[pair[1]]))
    avalue = unhexlify(acctno + '0000')
    c = lmk.encrypt(avalue)

    cypherPIN = ""
    for i in range(Configure.CFG_PIN_LENGTH-1):
        if (i == 0):
#            cypherPIN += chr(((((ord(PIN[i]) - ord('0')) + (ord(c[i]) % 10)) + 10) % 10) + ord('0'))
            cypherPIN += dec2asc(((asc2dec(PIN[i]) + (ord(c[i]) % 10)) + 10) % 10)
        else:
            cypherPIN += chr(((((ord(PIN[i]) - ord('0')) + ((ord(c[i]) + ord(cypherPIN[i-1])) % 10)) + 10) % 10) + ord('0'))
#            cypherPIN += dec2asc(((asc2dec(PIN[i]) + ((ord(c[i]) + ord(cypherPIN[i-1])) % 10)) + 10) % 10)

    return cypherPIN

def genPINUsingIBMMetheod(PVK, AccountNumber, PINValidationData, DecimalizationTable):
    print AccountNumber,PINValidationData,DecimalizationTable
    if (len(PVK) == 8):
        key = pyDes.des(PVK)
    else:
        key = pyDes.triple_des(PVK)

    if Configure.CFG_PIN_VALIDATION_DATA == 'LAST5':
        last5 = AccountNumber[-5:]
        validation = PINValidationData
        validation = re.sub('N', last5, validation)
    else:
        validation = re.sub('N', Configure.CFG_PIN_VALIDATION_DATA, PINValidationData)
    print "validation=",validation
    val = hexlify(key.encrypt(unhexlify(validation)))
    print "val=",val
    result = ""
    for digit in val:
        index = binval(digit)
        result += DecimalizationTable[index]

    print "pin result=", result
    PIN = result[:Configure.CFG_PIN_LENGTH-1]
    return PIN

def genFinalPIN(PIN, Offset):
    finalPIN = ""
    for i in range(Configure.CFG_PIN_LENGTH-1):
#        finalPIN += chr((((ord(PIN[i]) - ord('0')) + (ord(Offset[i]) - ord('0'))) % 10) + ord('0'))
        finalPIN += dec2asc((asc2dec(PIN[i]) + asc2dec(Offset[i])) % 10)
    return finalPIN

def genOffset(PIN, finalPIN):
    Offset = ""
    for i in range(Configure.CFG_PIN_LENGTH-1):
#        Offset += chr(((10 + (ord(finalPIN[i]) - ord('0')) - (ord(PIN[i]) - ord('0'))) % 10) + ord('0'))
        Offset += dec2asc((10 + asc2dec(finalPIN[i]) - asc2dec(PIN[i])) % 10)
    Offset = padding(Offset, 12, 'F')
    return Offset

class PINBlockFormat:
    def __init__(self): pass
    def genPINData(self, PIN): pass
    def genSerialData(self, AccountNumber): pass
    def genPINBlock(self, PIN, AccountNumber): pass
    def extractPINFromPINBlock(self, PINBlock, AccountNumber): pass

class PINBlockFormat01(PINBlockFormat):
    def genPINData(self, PIN):
        pinData = "%02d%s" % (len(PIN), PIN)
        return padding(pinData, 16, 'F')
    def genSerialData(self, AccountNumber):
        return ('0000' + AccountNumber)
    def genPINBlock(self, PIN, AccountNumber):
        pinData = self.genPINData(PIN)
        serialData = self.genSerialData(AccountNumber)
        return blockXOR(unhexlify(pinData), unhexlify(serialData))
    def extractPINFromPINBlock(self, PINBlock, AccountNumber):
        serialData = self.genSerialData(AccountNumber)
        pinData = hexlify(blockXOR(PINBlock, unhexlify(serialData)))
        pinLen = string.atoi(pinData[:2])
        return pinData[2:pinLen+2]

class PINBlockFormat02(PINBlockFormat):
    def genPINData(self, PIN):
        pinData = padding(PIN, 6, '0')
        return padding(pinData, 16, '0')
    def genPINBlock(self, PIN, AccountNumber):
        pinData = self.genPINData(PIN)
        return unhexlify(pinData)
    def extractPINFromPINBlock(self, PINBlock, AccountNumber):
        pinData = hexlify(PINBlock)
        return pinData[:6]

class PINBlockFormat03(PINBlockFormat):
    def genPINData(self, PIN):
        pinData = padding(PIN, 6, 'F')
        return padding(pinData, 16, 'F')
    def genPINBlock(self, PIN, AccountNumber):
        pinData = self.genPINData(PIN)
        return unhexlify(pinData)
    def extractPINFromPINBlock(self, PINBlock, AccountNumber):
        pinData = hexlify(PINBlock)
        return pinData[:6]

class PINBlockFormat04(PINBlockFormat01):
    pass

class PINBlockFormat08(PINBlockFormat01):
    def genSerialData(self, AccountNumber):
        return '0000000000000000'

PINBlockFormatMap = {
    '01' : PINBlockFormat01(),
    '02' : PINBlockFormat02(),
    '03' : PINBlockFormat03(),
    '04' : PINBlockFormat04(),
    '08' : PINBlockFormat08()
}

def extrackPINFromPINBlock(PINBlock, AccountNumber, PINBlockFormatCode):
    try:
        format = PINBlockFormatMap[PINBlockFormatCode]
    except:
        return (None, '23')
    try:
        return (format.extractPINFromPINBlock(PINBlock, AccountNumber), '00')
    except:
        return (None, '20')

def genPINBlock(PIN, AccountNumber, PINBlockFormatCode):
    format = PINBlockFormatMap[PINBlockFormatCode]
    return format.genPINBlock(PIN, AccountNumber)

def genCVV(PrimaryAccountNumber, ExpirationDate, ServiceCode, CVK_A, CVK_B):
    # step2 data block
    block1 = PrimaryAccountNumber
    length = len(block1)
    if (length > 16):
        raise ValueError('primary Account Number [' + PrimaryAccountNumber + '] is too long')
    elif (length < 16):
        block1 = padding(block1, 16, '0')
    block2 = ExpirationDate + ServiceCode
    block2 = padding(block2, 16, '0')
    # step3 encrypt block1 using CVKA
    keyA = pyDes.des(CVK_A)
    result3 = keyA.encrypt(unhexlify(block1))
    # step4: block2 XOR result3, then encrypt using CVKA
    xor = blockXOR(unhexlify(block2), result3)
    result4 = keyA.encrypt(xor)
    print "result4="+hexlify(result4)+"\n"
    # step5: decrypt using CVKB
    keyB = pyDes.des(CVK_B)
    result5 = keyB.decrypt(result4)
    # step6: encrypt using CVKA
    result6 = hexlify(keyA.encrypt(result5))
    # step7: extract digit from result6
    result7 = re.sub('[a-fA-F]', '', result6)
    # step8: extract hex from result6, and translate into digit by subtracting 10
    hexs = re.sub('[0-9]', '', result6)
    hexs.lower()
    result8 = ""
    for ch in hexs:
        val = binval(ch)
        result8 += chr(val-10+ord('0'))
    # step9: concatenate result7 and result8
    result9 = result7 + result8
    # step10: the starting 3 digit of result9 be CVV
    CVV = result9[:3]

    return CVV

def genKeyCheckValue(KEY, KCVLen):
    if (len(KEY) == 8):    # single length key
        key = pyDes.des(KEY)
        data = '0'*8
    elif (len(KEY) == 16):    # double length key
        key = pyDes.triple_des(KEY)
        data = '0'*16
    elif (len(KEY) == 24):    # triple length key
        raise ValueError('triple length key not support')
    KCV = hexlify(key.encrypt(data))
    return KCV[:KCVLen]

class KeyVariant:
    def __init__(self, encryptingKEY):
        self.encryptingKEY = encryptingKEY
    def decrypt(self): pass
    def encrypt(self): pass

class LMKVariant(KeyVariant):
    """ used for LMK variant """
    def __init__(self, encryptingKEY, variantIndex):
        KeyVariant.__init__(self, encryptingKEY)
        self.variantIndex = variantIndex

        # XOR add the first byte of the LMK pair
        firstByte = chr(ord(encryptingKEY[0]) ^ Configure.LMKVariantTable[variantIndex])
        # Replace the left-most byte of the LMK pair with the result of last Step  and use the resulting key as the specified Variant:
        encryptingKeyVariant = firstByte + encryptingKEY[1:]
        self.encryptingKeyVariant = pyDes.triple_des(encryptingKeyVariant)
    def encrypt(self, KEY):
        return self.encryptingKeyVariant.encrypt(KEY)
    def decrypt(self, KEY):
        return self.encryptingKeyVariant.decrypt(KEY)

class DoubleLengthKeyVariant(KeyVariant):
    def __init__(self, encryptingKEY):
        if (len(encryptingKEY) != 16):
            raise ValueError('key length error')
        KeyVariant.__init__(self, encryptingKEY)

        firstByteOfRightHalf = chr(ord(encryptingKEY[8]) ^ 0xA6)
        encryptingKeyLeft = encryptingKEY[:8] + firstByteOfRightHalf + encryptingKEY[9:]
        self.encryptingKeyLeft = pyDes.triple_des(encryptingKeyLeft)
        firstByteOfRightHalf = chr(ord(encryptingKEY[8]) ^ 0x5A)
        encryptingKeyRight = encryptingKEY[:8] + firstByteOfRightHalf + encryptingKEY[9:]
        self.encryptingKeyRight = pyDes.triple_des(encryptingKeyRight)
    def encrypt(self, KEY):
        return self.encryptingKeyLeft.encrypt(KEY[:8]) + self.encryptingKeyRight.encrypt(KEY[8:])
    def decrypt(self, KEY):
        return self.encryptingKeyLeft.decrypt(KEY[:8]) + self.encryptingKeyRight.decrypt(KEY[8:])

class TripleLengthKeyVariant(KeyVariant):
    def __init__(self, encryptingKEY):
        if (len(encryptingKEY) != 24):
            raise ValueError('key length error')
        KeyVariant.__init__(self, encryptingKEY)

        firstByteOfRightHalf = chr(ord(encryptingKEY[8]) ^ 0x6A)
        encryptingKeyLeft = encryptingKEY[:8] + firstByteOfRightHalf + encryptingKEY[9:]
        self.encryptingKeyLeft = pyDes.triple_des(encryptingKeyLeft)

        firstByteOfRightHalf = chr(ord(encryptingKEY[8]) ^ 0xDE)
        encryptingKeyMiddle = encryptingKEY[:8] + firstByteOfRightHalf + encryptingKEY[9:]
        self.encryptingKeyMiddle = pyDes.triple_des(encryptingKeyMiddle)

        firstByteOfRightHalf = chr(ord(encryptingKEY[8]) ^ 0x2B)
        encryptingKeyRight = encryptingKEY[:8] + firstByteOfRightHalf + encryptingKEY[9:]
        self.encryptingKeyRight = pyDes.triple_des(encryptingKeyRight)
    def encrypt(self, KEY):
        return self.encryptingKeyLeft.encrypt(KEY[:8]) + self.encryptingKeyRight.encrypt(KEY[8:16]) + self.encryptingKeyRight.encrypt(KEY[16:])
    def decrypt(self, KEY):
        return self.encryptingKeyLeft.decrypt(KEY[:8]) + self.encryptingKeyRight.decrypt(KEY[8:16]) + self.encryptingKeyRight.decrypt(KEY[16:])

def decryptKeyUnderLMK(keyName, KEY, scheme=''):
    lmkFunc = Configure.LMKFunction[keyName]
    pair = lmkFunc['PAIR']
    # LMK are all double length
    lmk = unhexlify(Configure.LMK[pair[0]] + Configure.LMK[pair[1]])
    if (lmkFunc['VARIANT'] == True):
        variantIndex = string.atoi(lmkFunc['KEY_TYPE'][0])
        key = LMKVariant(lmk, variantIndex)
    elif (scheme == 'U') or (scheme == 'T'):
        if (len(KEY) == 8):    # single length key, not variation
            key = pyDes.triple_des(lmk)
        elif (len(KEY) == 16):    # double length key
            key = DoubleLengthKeyVariant(lmk)
        elif (len(KEY) == 24):    # triple length key
            key = TripleLengthKeyVariant(lmk)
        else:
            raise ValueError('key length error')
    else:    # no variant
        key = pyDes.triple_des(lmk)
    clearKEY = key.decrypt(KEY)

    return clearKEY

def encryptKeyUnderLMK(keyName, KEY, scheme=''):
    lmkFunc = Configure.LMKFunction[keyName]
    pair = lmkFunc['PAIR']
    # LMK are all double length
    lmk = unhexlify(Configure.LMK[pair[0]] + Configure.LMK[pair[1]])
    if (lmkFunc['VARIANT'] == True):
        variantIndex = string.atoi(lmkFunc['KEY_TYPE'][0])
        key = LMKVariant(lmk, variantIndex)
    elif (scheme == 'U') or (scheme == 'T'):
        if (len(KEY) == 8):    # single length key, not variation
            key = pyDes.triple_des(lmk)
        elif (len(KEY) == 16):    # double length key
            key = DoubleLengthKeyVariant(lmk)
        elif (len(KEY) == 24):    # triple length key
            key = TripleLengthKeyVariant(lmk)
        else:
            raise ValueError('key length error')
    else:    # no variant
        key = pyDes.triple_des(lmk)
    cipherKEY = key.encrypt(KEY)

    return cipherKEY

class KeyScheme:
    def __init__(self, encryptingKEY, scheme=''):
        self.encryptingKEY = encryptingKEY
        self.scheme = scheme
        if (scheme == 'Z'):
            if (len(encryptingKEY) != 8):
                raise ValueError('key length error')
            self.key = pyDes.des(encryptingKEY)
        elif (scheme == 'U'):
            if (len(encryptingKEY) != 16):
                raise ValueError('key length error')
            self.key = DoubleLengthKeyVariant(encryptingKEY)
        elif (scheme == 'T'):
            if (len(encryptingKEY) != 24):
                raise ValueError('key length error')
            self.key = TripleLengthKeyVariant(encryptingKEY)
        elif (scheme == 'X'):
            if (len(encryptingKEY) != 16):
                raise ValueError('key length error')
            self.key = pyDes.triple_des(encryptingKEY)
        elif (scheme == 'Y'):
            if (len(encryptingKEY) != 24):
                raise ValueError('key length error')
            self.key = pyDes.triple_des(encryptingKEY)
        else:    # use default scheme(no variant)
            if (len(encryptingKEY) == 8):
                self.key = pyDes.des(encryptingKEY)
            elif (len(encryptingKEY) == 16) or (len(encryptingKEY) == 24):
                self.key = pyDes.triple_des(encryptingKEY)
            else:
                raise ValueError('key length error')

    def encrypt(self, KEY):
        return self.key.encrypt(KEY)

    def decrypt(self, KEY):
        return self.key.decrypt(KEY)


def calcMAC(key, data, initial_value):
    print "key=%s,initial_value=%s,macBlock=%s" % (hexlify(key),hexlify(initial_value),hexlify(data))
    if len(key) > 8:
        k = pyDes.des(key[:8])
        kFinal = pyDes.des(key[8:16])
        print "use triple des"
    elif len(key) == 16 or len(key) == 24:
        k = pyDes.des(key)
        print "use single des"
    else:
        raise ValueError('key length error')
    length = len(data)
    r = length % 8
    b = length / 8
    if (r != 0):
        b = b + 1
        data += "\0" * (8-r)
        print "remain=%d" % (r)
    print data + "!!!!!"
    mac = initial_value
    for i in range(b):
        blk = data[i*8 : (i+1)*8]
        t = blockXOR(mac, blk)
        mac = k.encrypt(t)
        print "mac=%s(block=%s)" % (hexlify(mac), hexlify(blk))
    if len(key) > 8:
        mac = kFinal.decrypt(mac)
        print "last mac=%s" % (hexlify(mac))
        mac = k.encrypt(mac)
        print "last mac=%s" % (hexlify(mac))
    return mac

def genRandomKey(keyLength):
    if keyLength not in (8,16,24):
        raise ValueError('key length error')
    rand = random.Random()
    digitSet = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    key = ''
    for i in range(keyLength*2):
        key += rand.choice(digitSet)
    clearKey = unhexlify(key)
    return clearKey

def extractKeySchemeAndKcvLength(cmdObj):
    """ 得到ZMK LMK的scheme """
    if cmdObj.__dict__.has_key('KeySchemeZMK'):
        schemeZMK = cmdObj.KeySchemeZMK.value
    else:
        schemeZMK = ''

    if cmdObj.__dict__.has_key('KeySchemeLMK'):
        schemeLMK = cmdObj.KeySchemeLMK.value
    else:
        schemeLMK = ''

    if cmdObj.__dict__.has_key('KeyCheckValueType'):
        kcvType = cmdObj.KeyCheckValueType.value
    else:
        kcvType = '0'
    if (kcvType == '0'):
        kcvLength = Configure.CFG_KCV_LENGTH
    elif (kcvType == '1'):
        kcvLength = 6
    else:
        raise ValueError('Key Check Value Type error [' + kcvType + ']')

    return (schemeZMK, schemeLMK, kcvLength)

def extractTMKSchemeAndKcvLength(cmdObj):
    """ 得到TMK LMK的scheme """
    if cmdObj.__dict__.has_key('KeySchemeTMK'):
        schemeTMK = cmdObj.KeySchemeTMK.value
    else:
        schemeTMK = ''

    if cmdObj.__dict__.has_key('KeySchemeLMK'):
        schemeLMK = cmdObj.KeySchemeLMK.value
    else:
        schemeLMK = ''

    if cmdObj.__dict__.has_key('KeyCheckValueType'):
        kcvType = cmdObj.KeyCheckValueType.value
    else:
        kcvType = '0'
    if (kcvType == '0'):
        kcvLength = Configure.CFG_KCV_LENGTH
    elif (kcvType == '1'):
        kcvLength = 6
    else:
        raise ValueError('Key Check Value Type error [' + kcvType + ']')

    return (schemeTMK, schemeLMK, kcvLength)

def padDataBlock(data, moduler=8):
    """ padding data to 8bytes block to calc MAC..."""
    data += chr(0x80)
    remain = len(data) % moduler
    if remain > 0:
        padLen = moduler - remain
        data += '\x00' * padLen
    return data

def icKeyDerivation(mk, pan, pan_sn):
    print "mk=" + hexlify(mk)
    k = pyDes.triple_des(mk)
    data = pan + pan_sn
    if len(data) >= 16:
        data = data[-16:]
    else:
        padLen = 16 - len(data) % 16
        data = '0' * padLen + data
    data = unhexlify(data)
    r = blockXOR(data, '\xFF'*8)
    return k.encrypt(data) + k.encrypt(r)

def icSessionKey(udk, atc):
    k = pyDes.triple_des(udk)
    l = '\x00' * 6 + atc
    r = '\x00' * 6 + blockXOR(atc, '\xFF\xFF', 2)
    print "l="+hexlify(l)+"\n"
    print "r="+hexlify(r)+"\n"
    return k.encrypt(l) + k.encrypt(r)

def generateARPC(mk, pan, pan_sn, atc, arqc, resp_cd):
    print "ARPC:mk="+hexlify(mk)+",arqc="+hexlify(arqc)+",atc="+hexlify(atc)+"resp_cd="+resp_cd
    sessionKey = icSessionKey(icKeyDerivation(mk, pan, pan_sn), atc)
    print "sessionKey="+hexlify(sessionKey)
    k = pyDes.triple_des(sessionKey)
    arpc =  k.encrypt(blockXOR(arqc, resp_cd+'\x00\x00\x00\x00\x00\x00'))
    print "ARPC="+hexlify(arpc)
    return arpc


def main():
    key = encryptKeyUnderLMK("CVK", unhexlify("0123456789abcdef0123456789abcdef"), "")
    print hexlify(key)

if __name__ == "__main__":
    main()
