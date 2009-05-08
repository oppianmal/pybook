#!/usr/bin/env python
#
# Copyright (C) 2009 Mal Minhas <mal@oppian.com>
#

from __future__ import with_statement   # must come first
import gtk
import gtk.glade
from logUtils import log
from globals import APPNAME,VERSION,COPYRIGHT,HOMEDIR,GLADEFILE
from gtkUtils import contactDetails
import threading

DEVICESTORE='.devices'

#---------------------------------------------- Discovery Dialog ----------------------------------------------
import bluetooth
import select

class AsyncDiscoverer(bluetooth.DeviceDiscoverer):
    ''' Handles asynchronous discovery of Bluetooth devices.  
    If this code doesn't work, it's likely a problem with hcid 
    and you may need to 'sudo hciconfig hci0 down|up' to 
    get your adaptor working.  '''
    def __init__(self,parent):
        bluetooth.DeviceDiscoverer.__init__(self)
        self.parent=parent
        
    def cancel_discovery(self):
        if not self.done:
            self.cancel_inquiry()
            self.done=True
            self.parent.on_completedDiscovery(self.count)
            
    def pre_inquiry(self):
        self.count=0
        self.done = False
        self.parent.on_startedDiscovery()
        
    def device_discovered(self,address,device_class,name):
        self.count+=1
        self.parent.on_discoveredDevice(address,name,device_class)
        
    def inquiry_complete(self):
        self.done = True
        self.parent.on_completedDiscovery(self.count)
        
class BluetoothDevicesDialog:
    def __init__(self,parent):
        self.discoverer=None
        self.gladefile=GLADEFILE
        self.wTree=gtk.glade.XML(self.gladefile,"bluetoothDevices")
        self.devicesDialog=self.wTree.get_widget("bluetoothDevices")
        self.devicesDialog.set_title("Bluetooth device neighbourhood")
        self.devicesModelView=self.wTree.get_widget("devicesTreeView")
        # Create the listStore model to use with the devicesListView
        self.devicesModel=gtk.ListStore(str,str,str)  # (DevAddr,DevName,Type)
        self.populateWithCurrentDevices()
        # Create a filter, from the model and set the TreeView to use it        
        #self.deviceFilter=self.devicesModel.filter_new()
        #self.deviceFilter.set_visible_column(1)
        self.devicesModelView.set_model(self.devicesModel)
        self.devicesModelView.set_enable_search(True)
        self.devicesModelView.set_search_column(1)
        treeselection=self.devicesModelView.get_selection()
        treeselection.connect('changed',self.on_device_selection_changed)
        col1=contactDetails.createTreeViewColumn("Device",1)
        self.devicesModelView.append_column(col1)
        col2=contactDetails.createTreeViewColumn("Type",2)
        self.devicesModelView.append_column(col2)
        self.devicesDialog.connect("close",self.on_close,self)
        self.devicesDialog.connect("delete-event",self.on_close,self)
        # autoconnect => signal handlers are named class methods.  eg. "on_mainWindow_destroy"
        self.wTree.signal_autoconnect(self)
        # Now show everything!
        self.show()        
        
    def populateWithCurrentDevices(self):
        ''' Read current devices from our file store '''
        try:
            with open(DEVICESTORE,'r') as f:
                devices=[tuple(line.rstrip().split(';')) for line in f.readlines()]
                [self.devicesModel.append(dev) for dev in devices if len(dev)==3]
        except:
            pass
        
    def show(self):
        self.devicesDialog.show()
        
    #------------------------------------- signal handlers and callbacks ------------------------------------------
    def on_close(self,dialog,response,parent):
        log.debug("on_close: %s %s %s" % (dialog,response,parent))
        parent.devicesDialog=None
        dialog.destroy()
        
    def on_delete_event(self,dialog,event,parent):
        log.debug("on_delete_event: %s %s %s" % (dialog,event,parent))
        parent.devicesDialog=None
        return True
        
    def on_cancel_pressed(self,button):
        if self.discoverer:
            log.debug("on_cancel_pressed: cancelling existing discovery")
            # Need to cancel our discovery...
            self.discoverer.cancel_discovery()
        else:
            log.debug("on_cancel_pressed: destroying dialog")
            self.devicesDialog.destroy()        
        
    def on_connect_pressed(self,button):
        log.debug("on_connect_pressed: response=%s" % button)
        # TODO: This should trigger an OBEX beam of current vCard to remote device
        
    def kickDiscovery(self):
        ''' Check out this article re. PyGTK and threads: 
        http://faq.pygtk.org/index.py?req=show&file=faq20.006.htp '''
        # Acquire and release the lock each time you muck with GTK.
        gtk.gdk.threads_enter()
        self.devicesDialog.set_title("Searching for Bluetooth devices....")
        gtk.gdk.threads_leave()
        self.discoverer=AsyncDiscoverer(self)
        self.discoverer.find_devices(lookup_names=True)
        readfiles=[self.discoverer,]
        print self.discoverer,readfiles
        while self.discoverer:
            try:
                rfds=select.select(readfiles,[],[])[0]
                if self.discoverer in rfds:
                    self.discoverer.process_event()
            except Exception,e:
                log.error("Exception on discovery: '%s'" % e)
                #self.discoverer=None
                gtk.gdk.threads_enter()                
                self.on_completedDiscovery(self.discoverer.count)
                gtk.gdk.threads_leave()
            
    def on_search_pressed(self,button):
        ''' Kick off a Bluetooth device discovery sequence to search for new Bluetooth devices '''
        log.debug("on_search_pressed: response=%s" % button)
        if not self.discoverer:
            # The following needs to run in its own thread!
            threading.Thread(target=self.kickDiscovery).start()
        
    def on_startedDiscovery(self):
        log.debug("on_startedDiscovery")
        
    def on_discoveredDevice(self,address,name,device_class):
        log.debug("on_discoveredDevice: %s %s %s" % (address,name,device_class))
        # TODO: This device needs to be added to the database and updated in UI...
        with open(DEVICESTORE,'a') as f:
            def deviceClassToStr(devclass):
                return "unknown"
            f.write("%s;%s;%s\n" % (address,name,deviceClassToStr(device_class)))
            self.devicesModel.append((address,name,deviceClassToStr(device_class)))
            
    def on_completedDiscovery(self,count):
        log.debug("on_completedDiscovery: %d" % count)
        self.discoverer=None
        self.devicesDialog.set_title("Bluetooth device neighbourhood")
            
    def on_device_selection_changed(self,selection):
        ''' IMPORTANT: This signal is associated with a gtk.TreeSelection not in Glade-3! '''
        model, paths = selection.get_selected_rows()
        if paths and paths[0]:
            id=paths[0][0]
            log.debug("on_device_selection_changed: %s" % id)
            
