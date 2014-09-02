import packages.rmnetwork as network
import packages.rmutil as rmutil
from packages.rmgui import *
from packages.rmnetwork.constants import *
from packages.lang.Localizer import *
import os, sys, platform, ast, time, threading, shutil

import wx
from wx.lib.pubsub import pub as Publisher
from wx.lib.wordwrap import wordwrap

HOST_WIN = 1
HOST_MAC = 2
HOST_LINUX = 3
HOST_SYS = None
BASE_PATH = None

################################################################################
# RASP MEDIA ALL PLAYERS PANEL #################################################
################################################################################
class RaspMediaAllPlayersPanel(wx.Panel):
    def __init__(self,parent,id,title,index,hosts,host_sys):
        #wx.Panel.__init__(self,parent,id,title)
        wx.Panel.__init__(self,parent,-1)
        global HOST_SYS, BASE_PATH
        HOST_SYS = host_sys
        BASE_PATH = parent.parent.base_path
        self.parent = parent
        self.index = index
        self.hosts = hosts

        '''
        # DEBUG HOST LIST
        self.hosts = []
        for i in range(10):
            host = {}
            host['addr'] = "10.0.0.%d" % i
            host['name'] = "Player %d" % i
            self.hosts.append(host)
        '''
        self.mainSizer = wx.GridBagSizer()
        self.leftSizer = wx.GridBagSizer()
        self.rightSizer = wx.GridBagSizer()
        self.notebook_event = None
        self.prgDialog = None
        self.Initialize()


    def SetHost(self, hostAddress):
        self.host = hostAddress

    def LoadData(self):
        for host in self.parent.hosts:
            for curHost in self.hosts:
                if host['addr'] == curHost['addr']:
                    curHost['name'] = host['name']
                    curHost['name_label'].SetLabel(curHost['name'])

    def PageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.parent.GetSelection()
        self.notebook_event = event
        # print "OnPageChanged, old:%d, new:%d, sel:%d" % (old, new, sel)
        newPage = self.parent.GetPage(new)
        if self.index == newPage.index:
            # print "PAGE CHANGED TO INDEX %d - PROCESSING AND LOADING DATA..." % (self.index)
            self.pageDataLoading = True
            self.LoadData()

    def Initialize(self):
        # setup UI in sizers
        self.SetupPlayerSection()
        self.SetupControlSection()

        # add sizers to main sizer
        self.mainSizer.Add(self.scroll ,(0,0), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT, border=10)
        self.mainSizer.Add(self.rightSizer, (0,2), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP |wx.RIGHT | wx.BOTTOM, border=5)

        self.SetSizerAndFit(self.mainSizer)

        #line = wx.StaticLine(self,-1,size=(self.mainSizer.GetSize()[0],2))
        #self.mainSizer.Add(line, (1,0), span=(1,4))

        #line = wx.StaticLine(self,-1,size=(2,self.mainSizer.GetCellSize(0,0)[1]),style=wx.LI_VERTICAL)
        #self.mainSizer.Add(line,(0,1), flag = wx.LEFT, border = 10)

        #self.Fit()
        line = wx.StaticLine(self,-1,size=(2,570),style=wx.LI_VERTICAL)
        self.mainSizer.Add(line,(0,1), span=(1,1), flag=wx.LEFT | wx.RIGHT, border=5)

        self.Show(True)

    def SetupPlayerSection(self):
        # scrolled panel to show player status list
        self.scroll = wx.lib.scrolledpanel.ScrolledPanel(self, -1, size=(300,570))
        self.scroll.SetAutoLayout(1)
        self.scroll.SetupScrolling(scroll_x=False, scroll_y=True)
        self.scroll.SetSizer(self.leftSizer)

        index = 0
        # name, ip and a rename button for each host
        for host in sorted(self.hosts):
            name = wx.StaticText(self.scroll,-1,label=host['name'])
            host['name_label'] = name
            ip = wx.StaticText(self.scroll,-1,label=host['addr'])
            setName = wx.Button(self.scroll,-1,label="...",size=(27,25))
            identify = wx.Button(self.scroll,-1,label=tr("identify"))
            line = wx.StaticLine(self.scroll,-1,size=(280,2))

            # add status UI for current host
            self.leftSizer.Add(name, (index,0), flag=wx.ALL, border=5)
            self.leftSizer.Add(setName, (index,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=5)
            index += 1
            self.leftSizer.Add(ip, (index,0), flag=wx.ALL, border=5)
            self.leftSizer.Add(identify, (index,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=5)
            index += 1
            self.leftSizer.Add(line, (index, 0), span=(1,2), flag=wx.LEFT, border=10)
            index += 1

            self.Bind(wx.EVT_BUTTON, lambda event, host=host: self.UpdatePlayerName(event,host), setName)
            self.Bind(wx.EVT_BUTTON, lambda event, host=host: self.IdentifyPlayer(event,host), identify)


    def SetupControlSection(self):
        # setup controls
        startAll = wx.Button(self,-1,label=tr("restart_all"), size=(200,25))
        stopAll = wx.Button(self,-1,label=tr("stop_all"), size=(200,25))
        identAll = wx.Button(self,-1,label=tr("identify_all"), size=(200,25))
        rebootAll = wx.Button(self,-1,label=tr("reboot_all"), size=(200,25))

        # bind events
        self.Bind(wx.EVT_BUTTON, self.RestartAllPlayers, startAll)
        self.Bind(wx.EVT_BUTTON, self.StopAllPlayers, stopAll)
        self.Bind(wx.EVT_BUTTON, self.IdentifyAllPlayers, identAll)
        self.Bind(wx.EVT_BUTTON, self.RebootAllPlayers, rebootAll)

        line = wx.StaticLine(self,-1,size=(260,2))

        self.rightSizer.Add(startAll,(0,1), flag=wx.LEFT, border=5)
        self.rightSizer.Add(stopAll,(1,1), flag=wx.ALL, border=5)
        self.rightSizer.Add(identAll,(2,1), flag=wx.LEFT, border=5)
        self.rightSizer.Add(rebootAll,(3,1), flag=wx.ALL, border=5)
        self.rightSizer.Add(line, (4,1), flag=wx.ALL, border=5)

    def UpdatePlayerName(self, event, host):
        dlg = wx.TextEntryDialog(self, tr("new_name")+":", tr("player_name"), host['name'])
        if dlg.ShowModal() == wx.ID_OK:
            newName = dlg.GetValue()
            host['name_label'].SetLabel(newName)
            msgData = network.messages.getConfigUpdateMessage("player_name", str(newName))
            network.udpconnector.sendMessage(msgData, host['addr'])
            time.sleep(0.2)
            #self.LoadConfig()
        dlg.Destroy()

    def RestartAllPlayers(self, event=None):
        msgData = network.messages.getMessage(PLAYER_RESTART)
        network.udpconnector.sendMessage(msgData)

    def StopAllPlayers(self, event=None):
        msgData = network.messages.getMessage(PLAYER_STOP)
        network.udpconnector.sendMessage(msgData)

    def RebootAllPlayers(self, event=None):
        dlg = wx.MessageDialog(self, tr("reboot_all_info"), tr("reboot_all"), style = wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            msgData = network.messages.getMessage(PLAYER_REBOOT)
            network.udpconnector.sendMessage(msgData)
            if HOST_SYS == HOST_WIN:
                dlg.Destroy()
            self.parent.parent.Close()


    def IdentifyPlayer(self, event, host):
        msgData = network.messages.getMessage(PLAYER_IDENTIFY)
        network.udpconnector.sendMessage(msgData, host['addr'])
        msg = tr("dlg_msg_identify")
        dlg = wx.MessageDialog(self, msg, tr("dlg_title_identify"), wx.OK | wx.ICON_EXCLAMATION)
        if dlg.ShowModal() == wx.ID_OK:
            msgData2 = network.messages.getMessage(PLAYER_IDENTIFY_DONE)
            network.udpconnector.sendMessage(msgData2, host['addr'])
        dlg.Destroy()

    def IdentifyAllPlayers(self, event=None):
        msgData = network.messages.getMessage(PLAYER_IDENTIFY)
        network.udpconnector.sendMessage(msgData)
        msg = tr("dlg_msg_identify")
        dlg = wx.MessageDialog(self, msg, tr("dlg_title_identify"), wx.OK | wx.ICON_EXCLAMATION)
        if dlg.ShowModal() == wx.ID_OK:
            msgData2 = network.messages.getMessage(PLAYER_IDENTIFY_DONE)
            network.udpconnector.sendMessage(msgData2)
        dlg.Destroy()

    def UdpListenerStopped(self):
        # print "UDP LISTENER STOPPED IN PANEL %d" % self.index
        global HOST_SYS
        if self.pageDataLoading:
            if self.remoteListLoading:
                self.pageDataLoading = False
                Publisher.unsubAll()
                if self.parent.prgDialog:
                    # print "CLOSING PRG DIALOG IN PARENT..."
                    self.parent.prgDialog.Update(100)
                    if HOST_SYS == HOST_WIN:
                        self.parent.prgDialog.Destroy()
                if self.prgDialog:
                    # print "CLOSING PRG DIALOG IN PANEL..."
                    self.prgDialog.Update(100)
                    if HOST_SYS == HOST_WIN:
                        self.prgDialog.Destroy()
            else:
                self.LoadRemoteFileList()
        else:
            if self.prgDialog:
                self.prgDialog.Update(100)
                if HOST_SYS == HOST_WIN:
                    self.prgDialog.Destroy()

    def ButtonClicked(self, event):
        button = event.GetEventObject()
        if button.GetName() == 'btn_identify':
            msgData = network.messages.getMessage(PLAYER_IDENTIFY)
            network.udpconnector.sendMessage(msgData, self.host)
            msg = tr("dlg_msg_identify")
            dlg = wx.MessageDialog(self, msg, tr("dlg_title_identify"), wx.OK | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_OK:
                msgData2 = network.messages.getMessage(PLAYER_IDENTIFY_DONE)
                network.udpconnector.sendMessage(msgData2, self.host)
            dlg.Destroy()
        elif button.GetName() == 'btn_reboot':
            self.RebootPlayer()

    def RebootPlayer(self):
        self.prgDialog = wx.ProgressDialog(tr("dlg_title_reboot"), wordwrap(tr("dlg_msg_reboot"), 350, wx.ClientDC(self)), parent = self)
        Publisher.subscribe(self.RebootComplete, "boot_complete")
        #Publisher.subscribe(self.UdpListenerStopped, 'listener_stop')
        self.prgDialog.Pulse()

        msgData = network.messages.getMessage(PLAYER_REBOOT)
        network.udpconnector.sendMessage(msgData, self.host, UDP_REBOOT_TIMEOUT)

    def RebootComplete(self):
        # print "REBOOT COMPLETE CALLBACK"
        self.prgDialog.Update(100)
        if HOST_SYS == HOST_WIN:
            self.prgDialog.Destroy()
        dlg = wx.MessageDialog(self,"Reboot complete!","",style=wx.OK)
        dlg.Show()
        if HOST_SYS == HOST_WIN:
            dlg.Destroy()

    def OnPlayerUpdated(self, result):
        self.prgDialog.Destroy()
        dlg = wx.MessageDialog(self,str(result),"Player Update",style=wx.OK)


    def PlayClicked(self, event):
        msgData = network.messages.getMessage(PLAYER_START)
        network.udpconnector.sendMessage(msgData, self.host)

    def StopClicked(self, event):
        msgData = network.messages.getMessage(PLAYER_STOP)
        network.udpconnector.sendMessage(msgData, self.host)



# HELPER METHOD to get correct resource path for image file
def resource_path(relative_path):
    global BASE_PATH
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        #print "BASE PATH FOUND: "+ base_path
    except Exception:
        #print "BASE PATH NOT FOUND!"
        base_path = BASE_PATH
    #print "JOINING " + base_path + " WITH " + relative_path
    resPath = os.path.normcase(os.path.join(base_path, relative_path))
    #resPath = base_path + relative_path
    #print resPath
    return resPath
