import sys
import re
import string
import Command
from Command import DataVariable,KeyVariable

keys = {}
def LoadKeys():
	global keys
	file = open('KEY.txt', 'r')
	for line in file.xreadlines():
		info = line.strip()
		if re.match('^#', info): continue
		(brand, type, value) = info.split(',')
		keys[brand.strip() + '|' + type.strip()] = value.strip()
	file.close()
	return keys

class KeyConfig:
	def	__init__(self, PVK, CVK_A, CVK_B):
		self.PVK = PVK
		self.CVK_A = CVK_A
		self.CVK_B = CVK_B

KeyConfigVISA = KeyConfig('3B3A0EC90E9C558B','F72E9942D9531834','77039F757ABE1DBB')
KeyConfigMC   = KeyConfig('1A726916334F5E71','0A61E674E88C6A7E','0A61E674E88C6A7E')
KeyConfigJCB  = KeyConfig('3C391F648D6E52C2','F72E9942D9531834','77039F757ABE1DBB')
KeyConfigCUP  = KeyConfig('AD3B43EB558F2446','0A61E674E88C6A7E','0A61E674E88C6A7E')

def GetKeyConfig(cardno):
	if cardno[0] == '3': brand = 'JCB'
	elif cardno[0] == '4': brand = 'VISA'
	elif cardno[0] == '5': brand = 'MC'
	elif cardno[0] == '6': brand = 'CUP'
	else:
		raise ValueError('unsupported card')
	return KeyConfig(keys[brand + '|PVK'], keys[brand + '|CVK_A'], keys[brand + '|CVK_B'])

def LoadCardList(filename):
	cards = []
	file = open(filename, 'r')
	blank = re.compile(r"^$")
	comment = re.compile(r"^#")
	for line in file.xreadlines():
		info = string.strip(line)
		info = re.sub(r"\"| ", "", info)
		if (blank.match(info) or comment.match(info)):continue
		(cardno,expiry,offset) = string.split(info, ',')
		if len(expiry) == 6:
			expiry = expiry[2:]
		cards.append((cardno,expiry,offset))
	file.close()
	return cards

def GenCardInfo(mp,cardno,expiry,offset):
	keyConfig = GetKeyConfig(cardno)
	AccountNumber = cardno[-13:-1]
	# generate pin
	command = mp.command_hash['EE']
	obj = Command.CommandObj()
	obj.MessageHeader = '    '
	obj.Code = DataVariable('EE')
	obj.PVK = KeyVariable(keyConfig.PVK)
	obj.Offset = DataVariable(offset[:6] + 'FFFFFF')
	obj.CheckLength = DataVariable('06')
	obj.AccountNumber = DataVariable(AccountNumber)
	obj.DecimalizationTable = DataVariable('1234567890123456')
	obj.PINValidationData = DataVariable(AccountNumber[:-1] + 'N')
	message = command.pack(obj)
#	print message
	resp = mp.ProcessMessage(message)
#	print resp
	command = mp.command_hash['EF']
	pinResp = command.unpack(resp)
#	print pinResp.PIN
	command = mp.command_hash['NG']
	obj = Command.CommandObj()
	obj.MessageHeader = '    '
	obj.Code = DataVariable('NG')
	obj.PIN = pinResp.PIN
	obj.AccountNumber = DataVariable(AccountNumber)
	message = command.pack(obj)
#	print message
	resp = mp.ProcessMessage(message)
	command = mp.command_hash['NH']
#	print resp
	pinResp = command.unpack(resp)
	
	# generate cvv
	command = mp.command_hash['CW']
	obj = Command.CommandObj()
	obj.MessageHeader = '    '
	obj.Code = DataVariable('CW')
	obj.CVK_AB = KeyVariable(keyConfig.CVK_A+keyConfig.CVK_B)
	obj.PrimaryAccountNumber = DataVariable(cardno + ';')
	obj.ExpirationDate = DataVariable(expiry)
	obj.ServiceCode = DataVariable('106')
	message = command.pack(obj)
#	print message
	resp = mp.ProcessMessage(message)
#	print resp
	command = mp.command_hash['CX']
	cvvResp = command.unpack(resp)
#	print cvvResp.CVV
	
	return (pinResp.PIN, cvvResp.CVV)

# main
def main(filename):
	LoadKeys()
	mp = Command.MessageProcessor('CommandPattern.xml')
	cards = LoadCardList(filename)
	print "#index | cardno | track2 data | pin"
	index = 0
	for (cardno,expiry,offset) in cards:
		index += 1
		(PIN, CVV) = GenCardInfo(mp, cardno, expiry, offset)
		msg = "%010d|%s|%s=%s10600000%s00000|%s" % (index,cardno,cardno,expiry,CVV,PIN)
		print msg

if __name__ == '__main__':
	main(sys.argv[1])
