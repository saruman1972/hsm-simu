import sys
import time
import wx
import Command
import Communication
import LogPanel
from AboutDialog import AboutDialog
from ConfirmDialog import ConfirmDialog
import Configure
import pyDes
import Utility
from TestCommandDialog import TestCommandDialog

class MainFrame(wx.Frame):

    def __init__(self, parent, address=None, id=-1, title='', pos=wx.Point(200,200), size=wx.Size(800,600)):
        self.address = address

        wx.Frame.__init__(self, parent, -1, title, pos, size)
        wx.EVT_SIZE(self, self.OnSize)
        wx.EVT_CLOSE(self, self.OnCloseWindow)
        self.log = LogPanel.MessageLogPanel(self, -1)
        self.Menubar = wx.MenuBar(wx.MB_DOCKABLE)
        wx.EVT_MENU(self, 0x201, self.OnMenuClose)
        wx.EVT_MENU(self, 0x202, self.OnMenuSetting)
        wx.EVT_MENU(self, 0x203, self.OnMenuTestCommand)
        wx.EVT_MENU(self, 0x210, self.OnMenuHelp)

        FileMenu = wx.Menu("", wx.MENU_TEAROFF)
        FileMenu.Append(0x202, "Configuration", "")
        FileMenu.Append(0x203, "Test Command", "")
        FileMenu.Append(0x201, "Exit", "")
        self.Menubar.Append(FileMenu, "File")
        HelpMenu = wx.Menu("", wx.MENU_TEAROFF)
        HelpMenu.Append(0x210, "About")
        self.Menubar.Append(HelpMenu, "Help")
        self.SetMenuBar(self.Menubar)

        icon = wx.Icon('icons/HSMSim.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.mp = Command.MessageProcessor('CommandPattern.xml', log=self.log)
        self.comm = Communication.Communication(self.mp, log=self.log, address=self.address)
        self.comm.openCommunication()

    def OnCloseWindow(self, event):
        if Configure.changed:
            dlg = ConfirmDialog(self, "Confirm Dialog", "Configure Changed, Save before quit?")
            dlg.CenterOnScreen()
            val = dlg.ShowModal()
            if val == wx.ID_OK:
                Configure.SaveConfiguration('Configuration.xml')
            dlg.Destroy()
        self.comm.quit()
        self.Destroy()
        event.Skip()

    def OnSize(self, event):
        size = self.GetClientSize()
        self.log.SetSize(size)
        event.Skip()

    def OnMenuClose(self, event):
        self.Close()
        event.Skip()

    def OnMenuSetting(self, event):
        dlg = Configure.SettingDialog(self, "Setting Dialog")
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if (val == wx.ID_OK):
            if Configure.changed:
                self.log.addMessage('HSM reinitializing...')

                self.comm.quit()
                self.comm = None
                time.sleep(1)

                self.mp = Command.MessageProcessor('CommandPattern.xml', log=self.log)
                self.comm = Communication.Communication(self.mp, log=self.log, address=self.address)
                self.comm.openCommunication()

                self.log.addMessage('done')

        dlg.Destroy()
        event.Skip()

    def OnMenuTestCommand(self, event):
        dlg = TestCommandDialog(self, "Test Command Dialog")
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if (val == wx.ID_OK):
            message = 'Message Received:===============================\n' + dlg.command + '\n================================='
            self.log.addMessage(message)
            resp = self.mp.ProcessMessage(dlg.command)
            message = 'Message Send:**************************\n' + resp + '\n***********************************'
            self.log.addMessage(message)
        dlg.Destroy()
        event.Skip()

    def OnMenuHelp(self, event):
        dlg = AboutDialog(self, "About")
        dlg.CenterOnScreen()
        dlg.ShowModal()
        dlg.Destroy()
        event.Skip()



if (__name__ == "__main__"):
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:", ["address"])
    except getopt.GetoptError:
        opts = ()
    address = None
    for (opt, arg) in opts:
        if opt in ("-a", "--address"):
            address = arg

    Configure.LoadConfiguration('Configuration.xml')
    theApp = wx.App(0)
    frame = MainFrame(None, address, -1, title='HSM Simulation', size=(800,400))
    frame.Show(True)
    theApp.SetTopWindow(frame)
    theApp.MainLoop()
