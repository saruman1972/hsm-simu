import sys
import string
import re
import wx

class TestCommandDialog(wx.Dialog):
    def __init__(self, parent, title):
        import Configure

        wx.Dialog.__init__(self, parent, -1, title)
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1, "please enter command:")
        sizer.Add(label, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
#		self.text = wx.TextCtrl(self, -1, "", wx.DLG_PNT(parent, wx.Point(0,0)), wx.Size(0,0), wx.TE_AUTO_URL | wx.TE_MULTILINE | wx.HSCROLL)
        self.text = wx.TextCtrl(self, -1, "", wx.Point(0,0), wx.Size(600,100), wx.TE_AUTO_URL | wx.TE_MULTILINE | wx.HSCROLL)
        sizer.Add(self.text, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

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
        self.command = self.text.GetValue()
        self.EndModal(wx.ID_OK)

class TheApp(wx.App):
    def OnInit(self):
        dlg = TestCommandDialog(None, "Test Command Dialog")
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if (val == wx.ID_OK):
            print "ok pressed" + ":command=" + dlg.command
        dlg.Destroy()
        return False

if __name__ == "__main__":
        theApp = TheApp(0)
        theApp.MainLoop()
