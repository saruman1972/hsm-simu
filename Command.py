#!/usr/bin/python
# -*- coding: gbk -*-

from xml.sax import *
import string
import re
from binascii import *
from ListFile import listFiles
import Configure


class PresentCondition:
    def __init__(self, element_name):
        self.element_name = element_name
        self.values = []

    def addConditionValue(self, value):
        self.values.append(value)

    def conditionSatisfied(self, cmdObj):
        raise ValueError('abstract base class')

class PresentConditionOnValue(PresentCondition):
    """ 根据前一个element的值来确定是否出现 """
    def __init__(self, element_name):
        PresentCondition.__init__(self, element_name)

    def addConditionValue(self, value):
        self.values.append(value)

    def conditionSatisfied(self, cmdObj):
        var = cmdObj.__dict__[self.element_name]
        for value in self.values:
            if var.value == value:
                return True
        return False

class PresentConditionOnPresentation(PresentCondition):
    """ 根据前一个element是否出现来确定是否出现 """
    def __init__(self, element_name):
        PresentCondition.__init__(self, element_name)

    def addConditionValue(self, value):
        self.values.append(value)

    def conditionSatisfied(self, cmdObj):
        if cmdObj.__dict__.has_key(self.element_name):
            return True
        else:
            return False

class PresentConditionOnNotNull(PresentCondition):
    """ 根据前一个element值是否为空来确定是否出现 """
    def __init__(self, element_name):
        PresentCondition.__init__(self, element_name)

    def addConditionValue(self, value):
        self.values.append(value)

    def conditionSatisfied(self, cmdObj):
        var = cmdObj.__dict__[self.element_name]
        if var.value == '':
            return False
        else:
            return True

class AlwaysPresent(PresentCondition):
    def __init__(self):
        PresentCondition.__init__(self, '')

    def conditionSatisfied(self, cmdObj=None):
        return True

class AlwaysAbsent(PresentCondition):
    def __init__(self):
        PresentCondition.__init__(self, '')

    def conditionSatisfied(self, cmdObj=None):
        return False

ALWAYS_PRESENT = AlwaysPresent()
ALWAYS_ABSENT  = AlwaysAbsent()


class DataVariable:
    """ 实际从报文中截取出来的变量 """
    def __init__(self, value=''):
        self.value = value

    def __str__(self):
        return self.value

    def pack(self):
        return self.value

class KeyVariable(DataVariable):
    """ 实际从报文中截取出来的KEY """
    def __init__(self, key, scheme=''):
        DataVariable.__init__(self, key)
        self.scheme = scheme
        if (scheme == ''):
            if (len(key) == 16*2):
                self.scheme = 'X'
            elif (len(key) == 24*2):
                self.scheme = 'Y'

    def __str__(self):
        return self.value

    def pack(self):
        return self.scheme + self.value

class DataField:
    """ 数据域的定义（从配置文件中读取） """
    def __init__(self, name="", coder=None, size=0):
        self.name = name
        self.coder = coder
        self.size = size
        self.present_condition = ALWAYS_PRESENT

    def encode(self, var, cmdObj):
        return var.pack()

    def decode(self, buffer, cmdObj):
        var = buffer[:self.size]
        return (DataVariable(var), self.size)

class KeyField(DataField):
    def __init__(self, name="", coder=None, size=Configure.CFG_KEY_LENGTH):
        DataField.__init__(self, name, coder, size)

    def encode(self, var, cmdObj):
        return var.pack()

    def decode(self, buffer, cmdObj):
        length = 0
        scheme = buffer[0].upper()
        scheme_length = 0
        if (re.match('[0-9A-F]', scheme) != None):
            # previously specified sheme
            length = self.size
            scheme = ''
        elif ((scheme == 'K') or (scheme == 'S')):
            # previously specified sheme
            length = self.size
        elif (scheme == 'X'):
            # Double length DES keys
            scheme_length = 1
            length = 16*2
        elif (scheme == 'Y'):
            # Triple length DES keys
            scheme_length = 1
            length = 16*3
        elif (scheme == 'Z'):
            # Single Length under ZMK/LMK
            scheme_length = 1
            length = 16
        elif (scheme == 'U'):
            # Double Length under ZMK/LMK
            scheme_length = 1
            length = 16*2
        elif (scheme == 'T'):
            # Triple Length under ZMK/LMK
            scheme_length = 1
            length = 16*3
        else:
            raise ValueError('invalid key scheme[' + scheme + ']')
        var = buffer[scheme_length:scheme_length+length]
        return (KeyVariable(var, scheme), scheme_length+length)