#---------------------------------------------- About Dialog ----------------------------------------------
class AboutDialog:
    ''' gtk.AboutDialog '''
    def __init__(self,parent):
        authors = [
        "Mal Minhas <mal@oppian.com>"
        ]
        self.about_dialog = gtk.AboutDialog()
        self.about_dialog.set_transient_for(parent.window)
        self.about_dialog.set_destroy_with_parent(True)
        self.about_dialog.set_name(APPNAME)
        self.about_dialog.set_version(VERSION)
        self.about_dialog.set_copyright(COPYRIGHT)
        self.about_dialog.set_website("http://www.oppian.com")
        self.about_dialog.set_comments("Contacts Demonstrator")
        self.about_dialog.set_authors(authors)
        self.about_dialog.set_logo_icon_name(gtk.STOCK_ORIENTATION_PORTRAIT)
        # callbacks for destroying the dialog
        def close(dialog, response, editor):
            editor.about_dialog = None
            dialog.destroy()
        def delete_event(dialog, event, editor):
            editor.about_dialog = None
            return True
        self.about_dialog.connect("response", close, self)
        self.about_dialog.connect("delete-event", delete_event, self)
            
    def show(self):
        self.about_dialog.show()

#---------------------------------------------- vCard Export Dialog ----------------------------------------------
class ExportDialog:
    ''' gtk.FileSelection dialog '''
    def __init__(self,parent,contFullName,vcard):
        self.export_dialog = gtk.FileSelection(contFullName)
        self.export_dialog.set_transient_for(parent.window)
        self.export_dialog.set_destroy_with_parent(True)
        vcf=HOMEDIR+'/'+contFullName.replace(' ','')+".vcf"
        self.export_dialog.set_filename(vcf)
        # callbacks for destroying the dialog
        def close(dialog, response, vcf):
            # Need to open this file and save the vcard to it
            with open(vcf,'w') as f:
                f.write(vcard)
            dialog.destroy()
        def delete_event(dialog, event):
            dialog = None
            return True
        self.export_dialog.connect("response", close, vcf)
        self.export_dialog.connect("delete-event", delete_event)
        
    def show(self):
        self.export_dialog.show()
                
#---------------------------------------------- Confirmation Dialog ----------------------------------------------
class ConfirmationDialog:
    ''' gtk.MessageDialog '''
    def __init__(self,parent,msg):
        self.dialog=gtk.MessageDialog(parent.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_NONE,msg)
        self.dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT)
        self.dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
        
    def run(self):
        return self.dialog.run()

    def destroy(self):
        self.dialog.destroy()

#------------------------------------------ Test code -----------------------------------------------------
if __name__=='__main__':
    # TODO: Need to create a PyGTK Window for this to work.
    # Probably want to add some buttons to test the launch of 
    # the various dialogs.
    dlg=AboutDialog(None)
    dlg.show()    