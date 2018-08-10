import wx

class MessageLogPanel(wx.Panel):
	def __init__(self, parent, id, size=wx.DefaultSize):
		wx.Panel.__init__(self, parent, id)
		self.panel = wx.Panel(self, -1, wx.DLG_PNT(self, wx.Point(0, 0)), self.GetClientSize())
#		self.Text = wx.TextCtrl(self.panel, -1, "", wx.DLG_PNT(self.panel, wx.Point(0,0)), wx.Size(0,0), wx.TE_AUTO_URL | wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP)
		self.Text = wx.TextCtrl(self.panel, -1, "", wx.DLG_PNT(self.panel, wx.Point(0,0)), wx.Size(0,0), wx.TE_AUTO_URL | wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
		self.button = wx.Button(self.panel, 1003, "Clear Log")
		self.button.SetPosition((0, -20))
		self.msgBox = wx.StaticText(self.panel, -1, "", (0,0))
		self.Bind(wx.EVT_BUTTON, self.OnClearLog, self.button)
		self.Bind(wx.EVT_SIZE, self.OnSize)
	
	def OnCloseWindow(self, event):
		self.Destroy()
		event.Skip()

	def OnSize(self, event):
		size = self.GetClientSize()
		self.panel.SetSize(size)
		self.Text.SetSize((size.x, size.y-25))
		self.button.SetPosition((0, size.y-25))
		self.msgBox.SetPosition((100, size.y-25))
		self.msgBox.SetSize((size.x, 25))

	def OnClearLog(self, event):
		self.Text.Clear()
	def addMessage(self, message):
		self.Text.AppendText(message + "\n\n")

if (__name__ == "__main__"):
	theApp = wx.App(0)
	frame = wx.Frame(None, -1, title='HSM Simulation', size=(400,200))
	win = MessageLogPanel(frame, -1)
	win.addMsg("aaaaaaaaaa")

	frame.Show(True)
	theApp.SetTopWindow(frame)
	theApp.MainLoop()
