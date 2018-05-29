#!/usr/bin/env python
from bluepy.btle import Peripheral, DefaultDelegate, UUID, ADDR_TYPE_RANDOM
import hexdump

class MyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print "Button Pressed"

p = Peripheral('FF:FF:80:02:5B:41')
p.setDelegate(MyDelegate())
print "Connected to device"

svc=p.getServiceByUUID(UUID("0000ffe0-0000-1000-8000-00805f9b34fb"))
ch=svc.getCharacteristics( UUID("0000ffe1-0000-1000-8000-00805f9b34fb"))[0]
noch=ch.getHandle()+1

p.writeCharacteristic(noch,b'\x01\x00')
while True:
    p.waitForNotifications(1.0)