class PINField(DataField):
    def __init__(self, name="", coder=None, size=0):
        DataField.__init__(self, name, coder, size)

    def encode(self, var, cmdObj):
        var = var.pack()
        length = len(var)
        if (length > Configure.CFG_PIN_LENGTH-1):
            raise ValueError('PIN length exceed configuration')
        var = var + 'F'*(Configure.CFG_PIN_LENGTH-length)
        return var

    def decode(self, buffer, cmdObj):
        length = Configure.CFG_PIN_LENGTH
        var = buffer[:length]
        index = string.find(var, 'F')
        if (index < 0):
            raise ValueError('PIN has no terminating F')
        var = var[:index]
        return (DataVariable(var), length)

class CheckValueField(DataField):
    def __init__(self, name="", coder=None, size=0):
        DataField.__init__(self, name, coder, size)

    def encode(self, var, cmdObj):
        buf = var.pack()
        return buf[:Configure.CFG_KCV_LENGTH]

    def decode(self, buffer, cmdObj):
        length = Configure.CFG_KCV_LENGTH
        return (DataVariable(buffer[:length]), length)

class DelimiteredVarLenField(DataField):
    """ 有分隔符结尾的变长域 """
    """ 如果分隔符为空，将会取值到buffer结束 """
    def __init__(self, name="", coder=None, size=0, delimiter=Configure.CFG_ELEMENT_DELIMITER):
        DataField.__init__(self, name, coder, size)
        self.delimiter = delimiter

    def encode(self, var, cmdObj):
        return var.pack()

    def decode(self, buffer, cmdObj):
        if self.delimiter == '':
            length = len(buffer)
            return (DataVariable(buffer), length)
        else:
            length = string.find(buffer, self.delimiter)
            if (length > 0):
                return (DataVariable(buffer[:length]), length+len(self.delimiter))
            else:
                length = len(buffer)
                return (DataVariable(buffer), length)
#                raise ValueError('VarLenField has no terminating delimiter')

class LengthedVarLenField(DataField):
    """ 长度由其他域指定的变长域 """
    def __init__(self, name="", coder=None, size=0, length_element_name=''):
        DataField.__init__(self, name, coder, size)
        self.length_element_name = length_element_name

    def encode(self, var, cmdObj):
        return var.pack()

    def decode(self, buffer, cmdObj):
        length = string.atoi(cmdObj.__dict__[self.length_element_name].value)
        if (length < 0):
            raise ValueError('VarLenField has no terminating delimiter')
        var = buffer[:length]
        return (DataVariable(var), length)

class DelimiterField(DataField):
    def __init__(self, name="", coder=None, size=0):
        DataField.__init__(self, name, coder, size)

    def encode(self, var, cmdObj):
        return Configure.CFG_ELEMENT_DELIMITER

    def decode(self, buffer, cmdObj):
        if (buffer[0] != Configure.CFG_ELEMENT_DELIMITER):
            raise ValueError('delimiter missing')
        var = buffer[0]
        return (DataVariable(var), 1)


# 域编码格式（A AN N ANS BCD....）
class FieldEncode:
    def __init__(self, regularExpression=None):
        self.charSet = charSet
        self.re = regularExpression

    def encode(self, variable, size, padding):
        return self.charSet.encode(variable)

    def decode(self, buffer, size):
        return (self.charSet.decode(buffer), size)

    def valid(self, variable):
        """ valid the content in variables according to the predifined pattern """
        if (self.re == None):
            return True
        elif (re.match(variable) == None):
            return False
        else:
            return True

    def padding(self, variable, size, align, pad_char):
        padding = pad_char * (size - len(variable))
        if (align == LEFT_JUST):
            return variable+padding
        elif (align == RIGHT_JUST):
            return padding+variable


