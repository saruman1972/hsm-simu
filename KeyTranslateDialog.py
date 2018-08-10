import sys
import wx
import re
from binascii import *
from Utility import *

keyTypes = [
    'ZMK',
    'ZPK',
    'TMK',
    'TPK',
    'PVK',
    'CVK',
    'TAK',
    'ZAK',
    'ZEK',
    'RSA',
    'MK-AC',
    'MK-SMI',
    'MK-SMC',
    'MK-DAK'
]
keySchemes = [
    '',
    'U',
    'T',
]

class KeyTranslateDialog(wx.Dialog):
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, -1, title)
        sizer = wx.BoxSizer(wx.VERTICAL)

        box1 = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, -1, "Key Type:")
        box1.Add(label)
        self.keyTypeList = wx.Choice(self, -1, size=(100,-1), choices=keyTypes)
        box1.Add(self.keyTypeList)
        
        box2 = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, -1, "Key Scheme:")
        box2.Add(label)
        self.keySchemeList = wx.Choice(self, -1, size=(80,-1), choices=keySchemes)
        box2.Add(self.keySchemeList)
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(box1, 50, wx.ALIGN_LEFT, 50)
        box.Add(wx.Size(100,50), 50)
        box.Add(box2, 50, wx.ALIGN_RIGHT, 50)

        sizer.Add(box, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        
        label = wx.StaticText(self, -1, "Original Key:")
        sizer.Add(label, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.originalKeyText = wx.TextCtrl(self, -1, "", size=(400,-1))
        self.originalKeyText.SetMaxLength(32)
        sizer.Add(self.originalKeyText, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        label = wx.StaticText(self, -1, "Translated Key:")
        sizer.Add(label, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.translatedKeyText = wx.TextCtrl(self, -1, "", size=(400,-1), style=wx.TE_READONLY)
        sizer.Add(self.translatedKeyText, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)
        self.btnDecrypt = wx.Button(self, -1, 'Decrypt')
        self.Bind(wx.EVT_BUTTON, self.OnDecrypt, self.btnDecrypt)
        box.Add(self.btnDecrypt)
        self.btnEncrypt = wx.Button(self, -1, 'Encrypt')
        self.Bind(wx.EVT_BUTTON, self.OnEncrypt, self.btnEncrypt)
        box.Add(self.btnEncrypt)
        sizer.Add(box, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

        icon = wx.Icon('icons/KeyTranslateDialog.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

    def GetInput(self):
        index = self.keyTypeList.GetSelection()
        if index < 0:
            raise ValueError('keyType not selected')
        keyType = keyTypes[index]
        index = self.keySchemeList.GetSelection()
        if index < 0:
            scheme = ''
        else:
            scheme = keySchemes[index]
        originalKey = self.originalKeyText.GetValue().upper()
        if (len(originalKey) != 16) and (len(originalKey) != 32):
            raise ValueError('key length error')
        if re.match('^[0-9A-F]*$', originalKey) == None:
            raise ValueError('invalid key')
        return (keyType, scheme, originalKey)

    def OnDecrypt(self, event):
        try:
            keyType, scheme, originalKey = self.GetInput()
        except: return
        translatedKey = decryptKeyUnderLMK(keyType, unhexlify(originalKey), scheme)
        self.translatedKeyText.SetValue(hexlify(translatedKey).upper())
        event.Skip()
    
    def OnEncrypt(self, event):
        try:
            keyType, scheme, originalKey = self.GetInput()
        except: return
        translatedKey = encryptKeyUnderLMK(keyType, unhexlify(originalKey), scheme)
        self.translatedKeyText.SetValue(hexlify(translatedKey).upper())
        event.Skip()

class TheApp(wx.App):
    def OnInit(self):
        dlg = KeyTranslateDialog(None, "Key Translate Dialog")
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        dlg.Destroy()
        return True

if __name__ == "__main__":
        theApp = TheApp(0)
        theApp.MainLoop()
