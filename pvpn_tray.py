#!/usr/bin/env python2
# pvpn-cli tray icon controller & status

import subprocess
from subprocess import check_output
import os
import sys
import wx

DEBUG=True

TRAY_ICON_ON = 'pvpn_on.png'
TRAY_ICON_OFF = 'pvpn_off.png'
PVPN_CLI_HOME = "/home/YOURUSERNAME/.protonvpn-cli/"

global PVPN_STATUS

def is_pvpn_found():
    if subprocess.call("type pvpn", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 1:
        sys.out.stderr("Cannot find pvpn binary !")
        sys.exit(1)

def debug_print(text):
    global DEBUG
    if DEBUG:
        print(text)

def disconnect_pvpn():
    check_output(['pvpn', '--disconnect']) 
    debug_print("Disconnected") 
    
def connect_pvpn_fastest():
    check_output(['pvpn', '--fastest-connect']) 
    debug_print("Connecting to fastest") 

def get_pvpn_status():
    global PVPN_STATUS 
    if os.path.isfile(PVPN_CLI_HOME + ".connection_config_id"):
        PVPN_STATUS=True 
    else:
        PVPN_STATUS=False

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item

class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        get_pvpn_status() 
        if PVPN_STATUS: 
            self.set_icon(TRAY_ICON_ON)
        else:
            self.set_icon(TRAY_ICON_OFF)

        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Connect/Disconnect', self.on_toggle_connection)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, check_output(['pvpn', '--status']))

    def on_toggle_connection(self, event): 
        global PVPN_STATUS 
        get_pvpn_status() 
        if PVPN_STATUS:
            debug_print("Will disconnect")
            disconnect_pvpn() 
            self.set_icon(TRAY_ICON_OFF)
        else:
            debug_print("Will connect")
            connect_pvpn_fastest()
            self.set_icon(TRAY_ICON_ON)
        
    def on_left_down(self, event):
        print 'Updating status'
        self.set_icon(TRAY_ICON)

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.frame.Close()

class App(wx.App):
    def OnInit(self):
        frame=wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True

def main():
    is_pvpn_found()
    app = App(False)
    app.MainLoop()

if __name__ == '__main__':
    main()