class FieldEncode_ASCII(FieldEncode):
    """ alphabetical characters """
    def __init__(self):
        regularExpression = re.compile('^[a-zA-Z]*$')
        FieldEncode.__init__(self, regularExpression)

    def encode(self, variable, size, padding=False):
        if (padding):
            variable = variable[:size]
            variable = self.padding(variable, size, LEFT_JUST, ' ')
        return self.charSet.encode(variable)

    def decode(self, buffer, size):
        var = buffer[:size]
        return (var, size)








class CommandObj:
    def __init__(self):
        self.MessageHeader = ""
        self.MessageTrailer = ""

class CommandPattern:
    def __init__(self, code, func=None):
        self.code = code
        self.func = func
        self.desc = ""
        self.elements = []
        element = DataField('Code', None, 2)
        self.elements.append(element)

    def AppendElement(self, element):
        self.elements.append(element)

    def pack(self, commandObj):
        buffer = ""
        # message header
        buffer += commandObj.MessageHeader

        # data elements
        for element in self.elements:
            var = commandObj.__dict__[element.name]
            var = element.encode(var, commandObj)
            buffer += var

        # optional message trailer
        if (len(commandObj.MessageTrailer) > 0):
            buffer += Configure.END_MESSAGE_DELIMITER
            buffer += commandObj.MessageTrailer

        return buffer

    def unpack(self, buffer):
        # message header
        MessageHeader = buffer[:Configure.CFG_MESSAGE_HEADER_LENGTH]
        obj = CommandObj()
        obj.MessageHeader = MessageHeader
        buffer = buffer[Configure.CFG_MESSAGE_HEADER_LENGTH:]

        # optional message trailer
        index = string.find(buffer, Configure.END_MESSAGE_DELIMITER)
        if (index >= 0):
            trailer = buffer[index:]
            print trailer
            if (trailer[0] != Configure.END_MESSAGE_DELIMITER):
                raise ValueError('invalid message')
            if (len(buffer)-index > Configure.CFG_MESSAGE_TRAILER_LENGTH+1):
                raise ValueError('message trailer is too long')
            MessageTrailer = trailer[1:]
            obj.MessageTrailer = MessageTrailer

        # data elements
        for element in self.elements:
            if len(buffer) > 0:
                if element.present_condition.conditionSatisfied(obj):
                    (var, length) = element.decode(buffer, obj)
                    obj.__dict__[element.name] = var
                    buffer = buffer[length:]
            else:
                obj.__dict__[element.name] = DataVariable('')

        return obj

    def dump(self, cmdObj):
        msg = ''
        # message header
        msg += "MessageHeader:\'" + cmdObj.MessageHeader + "\'\n"

        # data elements
        for element in self.elements:
            if element.present_condition.conditionSatisfied(cmdObj):
                val = str(cmdObj.__dict__[element.name])
                if element.coder == 'BINARY':
                    val = hexlify(val)
                msg += element.name + ":\'" + val + "\'\n"

        # optional message trailer
        msg += "MessageTrailer:\'" + cmdObj.MessageTrailer + "\'\n"

        return msg


class RequestCommand(CommandPattern):
    def __init__(self, code, resp_code, func):
        CommandPattern.__init__(self, code, func)
        self.resp_code = resp_code

class ResponseCommand(CommandPattern):
    def __init__(self, code):
        CommandPattern.__init__(self, code)
        resp_cd = DataField('ResponseCode', None, 2)
        self.elements.append(resp_cd)



