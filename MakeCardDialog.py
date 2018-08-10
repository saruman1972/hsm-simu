import sys
import re
import string
import wx
import Command
from Configure import LoadConfiguration

class MakeCardDialog(wx.Dialog):
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, -1, title)
        sizer = wx.BoxSizer(wx.VERTICAL)

        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, 'Card No:')
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.cardnoText = wx.TextCtrl(self, -1, "", size=(200,-1))
        self.cardnoText.SetMaxLength(16)
        box.Add(self.cardnoText, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, 'Expiry CCYYMM:')
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.expiryText = wx.TextCtrl(self, -1, "", size=(80,-1))
        self.expiryText.SetMaxLength(6)
        box.Add(self.expiryText, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, 'Service Code:')
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.serviceCodeText = wx.TextCtrl(self, -1, "", size=(80,-1))
        self.serviceCodeText.SetValue('101')
        self.serviceCodeText.SetMaxLength(3)
        box.Add(self.serviceCodeText, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, 'PIN Offset:')
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.offsetText = wx.TextCtrl(self, -1, "", size=(80,-1))
#        self.offsetText.SetValue('000000FFFFFF')
#        self.offsetText.SetMaxLength(12)
        self.offsetText.SetValue('000000')
        self.offsetText.SetMaxLength(6)
        box.Add(self.offsetText, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, 'PIN:')
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.pinText = wx.TextCtrl(self, -1, "", size=(80,-1), style=wx.TE_READONLY)
        box.Add(self.pinText, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        label = wx.StaticText(self, -1, 'CVV2:')
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.cvv2Text = wx.TextCtrl(self, -1, "", size=(10,-1), style=wx.TE_READONLY)
        box.Add(self.cvv2Text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        label = wx.StaticText(self, -1, 'Track2 Data:')
        sizer.Add(label, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.track2Text = wx.TextCtrl(self, -1, "", size=wx.Size(400,-1), style=wx.TE_READONLY)
        sizer.Add(self.track2Text, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        self.btnOK = wx.Button(self, wx.ID_OK, "Generate")
        self.btnOK.SetDefault()
        sizer.Add(self.btnOK, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

        icon = wx.Icon('icons/MakeCardDialog.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.Bind(wx.EVT_BUTTON, self.OnOK, self.btnOK)
        self.mp = Command.MessageProcessor('CommandPattern.xml')
        self.LoadKeys()

    def OnOK(self, event):
        cardno = self.cardnoText.GetValue()
        if (len(cardno) != 16) or (re.match('^[0-9]*$', cardno) == None):
            return
        expiry = self.expiryText.GetValue()
        if (len(expiry) != 6) or (re.match('^[0-9]*$', expiry) == None):
            return
        serviceCode = self.serviceCodeText.GetValue()
        if (len(serviceCode) != 3) or (re.match('^[0-9]*$', serviceCode) == None):
            return
#        offset = self.offsetText.GetValue().upper()
        offset = self.offsetText.GetValue().upper() + 'FFFFFF'
        if (len(offset) != 12) or (re.match('^[0-9A-F]*$', offset) == None):
            return

        if cardno[0] == '3':
            brand = 'JCB'
        elif cardno[0] == '4':
            brand = 'VISA'
        elif cardno[0] == '5':
            brand = 'MC'
        elif cardno[0] == '6':
            brand = 'CUP'
        else: return

        print "PVK=", self.keys[brand + '|PVK']

        decimalTable = self.keys['DECIMAL_TABLE|']
        pinValidationData = self.keys['PIN_VALIDATION_DATA|']
        match_obj = re.search('\[(.*):(.*)\]', pinValidationData)
        if match_obj:
            (start,end) = match_obj.groups()
            pinValidationData = re.sub('\[(.*):(.*)\]', cardno[string.atoi(start):string.atoi(end)], pinValidationData)

        pvk = self.keys[brand + '|PVK']
        if len(pvk) == 16:
            pass
        elif len(pvk) == 32:
            pvk = 'X'+pvk
        elif len(pvk) == 48:
            pvk = 'Y'+pvk
        else:
            return

        message = '1234EE' + pvk + offset + '06' + cardno[-13:-1] + decimalTable + pinValidationData
        # BOC algorithm:
#        message = '1234EE' + self.keys[brand + '|PVK'] + offset + '06' + cardno[-13:-1] + '1234567890123456' + cardno[-13:-2] + 'N'
        # ABC algorithm: last 10 digit of cardno + 'DDDDDD'
#        message = '1234EE' + self.keys[brand + '|PVK'] + offset + '06' + cardno[-13:-1] + '0123456789012345' + cardno[-10:] + 'NN'
        print message
        resp = self.mp.ProcessMessage(message)
        cipherPIN = resp[8:]
        message = '1234NG' + cardno[-13:-1] + cipherPIN
        print message
        resp = self.mp.ProcessMessage(message)
        PIN = resp[8:-1]
        self.pinText.SetValue(PIN)

        print "CVK1=",self.keys[brand + '|CVK1']
        message = '1234CW' + self.keys[brand + '|CVK1'] + cardno + ';' + expiry[2:] + serviceCode
        print message
        resp = self.mp.ProcessMessage(message)
        CVV = resp[8:]
        self.track2Text.SetValue(cardno + '=' + expiry[2:] + serviceCode + '00000' + CVV + '00000')

        print "CVK2=",self.keys[brand + '|CVK2']
        serviceCode = '000'
        message = '1234CW' + self.keys[brand + '|CVK2'] + cardno + ';' + expiry[2:] + serviceCode
        print message
        resp = self.mp.ProcessMessage(message)
        CVV2 = resp[8:]
        self.cvv2Text.SetValue(CVV2)

    def LoadKeys(self):
        self.keys = {}
        file = open('KEY.txt', 'r')
        for line in file.xreadlines():
            info = line.strip()
            print "info=",info
            if re.match('^#', info): continue
            (brand, type, value) = info.split(',')
            print "brand=",brand,"type=",type,"value=",value
            self.keys[brand.strip() + '|' + type.strip()] = value.strip()
        file.close()

class TheApp(wx.App):
    def OnInit(self):
        dlg = MakeCardDialog(None, "Generate Card Information Tool")
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        dlg.Destroy()
        return True

if __name__ == "__main__":
        LoadConfiguration('Configuration.xml')
        theApp = TheApp(0)
        theApp.MainLoop()
