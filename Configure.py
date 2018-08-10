import sys
import string
import re
import wx
from xml.sax import *

CFG_KEY_LENGTH = 16
CFG_ZMK_LENGTH = 16
CFG_CVK_LENGTH = 32
CFG_PIN_LENGTH = 7
CFG_MESSAGE_HEADER_LENGTH = 4
CFG_MESSAGE_TRAILER_LENGTH = 32
CFG_ELEMENT_DELIMITER = ';'
CFG_KCV_LENGTH = 16
CFG_COMMUNICATION_PORT = 8888
CFG_PIN_VALIDATION_DATA = 'LAST5'

END_MESSAGE_DELIMITER = chr(0x19)
changed = False

LMK = [
    '0101010101010101',    '7902CD1FD36EF8BA',
    '2020202020202020',    '3131313131313131',
    '4040404040404040',    '5151515151515151',
    '6161616161616161',    '7070707070707070',
    '8080808080808080',    '9191919191919191',
    'A1A1A1A1A1A1A1A1',    'B0B0B0B0B0B0B0B0',
    'C1C1010101010101',    'D0D0010101010101',
    'E0E0010101010101',    'F1F1010101010101',
    '1C587F1C13924FEF',    '0101010101010101',
    '0101010101010101',    '0101010101010101',
    '0202020202020202',    '0404040404040404',
    '0707070707070707',    '1010101010101010',
    '1313131313131313',    '1515151515151515',
    '1616161616161616',    '1919191919191919',
    '1A1A1A1A1A1A1A1A',    '1C1C1C1C1C1C1C1C',
    '2323232323232323',    '2525252525252525',
    '2626262626262626',    '2929292929292929',
    '2A2A2A2A2A2A2A2A',    '2C2C2C2C2C2C2C2C',
    '2F2F2F2F2F2F2F2F',    '3131313131313131',
    '0101010101010101',    '0101010101010101'
]

KeyTypeTable = {
    '000' : 'ZMK',
    '100' : 'ZMK',
    '200' : 'KML',

    '001' : 'ZPK',

    '002' : 'PVK', # and 'TPK', 'TMK',
    '402' : 'CVK', # and 'CSCK'

    '003' : 'TAK',

    '006' : 'WWK',

    '008' : 'ZAK',

    '00A' : 'ZEK',

    '00C' : 'RSA',

    '409' : 'MK-DAK',
    '309' : 'MK-SMC',
    '209' : 'MK-SMI',
    '109' : 'MK-AC'
}

KeySchemeTable = [
    'Z',
    'U',
    'T',
    'X',
    'Y'
]

LMKFunction = {
    'PIN' : { 'PAIR' : [02, 03], 'VARIANT' : False, 'KEY_TYPE' : '???'},
    'ZMK' : { 'PAIR' : [04, 05], 'VARIANT' : False, 'KEY_TYPE' : '000'},
    'ZPK' : { 'PAIR' : [06, 07], 'VARIANT' : False, 'KEY_TYPE' : '001'},
    'TMK' : { 'PAIR' : [14, 15], 'VARIANT' : False, 'KEY_TYPE' : '002'},
    'TPK' : { 'PAIR' : [14, 15], 'VARIANT' : False, 'KEY_TYPE' : '002'},
    'PVK' : { 'PAIR' : [14, 15], 'VARIANT' : False, 'KEY_TYPE' : '002'},
    'CVK' : { 'PAIR' : [14, 15], 'VARIANT' : True , 'KEY_TYPE' : '402'},
    'TAK' : { 'PAIR' : [16, 17], 'VARIANT' : False, 'KEY_TYPE' : '003'},
    'ZAK' : { 'PAIR' : [26, 27], 'VARIANT' : False, 'KEY_TYPE' : '008'},
    'ZEK' : { 'PAIR' : [30, 31], 'VARIANT' : False, 'KEY_TYPE' : '00A'},
    'RSA' : { 'PAIR' : [34, 35], 'VARIANT' : False, 'KEY_TYPE' : '00C'},
    'MK-AC' : { 'PAIR' : [28, 29], 'VARIANT' : True  , 'KEY_TYPE' : '109'},
    'MK-SMI': { 'PAIR' : [28, 29], 'VARIANT' : True  , 'KEY_TYPE' : '209'},
    'MK-SMC': { 'PAIR' : [28, 29], 'VARIANT' : True  , 'KEY_TYPE' : '309'},
    'MK-DAK': { 'PAIR' : [28, 29], 'VARIANT' : True  , 'KEY_TYPE' : '409'}
}