class CommandParseHandler(ContentHandler):

    def __init__(self, func_hash):
        self.func_hash = func_hash
        self.null = re.compile("^\s*$")
        self.content = ""
        self.command = None
        self.command_hash = {}
        self.element = None
        self.size_attrs = None

    def startElement(self, tag, attrs):
        if (tag == "command"):
            code = attrs['code']
            if self.command_hash.has_key(code):
                raise ValueError('command[' + code + '] duplicated')
            direction = attrs['direction'].upper()
            if (direction == 'REQUEST'):
                resp_code = attrs['response_code'].encode('ascii')
                if self.func_hash.has_key(code):
                    func = self.func_hash[code]
                    self.command = RequestCommand(code, resp_code, func)
                else:
                    print code
                    raise ValueError('function[command_' + code + '] not defined')
            elif (direction == 'RESPONSE'):
                self.command = ResponseCommand(code)
            else:
                raise ValueError('invalid direction ' + attrs['direction'])
        elif (tag == "element"):
            try:
                type = attrs['type'].upper()
            except:
                type = 'NORMAL'
            if (type == 'NORMAL'):
                self.element = DataField()
            elif (type == 'KEY'):
                self.element = KeyField(size = Configure.CFG_KEY_LENGTH)
            elif (type == 'ZMK'):
                self.element = KeyField(size = Configure.CFG_ZMK_LENGTH)
            elif (type == 'CVK'):
                self.element = KeyField(size = Configure.CFG_CVK_LENGTH)
            elif (type == 'PIN'):
                self.element = PINField()
            elif (type == 'DELIMITER'):
                self.element = DelimiterField()
            elif (type == 'CHECKVALUE'):
                self.element = CheckValueField()
            else:
                raise ValueError('invalid element type ' + attrs['type'])
        elif (tag == "size"):
            self.size_attrs = attrs
        elif (tag == "present_condition"):
            if (attrs['type'] == 'OnValue'):
                self.element.present_condition = PresentConditionOnValue(attrs['element'])
            elif (attrs['type'] == 'OnPresentation'):
                self.element.present_condition = PresentConditionOnPresentation(attrs['element'])
            elif (attrs['type'] == 'OnNotNull'):
                self.element.present_condition = PresentConditionOnNotNull(attrs['element'])
            else:
                raise ValueError('present condition type error[' + attrs['type'] + ']')

    def endElement(self, tag):
        if (tag == "command"):
            self.command_hash[self.command.code] = self.command
            self.command = None
        elif (tag == "description"):
            self.command.desc = self.content
        elif (tag == "element"):
            self.command.AppendElement(self.element)
            self.element = None
        elif (tag == "name"):
            self.element.name = self.content.encode('ascii')
        elif (tag == "encode"):
            self.element.coder = self.content
        elif (tag == "size"):
            self.element.size = string.atoi(self.content)
            if (self.element.size == -1):
                # variable length field
                if self.size_attrs.has_key('delimiter'):
                    self.element = DelimiteredVarLenField(self.element.name, self.element.encode, 0, self.size_attrs['delimiter'].encode('ascii'))
                elif self.size_attrs.has_key('length_element'):
                    self.element = LengthedVarLenField(self.element.name, self.element.encode, 0, self.size_attrs['length_element'])
            self.size_attrs = None
        elif (tag == "value"):
            self.element.present_condition.addConditionValue(self.content)

        self.content = ""

    def characters(self, content):
        if (self.null.match(content) == None):
            self.content += string.strip(content)


def LoadCommandPattern(filename, func_hash):
#    try:
        p = make_parser()
        handler = CommandParseHandler(func_hash)
        p.setContentHandler(handler)
        p.parse(filename)

        return handler.command_hash
#    except:
#        return {}

def LoadCommandFuncsSuffix(suffix):
    func_hash = {}
    commands = listFiles('commands', 'command??'+suffix, recurse=0)
    for command in commands:
#        command = re.sub(r"commands\\", "", command)
        command = re.sub(r"commands\/", "", command)
        command = re.sub(suffix, "", command)
        module = __import__(command)
        for funcname in module.__dict__.keys():
            m = re.match('^command_(..)$', funcname)
            if (m != None):
                if func_hash.has_key(m.group(1)):
                    raise ValueError('command[' + m.group(1) + '] duplicated')
                func_hash[m.group(1)] = module.__dict__[funcname]

    return func_hash

def LoadCommandFuncs():
    import sys
    sys.path.append("commands")
    func_hash = LoadCommandFuncsSuffix(".py")
    if (len(func_hash) > 0):
        return func_hash
    else:
        return LoadCommandFuncsSuffix(".pyc")

#def LoadCommandFuncs():
#    import AllCommands
#    commands = listFiles(path, 'command??.xml', recurse=0)
#    func_hash = {}
#    for funcname in AllCommands.__dict__.keys():
#        m = re.match('^command_(..)$', funcname)
#        if (m != None):
#            func_hash[m.group(1)] = AllCommands.__dict__[funcname]
#    return func_hash



