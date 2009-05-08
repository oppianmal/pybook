import bluetooth
import select

class AsyncDiscoverer(bluetooth.DeviceDiscoverer):
    
    def pre_inquiry(self):
        self.done = False
    
    def device_discovered(self, address, device_class, name):
        print "%s - %s" % (address, name)

    def inquiry_complete(self):
        self.done = True

d=AsyncDiscoverer()
d.find_devices(lookup_names=True)
readfiles=[d,]
while True:
    rfds=select.select(readfiles,[],[])[0]
    if d in rfds:
        d.process_event()
    if d.done: 
        break
    print "here?"