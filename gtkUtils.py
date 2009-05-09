import gtk
import pango
import gobject

class contactDetails:
    @staticmethod
    def initContactDetailView(parent):
        # 1. Remove the existing table
        view=parent.contactDetailVbox
        table=parent.contactDetailTable
        view.remove(table)
        # 2. Create a new table
        table=gtk.Table(rows=30,columns=2,homogeneous=False)
        table.set_row_spacings(0)
        table.set_col_spacings(0)
        view.add(table)
        parent.contactDetailTable=table
        return view,table
        
    @staticmethod
    def setupContactNameLabel(parent,contFullName):
        ''' Setup name label '''
        font=pango.FontDescription("arial 12")
        parent.contactDetailName.modify_font(font)
        parent.contactDetailName.set_text("<span size='xx-large'><b>%s</b></span>" % contFullName)
        parent.contactDetailName.set_use_markup(True)
        
    @staticmethod
    def setupContactField(label,value,table,offset):
        label=gtk.Label("<span size='large'><b>%s:</b></span>" % label)
        label.set_use_markup(True)
        label.set_alignment(0.00,0.00)
        x,x1,y,y1=0,1,offset,offset+1
        table.attach(label,x,x1,y,y1,xoptions=gtk.FILL,yoptions=gtk.FILL,xpadding=0,ypadding=5) # x-x1 is the horiz range.  y-y1 is the vert range
        value.set_use_markup(True)
        value.set_alignment(0.00,0.00)
        x,x1,y,y1=1,2,offset,offset+1
        table.attach(value,x,x1,y,y1,xoptions=gtk.FILL,yoptions=gtk.FILL,xpadding=10,ypadding=5) # x-x1 is the horiz range.  y-y1 is the vert range
        
    @staticmethod
    def vcardThumbnailToGtkImage(photo):
        # Now we need to shovel it into a GTKImage....
        file="temp.jpg"
        f=open(file,'w')
        f.write(photo)
        f.close()
        return gtk.gdk.pixbuf_new_from_file(file).scale_simple(80,80, gtk.gdk.INTERP_BILINEAR)    # scale it dude
    
    @staticmethod
    def setupContactThumbnail(parent,image=None):
        photo=parent.contactDetailPhoto
        if image:
            photo.set_from_pixbuf(image)
            photo.set_property("height-request",80)
            photo.set_property("width-request",80)
            photo.set_no_show_all(False)
        else:
            photo.clear()
            photo.set_property("height-request",0)
            photo.set_property("width-request",0)
            photo.set_no_show_all(True)
        parent.contactDetailPhoto=photo

    @staticmethod
    def populateVobjectContactDetailFields(table,cont):
        ''' TODO: Need to do a proper label mapping and process these in the right order '''
        offset=0
        keys=[str(key) for key in cont.contents.keys()]
        for k in keys:
            # SPECIAL CASES:  'email', 'tel', 'org' - they are arrays
            if k in ['adr','note','title','bday','url','email','tel']:
                value=eval('cont.'+k+'.value')
                # Need to replace <BR> tags with \n and replace & with amp;
                if k=='note':
                    value=value.replace('&','amp;')
                    value=gtk.Label("<span size='large'>%s</span>" % value)   # Convert & to amp; etc
                    value.set_property("wrap",True)
                    value.set_property("wrap-mode",pango.WRAP_WORD)
                else:
                    value=gtk.Label("<span size='large'>%s</span>" % value)
                contactDetails.setupContactField(k,value,table,offset)
                offset+=1
            elif k=='org':
                value=', '.join(cont.org.value)
                value=gtk.Label("<span size='large'>%s</span>" % value)
                contactDetails.setupContactField(k,value,table,offset)
                offset+=1
                
    @staticmethod
    def populateEvolutionContactDetailFields(table,cont):
        # Note that we MUST supply these for the field display to work properly.
        validfields=['title','org','org_unit','mobile_phone','business_phone','email_1','email_2','birth_date','note','address-home','address-work']
        translations=['Title','Organisation','Unit','Mobile','Business Phone','Main Email','Secondary email','Birthdate','Note','Home Address','Work Address']
        labelmapping=dict(zip(validfields,translations))
        offset=0
        for prop in validfields:
            value=cont.get_property(prop)
            if value and type(value)==type('str'):  # it's a string field
                # Need to replace <BR> tags with \n and replace & with amp;
                if prop=='note':
                    value=value.replace('<br>','\n')
                    value=value.replace('<BR>','\n')
                    value=value.replace('&','amp;')
                    value=gtk.Label("<span size='large'>%s</span>" % value)   # Convert & to amp; etc
                    value.set_property("wrap",True)
                    value.set_property("wrap-mode",pango.WRAP_WORD)
                else:
                    value=gtk.Label("<span size='large'>%s</span>" % value)
                label=labelmapping.get(prop)
                contactDetails.setupContactField(label,value,table,offset)
                offset+=1
            elif value and type(value)==gobject.GBoxed: # it's got some raw data in it
                data=value.copy()
                '''
                print "CLASS: %s" % data.__class__
                print "DOC: %s" % data.__doc__
                print "GTYPE: %s" % data.__gtype__
                print "REPR: %s" % data.__repr__()
                print dir(data)
                #print "getattr: %s" % data.__getattribute__('month')  # doesn't work                
                '''
                
    @staticmethod
    def createTreeViewColumn(title,columnId,visible=True):
        ''' Creates a gtk.TreeViewColumn and then sets some needed properties '''
        column=gtk.TreeViewColumn(title,gtk.CellRendererText(),text=columnId)
        column.set_resizable=True
        column.set_visible=visible
        column.set_sort_column_id(columnId)
        return column
        