class MessageProcessor:
    def __init__(self, commandPatternFile, log=None):
        self.commandPatternFile = commandPatternFile
        func_hash = LoadCommandFuncs()
        self.command_hash = LoadCommandPattern(commandPatternFile, func_hash)
        self.log = log

    def ProcessMessage(self, message):
        resp_msg = ""
        commandCode = message[Configure.CFG_MESSAGE_HEADER_LENGTH:Configure.CFG_MESSAGE_HEADER_LENGTH+2]
        if self.command_hash.has_key(commandCode):
            command = self.command_hash[commandCode]
            cmdObj = command.unpack(message)
            if (self.log != None):
                logMsg = command.dump(cmdObj)
                self.log.addMessage(logMsg)
#            print cmdObj.__dict__
            respObj = command.func(cmdObj)
            # add common elements
            respObj.MessageHeader = cmdObj.MessageHeader
            respObj.MessageTrailer = cmdObj.MessageTrailer
            respObj.Code = DataVariable(command.resp_code)

#            print respObj.__dict__
            respCommand = self.command_hash[command.resp_code]
            resp_msg = respCommand.pack(respObj)
            if (self.log != None):
                logMsg = respCommand.dump(respObj)
                self.log.addMessage(logMsg)
            return resp_msg
        else:
            raise ValueError('invalid command [' + commandCode + ']')







if (__name__ == "__main__"):
    import sys
    class Logger:
        def __init__(self): pass
        def addMessage(self, message):
            print message

    logger = Logger()
    mp = MessageProcessor('CommandPattern.xml', logger)



#    sys.exit()
    message = '1234KQ22843FDA0B15CA1618843FDA0B15CA1618\x12\x34\x56\x78\x90\x12\x34\x56\x01\x230000\xD7\x32\x52\x60\x05\x6B\x3F\xD300'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234KU02FC9142CB51FEF5D6FC9142CB51FEF5D6\x12\x34\x56\x78\x90\x12\x34\x56\x00\x00\x00\x00\x00\x00\x12\x340008\x12\x34\x56\x78\x90\x12\x34\x56'
    resp = mp.ProcessMessage(message)
    print resp

    exit(0)

    message = '1234KQ10843FDA0B15CA1618843FDA0B15CA1618\x12\x34\x56\x78\x90\x12\x34\x56\x01\x23000008\x12\x34\x56\x78\x90\x12\x34\x56\x78;\xD7\x32\x52\x60\x05\x6B\x3F\xD300'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234KQ00843FDA0B15CA1618843FDA0B15CA1618\x12\x34\x56\x78\x90\x12\x34\x56\x01\x23000008\x12\x34\x56\x78\x90\x12\x34\x56\x78;\xD7\x32\x52\x60\x05\x6B\x3F\xD3'
    resp = mp.ProcessMessage(message)
    print resp

    exit(0)

    # unpack message
    message = '1234EE3B3A0EC90E9C558B111111FFFFFF06673010402800123456789012345667301040280N'
    resp = mp.ProcessMessage(message)
    print resp
    message = '1234EE3B3A0EC90E9C558B000000FFFFFF06811034803066123456789012345681103480306N'
    resp = mp.ProcessMessage(message)
    print resp
    message = '1234DE3B3A0EC90E9C558B123456F06673010402800123456789012345667301040280N'
    resp = mp.ProcessMessage(message)
    print resp
    message = '    DE3B3A0EC90E9C558B948842F06674000001107123456789012345667400000110N'
    resp = mp.ProcessMessage(message)
    print resp

    print "\n\n"

