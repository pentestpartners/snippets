#!/usr/bin/env python
from bluepy.btle import Peripheral, DefaultDelegate, UUID, ADDR_TYPE_RANDOM, ADDR_TYPE_PUBLIC, Scanner
import hexdump
import binascii
import urllib2
import json
import fnmatch
from Crypto.Cipher import AES

class NotifyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print "Token obtained"
        # Try to unlock it
        mica.unlock(data)

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            if fnmatch.fnmatch(dev.addr, 'f0:?5:*'):
                print "Found Nokelock, %s, unlocking it" % (dev.getValueText(9))
                unlockMicaLock(dev.addr)

class MicaLock():
    def __init__(self):
        self.addr=""
        self.key=""
	self.apitoken=""

    def setAddr(self,addr):
        self.addr=addr
        self.p = Peripheral(self.addr, addrType=ADDR_TYPE_PUBLIC)
        self.p.setDelegate(NotifyDelegate())

    def getAddr(self):
        return self.addr

    def setKey(self,key):
        self.key=key
        self.aes=AES.new(key, AES.MODE_ECB)

    def getKey(self):
        return self.key

    def getApiToken(self):
	return self.apitoken

    def setApiToken(self, token):
	self.apitoken=token

    def getToken(self):
        message=binascii.unhexlify('060101017031321c66567559003a0a4d')
        # Start listening for notification
        self.p.writeCharacteristic(7,b'\x01\x00')
        # Send message
        self.p.writeCharacteristic(3,self.aes.encrypt(message))
        self.p.waitForNotifications(1.0)

    def unlock(self,token):
        unlockit=binascii.unhexlify('050106303030303030') + self.aes.decrypt(token)[3:7] + binascii.unhexlify('000000')
        print "Unlocking"
        self.p.writeCharacteristic(3,self.aes.encrypt(unlockit))
	self.p.disconnect()


def unlockMicaLock(addr):
    mica.setAddr(addr)
    print "Obtaining Encryption key"

    body='{"mac":"%s"}' % (addr)
    request=urllib2.Request("http://app.nokelock.com:8080/newNokelock/lock/queryDevice",data=str(body),headers={'Content-Type': 'application/json','token': mica.getApiToken()})
    response=urllib2.urlopen(request)
    apiresp=json.loads(response.read())
    deckey=apiresp['result']['lockKey']
    hexkey=''
    for i in deckey.split(","):
        a=hex(int(i))[2:].zfill(2)
        hexkey=hexkey+a
    key=binascii.unhexlify(hexkey)
    mica.setKey(key)

    # Bluetooth stuff now
    print "Obtaining BLE token"
    mica.getToken()
    
mica=MicaLock()
username="username"
password="password"
# log in
print "Getting API token"
body='{"type":19,"account":"%s","code":"%s"}' % (username,password)
request=urllib2.Request("http://app.nokelock.com:8080/newNokelock/user/loginByPassword",data=str(body),headers={'Content-Type': 'application/json'})
response=urllib2.urlopen(request)
apiresp=json.loads(response.read())
apitoken=apiresp['result']['token']
mica.setApiToken(apitoken)

scanner=Scanner(0).withDelegate(ScanDelegate())
devices=scanner.scan()