LMKVariantTable = [
    0x00,
    0xA6,
    0x5A,
    0x6A,
    0xDE,
    0x2B,
    0x50,
    0x74,
    0x9C
]











def getConfigureKeyList():
    import Configure
    keys = []
    for key in Configure.__dict__.keys():
        if re.match('^CFG_', key):
            keys.append(key)
    return keys

class ConfigHandler(ContentHandler):

    def __init__(self):
        import Configure
        self.content = ""
        self.name = ''
        self.value = ''
        self.type = ''

    def startElement(self, tag, attrs):
        if (tag == 'element'):
            if attrs.has_key('type'):
                self.type = attrs['type']

    def endElement(self, tag):
        import Configure
        if (tag == 'element'):
            if self.type == 'int':
                val = string.atoi(self.value)
            else:
                val = self.value
            Configure.__dict__['CFG_'+self.name] = val
            self.name = ''
            self.value = ''
            self.type = ''
        elif (tag == "name"):
            self.name = self.content
        elif (tag == "value"):
            self.value = self.content
        self.content = ""

    def characters(self, content):
        if (re.match("^\s*$", content) == None):
            self.content += string.strip(content)

def LoadConfiguration(filename):
#    try:
        p = make_parser()
        handler = ConfigHandler()
        p.setContentHandler(handler)
        p.parse(filename)

#    except:
#        pass

def SaveConfiguration(filename):
    import Configure

    file = open(filename, 'w')
    file.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\" ?>\n")
    file.write("<configuration>\n")
    file.write("\t<description>\n")
    file.write("\t\tHSM configuration\n")
    file.write("\t</description>\n\n")

    for key in getConfigureKeyList():
        if str(type(Configure.__dict__[key])) == "<type 'int'>":
            file.write("\t<element  type=\"int\">\n")
        else:
            file.write("\t<element>\n")
        file.write("\t\t<name> " + key[4:] + " </name>\n")
        val = Configure.__dict__[key]
        if str(type(Configure.__dict__[key])) == "<type 'int'>":
            val = "%d" % val
        elif type(val) == 'str': pass
        else: pass
        file.write("\t\t<value> " + val + " </value>\n")
        file.write("\t</element>\n")
    file.write("</configuration>\n")
    file.close()




class SettingDialog(wx.Dialog):
    def __init__(self, parent, title):
        import Configure

        self.keys = getConfigureKeyList()
        wx.Dialog.__init__(self, parent, -1, title)
        sizer = wx.BoxSizer(wx.VERTICAL)

        for key in self.keys:
            box = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self, -1, key[4:])
            box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            text = wx.TextCtrl(self, -1, "", size=(80,-1))
            val = Configure.__dict__[key]
            if str(type(val)) == "<type 'int'>":
                val = "%d" % val
            elif type(val) == 'str': pass
            else: pass
            text.SetValue(val)
            self.__dict__[key] = text
            box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

            sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)




        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnSizer = wx.StdDialogButtonSizer()

        self.btnOK = wx.Button(self, wx.ID_OK)
        self.btnOK.SetDefault()
        btnSizer.AddButton(self.btnOK)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnSizer.AddButton(btn)
        btnSizer.Realize()

        sizer.Add(btnSizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

        self.Bind(wx.EVT_BUTTON, self.OnOK, self.btnOK)

    def OnOK(self, event):
        import Configure

        for key in self.keys:
            val = self.__dict__[key].GetValue()
            if str(type(Configure.__dict__[key])) == "<type 'int'>":
                val = string.atoi(val)
            elif type(val) == 'str': pass
            else: pass
            if Configure.__dict__[key] != val:
                Configure.__dict__[key] = val
                Configure.changed = True

        self.EndModal(wx.ID_OK)

class TheApp(wx.App):
    def OnInit(self):
        dlg = SettingDialog(None, "Setting Dialog")
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if (val == wx.ID_OK):
            print "ok pressed"
        dlg.Destroy()
        return false

if __name__ == "__main__":
        print getConfigureKeyList()
        SaveConfiguration("abcd")
        theApp = TheApp(0)
        theApp.MainLoop()
