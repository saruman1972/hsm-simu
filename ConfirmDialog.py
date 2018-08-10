import sys
import string
import re
import wx

class ConfirmDialog(wx.Dialog):
	def __init__(self, parent, title, info):
		wx.Dialog.__init__(self, parent, -1, title)
		sizer = wx.BoxSizer(wx.VERTICAL)

		label = wx.StaticText(self, -1, info)
		sizer.Add(label, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

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
		self.EndModal(wx.ID_OK)

class TheApp(wx.App):
	def OnInit(self):
		dlg = ConfirmDialog(None, "Confirm Dialog", "Configure changed, save before quit?")
		dlg.CenterOnScreen()
		val = dlg.ShowModal()
		if (val == wx.ID_OK):
			print "ok pressed"
		dlg.Destroy()
		return false

if __name__ == "__main__":
		theApp = TheApp(0)
		theApp.MainLoop()