#    message = '1234CW320D4D18109327D69C994F0AA348A7583568274934067611;1010106'
    message = '1234CW0A61E674E88C6A7E0A61E674E88C6A7E3568274934067611;1010106'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234CWU1750CDFB0757D3B3021AE502DDEDD9803568274934067611;1010106'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234CYU1750CDFB0757D3B3021AE502DDEDD9807173568274934067611;1010106'
    resp = mp.ProcessMessage(message)
    print resp


    print "\n\n"

    message = '1234NG673010402800868064F' + chr(0x19) + '99999999999999999999999999999999'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234NG811034803066448926F'
    resp = mp.ProcessMessage(message)
    print resp

    """
    NG 811034803066 448926F
    NH 328293F

    NG 673010402800 868064F
    NH00 459838F 301040280010
    """

    message = '1234EA8B4ECCAE01B4B17A3B3A0EC90E9C558B12BB2302883721C80E0806811034803066123456789012345681103480306N000000FFFFFF'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234JE8B4ECCAE01B4B17ABB2302883721C80E08811034803066'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234JCFCBA7CF5972CF0DDBB2302883721C80E08811034803066'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234JG8B4ECCAE01B4B17A08811034803066448926F'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234MQ099C86D96674E78411230420 163568256758324426 011000 000000010000 0810222036 000002 6011 00 0803112900 0803112900 001 100001 02000763130907192701'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234MQ199C86D96674E78410320420 163568256758324426 011000 0'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234MQ399C86D96674E7841E64EDA19D56735CF09100000010000 0810222036 000002 6011 00 0803112900 0803112900 001 100001 02000763130907192701'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234MA6A672D0CF83197440420 163568256758324426 011000 000000010000 0810222036 000002 6011 00 0803112900 0803112900 001 100001 02000763130907192701'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234ME6A672D0CF83197446A672D0CF8319744FBD2FDC70420 163568256758324426 011000 000000010000 0810222036 000002 6011 00 0803112900 0803112900 001 100001 02000763130907192701'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234MS010099C86D96674E784101230420 163568256758324426 011000 000000010000 0810222036 000002 6011 00 0803112900 0803112900 001 100001 02000763130907192701'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234CC8B4ECCAE01B4B17A8B4ECCAE01B4B17A12BB2302883721C80E080811034803066'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234CAFCBA7CF5972CF0DD8B4ECCAE01B4B17A12BB2302883721C80E080811034803066'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234FADA05B7A979CBD9A156CC09E7CFDC4CEF'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234FAU42BBE7D9A0A55D0EAA54C982B4D06B7056CC09E7CFDC4CEF'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234FAU42BBE7D9A0A55D0EAA54C982B4D06B70X56CC09E7CFDC4CEF56CC09E7CFDC4CEF'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234FAU42BBE7D9A0A55D0EAA54C982B4D06B70UF7B242F7911004F7536FE0EBA81EC899'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234FAU42BBE7D9A0A55D0EAA54C982B4D06B70X56CC09E7CFDC4CEF56CC09E7CFDC4CEF;UU1'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234GCU42BBE7D9A0A55D0EAA54C982B4D06B70U063A0E7C0F2124E54BFA531C4095771D;UU1'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234IAU42BBE7D9A0A55D0EAA54C982B4D06B70;UU1'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234A6001DA05B7A979CBD9A156CC09E7CFDC4CEFZ'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234A6001U42BBE7D9A0A55D0EAA54C982B4D06B70X56CC09E7CFDC4CEF56CC09E7CFDC4CEFU'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234A00001Z'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234MQ06A672D0CF83197441230420 164026731234567890 011000 000000001000 0529165841 000003 6011 00 0803112900 0803112900 001 100001 02000000011111111111'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234MA6A672D0CF83197440420 164026731234567890 011000 000000001000 0529165841 000003 6011 00 0803112900 0803112900 001 100001 02000000011111111111'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234MC6A672D0CF8319744312FF9250420 164026731234567890 011000 000000001000 0529165841 000003 6011 00 0803112900 0803112900 001 100001 02000000011111111111'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234ME6A672D0CF83197446A672D0CF8319744312FF9250420 164026731234567890 011000 000000001000 0529165841 000003 6011 00 0803112900 0803112900 001 100001 02000000011111111111'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234MGUA43ACFB17EE787E0D09613FF679AD4466A672D0CF8319744'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234MIUA43ACFB17EE787E0D09613FF679AD446116DD1968ADB63F8'
    resp = mp.ProcessMessage(message)
    print resp

    message = '1234CC5C9B078DA816F0965C9B078DA816F09612DB6D719C7A1E4D290808673123456789'
    resp = mp.ProcessMessage(message)
    print resp


