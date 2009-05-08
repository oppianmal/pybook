#!/usr/bin/env python
#
# Copyright (C) 2009 Mal Minhas <mal@oppian.com>
#
# Description:
# ------------------
# Glade-3 and PyGTK Contacts technology demonstrator
#
# TODO:
# ---------
# 1. Implement basic scrolling list of contact names on the left                                DONE
#   - TreeView and TreeModel navigation                                                         DONE
#   - Sort out row activation                                                                   DONE
# 2. Implement support for import/export of contacts through EDS                                DONE
# 3. Implement window display of currently selected contact on the right                        DONE
#   - Figure out neat layout of display data                                                    DONE
#   - Figure out word wrapping of long note data                                                DONE
# 4. Implement support for contact thumbnail display                                            
# 5. Address book integration                                                                   DONE
#   - Evolution                                                                                 DONE
#   - WAB                                                                                       ---
# 6. Implement contact search support                                                           DONE
# 7. Export contacts as .vcf                                                                    DONE
# 8. Import contacts from .vcf                                                                  TBD
#   - Requires vCard parser/generator support - we need to shift all         
#     data interfacing to Evolution to be done via vCard using sympla...
# 9. Bluetooth sending of contacts via OBEX                                             TBD
# 10. Implement contacts deletion                                                            TBD
#
# 11. Stretch goal - implement Bluetooth support for importing contacts from a phone (SyncML)
# 12. Stretch goal - implement web service support for importing contacts from Google
# 13. Internationalisation and text format support (pango)

'''
def _create_object(self, contact):
        obj = evolution.ebook.EContact(vcard=contact.get_vcard_string())
        if self.book.add_contact(obj):
            return self._get_object(obj.get_uid()).get_rid()
        else:
            raise Exceptions.SyncronizeError("Error creating contact")

    def _delete_object(self, uid):
        try:
            return self.book.remove_contact_by_id(uid)
        except:
            # sys.excepthook(*sys.exc_info())
            return False
'''

from __future__ import with_statement   # must come first
# Common core initialization to ensure underlying platform is correctly set up.
import os,sys
try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import gtk
    import gtk.glade
except:
    print "Failed to handle imports properly!"
    sys.exit(1)
        
from globals import *
from gtkUtils import contactDetails
from logUtils import log
from contactUtils import symplaContact
from dialogs import AboutDialog,ExportDialog,BluetoothDevicesDialog,ConfirmationDialog

osname,platf=determinePlatform()
log.debug("OS: '%s', PLATFORM: '%s'" % (osname,platf))
if osname=='nt':
    # Using WABAccess: http://sourceforge.net/projects/wabaccess/
    # WABAccess is a convenience COM/ATL component that gives late binding access 
    # (via IDispatch) to Windows Address Book and Outlook Express functionality.
    # NOTE: In order to use this support, it is necessary to run the win32com 
    # makepy.py utility over "WABAccess 1.0 Library" to generate the Python type library.
    # If we wanted to use Outlook directly instead, we would need to run makepy.py 
    # over "MicrosoftOutlook 11.0 Object Library" and then use the  same general 
    # support as below to talk to Outlook via COM.
    # The OutlookExplorer.py script shows the way.
    import win32com.client
    from win32com.client.gencache import EnsureDispatch
    from win32com.client import constants
    WINDOWS=True
elif osname=='posix':
    # Using Evolution and EDS on Linux.  You can get the evolution Python bindings thus:
    # $ sudo apt-get install python-evolution
    import evolution
    WINDOWS=False
else:
    print "OS '%s' on platform '%s' not yet supported!" % (osname,platf)
    sys.exit()

class ContactsApp:
    def __init__(self):
        log.debug("ContactsApp::__init__")
        self.currentContact = None
        self.about_dialog = None
        self.hostHasGtkBuilder = False
        version=gtk.gtk_version
        if int(version[0]) >= 2 and int(version[1]) >= 12:   
            self.hostHasGtkBuilder = True
        log.debug("Does host support GtkBuilder?: %s" % self.hostHasGtkBuilder)
        self.gladefile=GLADEFILE
        self.wTree=gtk.glade.XML(self.gladefile,"mainWindow")
        self.window = self.wTree.get_widget("mainWindow")
        self.window.maximize()
        self.notebook=self.wTree.get_widget("mainNotebook")
        self.statusbar = self.wTree.get_widget("statusbar")
        self.contactModelView=self.wTree.get_widget("contactsTreeView")
        # Color changing of background needs to be done on the uppermost widget - in our case the viewport
        self.contactDetailViewport=self.wTree.get_widget("summaryViewport")
        color = gtk.gdk.color_parse("white")
        self.contactDetailViewport.modify_bg(gtk.STATE_NORMAL,color)
        self.contactDetailVbox=self.wTree.get_widget("summaryVbox")
        self.contactDetailName=self.wTree.get_widget("summaryName")
        self.contactDetailPhoto=self.wTree.get_widget("summaryPhoto")
        self.contactDetailTable=self.wTree.get_widget("summaryTable")
        # Create the listStore model to use with the contactListView
        self.contactModel=gtk.ListStore(str,str)  # (ContactId,FullName)
        self.populateWithAddressBookContacts()
        # Create a filter, from the model and set the TreeView to use it
        self.contactFilter=self.contactModel.filter_new()
        self.contactFilter.set_visible_column(1)
        #view=gtk.TreeView(filter)
        self.contactModelView.set_model(self.contactModel)
        self.contactModelView.set_enable_search(True)
        self.contactModelView.set_search_column(1)
        #self.contactModelView.set_filter(self.contactFilter)
        treeselection=self.contactModelView.get_selection()
        treeselection.connect('changed',self.on_contactsTreeView_selection_changed)
        col=contactDetails.createTreeViewColumn("Name",1)
        self.contactModelView.append_column(col)
        self.toolbar = self.wTree.get_widget("toolbar")
        # autoconnect => signal handlers are named class methods.  eg. "on_mainWindow_destroy"
        self.wTree.signal_autoconnect(self)
        self.window.set_icon_name(gtk.STOCK_ORIENTATION_PORTRAIT)   # set the window icon to the GTK "portrait" icon
        self.statusbar_cid = self.statusbar.get_context_id(APPNAME)   # setup and initialize our statusbar
        # We're going to fire up the last contact Id on startup
        self.contactModelView.set_cursor(121,col)
        # Now show everything!
        self.window.show()
                
    def populateWithAddressBookContacts(self):
        if WINDOWS:
            self.populateWithWABContacts()
        else:
            self.populateWithEvolutionContacts()
        
    def populateWithWABContacts(self):
        ''' Appends all WAB contacts to the contactList using the WAB (id,name) as the contact (id,name) '''
        log.debug("ContactsApp::populateWithWABContacts")
        self.addresses=EnsureDispatch("WABAccess.Session",bForDemand=0)
            
    def populateWithEvolutionContacts(self):
        ''' Appends all Evolution contacts to the contactList using the Evolution (id,name) as the contact (id,name) '''
        # Zeth on pyevolution:  http://commandline.org.uk/python/2007/dec/1/three-useful-python-bindings/
        log.debug("ContactsApp::populateWithEvolutionContacts")
        self.addresses=evolution.ebook.open_addressbook('default')
        # This will show you all the available properties
        allContacts=self.addresses.get_all_contacts()
        contacts=[(cont.get_property('full-name').lower(),cont) for cont in allContacts]    # Note the lowering...
        contacts.sort() # alphabetic sort in-place on contact names
        for (name,cont) in contacts:
            contId=cont.get_property('id')
            name=cont.get_property('full-name')
            self.contactModel.append((contId,name))            
            
    def displayVCardContact(self,contId,contFullName):
        ''' Displays corresponding vCard contact field details in the table in 'summaryViewport' '''
        log.debug("displayVcardContact(%s,'%s')" % (contId,contFullName))
        if self.currentContact and contId==self.currentContact[0]:
            log.debug("Attempting to show the same contact - moving on")
            return
        self.currentContact=(contId,contFullName)
        cont=self.getContactById(contId)
        vcf=cont.get_vcard_string()
        cont=symplaContact(vcard=vcf)
        # Now follows the display utility logic
        view,table=contactDetails.initContactDetailView(self)
        contactDetails.setupContactNameLabel(self,contFullName)
        # TO DO: sort out thumbnail and other fields...
        #contactDetails.setupContactThumbnail(self,cont)
        
        
        
    def displayEvolutionContact(self,contId,contFullName):
        ''' Displays corresponding Evolution contact field details in the table in 'summaryViewport' '''
        log.debug("displayEvolutionContact(%s,'%s')" % (contId,contFullName))
        if self.currentContact and contId==self.currentContact[0]:
            log.debug("Attempting to show the same contact - moving on")
            return
        self.currentContact=(contId,contFullName)
        cont=self.getContactById(contId)
        # Now follows the display utility logic
        view,table=contactDetails.initContactDetailView(self)
        contactDetails.setupContactNameLabel(self,contFullName)
        contactDetails.setupContactThumbnail(self,cont)
        # Populate our table with attr-vals from contact.  Note that 
        # we MUST supply these for the field display to work properly.
        validfields=['title','org','org_unit','mobile_phone','business_phone','email_1','email_2','birth_date','note','address-home','address-work']
        translations=['Title','Organisation','Unit','Mobile','Business Phone','Main Email','Secondary email','Birthdate','Note','Home xAddress','Work Address']
        labelmapping=dict(zip(validfields,translations))
        contactDetails.populateContactDetailFields(table,cont,validfields,labelmapping) 
        view.show_all()     # To now show the table
        
    def editContact(self,contId,contFullName):
        log.debug("editContact(%s,'%s')" % (contId,contFullName))
        
    def selectAndDisplayContact(self,contId,col=None):
        iter=self.contactModel.get_iter(contId)
        self.contactModelView.set_cursor(contId,col)
        contId,contFullName=self.contactModel.get(iter,0,1)
        self.displayEvolutionContact(contId,contFullName)
        #self.displayVCardContact(contId,contFullName)
        
    def getContactById(self,contId):
        # NOTE: self.addresses[0].__doc__   gives you the supported properties
        return self.addresses.get_contact(contId)
        
    #---------------------------  Menubar signal handlers --------------------------
    def on_about_menu_item_activate(self, menuitem, data=None):
        ''' Called when the user clicks the 'About' menu. We create a GtkAboutDialog. 
        This dialog will NOT be modal but will be on top of the main application window.'''
        if self.about_dialog:
            self.about_dialog.present()
            return
        about_dialog=AboutDialog(self)
        self.about_dialog = about_dialog
        about_dialog.show()
                
    #---------------------------  Toolbar buttons signal handlers --------------------------
    def on_button_add_clicked(self,widget,data=None):
        ''' User clicked to add a contact.  This should launch a new contact dialog '''
        # TODO: We would want to launch a dialog OR edit page of notebook here...
        log.debug("TBD")
        #contactId=self.id
        #contactFullName="Mickey Mouse %d" % self.id
        #self.contactModel.append((contactId,contactFullName))

    def on_button_edit_clicked(self,widget,data=None):
        ''' User clicked to edit a contact.  This should launch an edit contact dialog '''
        log.debug("TBD")
            
    def on_button_delete_clicked(self,widget,data=None):
        ''' Use a modal verification dialog '''
        contId,contFullName=self.currentContact
        messageDlg=ConfirmationDialog(self,"Are you sure you want to delete '%s'?" % contFullName)
        resp=messageDlg.run()
        if resp==gtk.RESPONSE_ACCEPT:
            log.debug("Delete '%s' now!" % contFullName)
        messageDlg.destroy()  # destroy dialog either way
        
    def on_button_export_clicked(self,widget,data=None):
        ''' User clicked to export a contact.  This should launch a new file dialog '''
        if not self.currentContact:
            log.warning("No current contact set - returning")
            return
        contId,contFullName=self.currentContact
        cont=self.getContactById(contId)
        vcard=cont.get_vcard_string()
        log.debug("Current contact='%s'" % contFullName)
        export_dialog=ExportDialog(self,contFullName,vcard)
        export_dialog.show()
        
    def on_button_send_clicked(self,widget,data=None):
        ''' User clicked to export a contact.  This should launch a Bluetooth device selection dialog '''
        discoverer_dialog=BluetoothDevicesDialog(self)
        discoverer_dialog.show()
        
    #---------------------------  Contact list treeview signal handlers --------------------------
    def on_contactsTreeView_selection_changed(self,selection):
        ''' IMPORTANT: This signal is associated with a gtk.TreeSelection not in Glade-3! '''
        model, paths = selection.get_selected_rows()
        if paths and paths[0]:
            contId=paths[0][0]
            log.debug("on_contactsTreeView_selection_changed : %s" % contId)
            self.selectAndDisplayContact(contId)
        
    def on_contactsTreeView_row_activated(self,treeview,path,col,data=None):
        ''' Invoked on _selecting_ a different entry in treeview.  Cue for launching an edit dialog/notebook tab '''
        model,iter=treeview.get_selection().get_selected()
        contId,contFullName=model.get(iter,0,1)   # Getting col 0 (uid) and col 1 (full name)        
        self.editContact(contId,contFullName)
        
    def on_contactsTreeView_start_interactive_search(self,treeview,data=None):
        log.debug("on_contactsTreeView_start_interactive_search: %s" % data)
        
    #---------------------------  Main window signal handlers --------------------------
    def on_mainWindow_destroy(self, widget, data=None):
        ''' When our window is destroyed, we want to break out of the GTK main loop. 
        We do this by calling gtk_main_quit(). We could have also just specified 
        gtk_main_quit as the handler in Glade!'''
        log.debug("ContactsApp::on_mainWindow_destroy")
        gtk.main_quit()
        
if __name__=="__main__":
    gtk.gdk.threads_init()  # Initialize threads
    mycontacts=ContactsApp()
    try:
        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()
    except:
        log.debug("Exiting from main GTK loop....")