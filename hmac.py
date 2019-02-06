from burp import IBurpExtender
from burp import ISessionHandlingAction
from burp import IParameter
from java.io import PrintWriter
from datetime import datetime

import hashlib
import hmac
import base64
 
class BurpExtender(IBurpExtender, ISessionHandlingAction):
	#
	# implement IBurpExtender
	#
	def registerExtenderCallbacks(self, callbacks):
		stdout = PrintWriter(callbacks.getStdout(), True)
		self._callbacks = callbacks
		self._helpers = callbacks.getHelpers()
		callbacks.setExtensionName("HMAC Header")
		stdout.println("HMAC Header Registered OK")
		callbacks.registerSessionHandlingAction(self)
		stdout.println("Session handling started")
		return
	 
	def getActionName(self):
		return "HMAC Header"
	 
	def performAction(self, currentRequest, macroItems):
		#Update the secret key for HMAC
		Secret = "THIS-IS-A-SeCRet"

		stdout = PrintWriter(self._callbacks.getStdout(), True)
		requestInfo = self._helpers.analyzeRequest(currentRequest)
		 
		#Get URL path (the bit after the FQDN)
		urlpath = self._helpers.analyzeRequest(currentRequest).getUrl().getPath()	
		urlpath = self._helpers.urlEncode(urlpath)		
				
		#Get body
		BodyBytes = currentRequest.getRequest()[requestInfo.getBodyOffset():]
		BodyStr = self._helpers.bytesToString(BodyBytes)
		
		#Get time
		timestamp = datetime.now()
		timestamp = timestamp.isoformat() 
		 
		#Compute HMAC
		content = urlpath+BodyStr+timestamp
		stdout.println(content)
		_hmac = base64.b64encode(hmac.new(Secret, content, digestmod=hashlib.sha256).hexdigest())
		stdout.println(_hmac)
		
		#Add to headers array
		headers = requestInfo.getHeaders()
		hmacheader = "Authentication Bearer: "+_hmac+":"+timestamp
		headers.add(hmacheader)

		# Build new HTTP message with the new HMAC header
		message = self._helpers.buildHttpMessage(headers, BodyStr)
		
		# Update request with the new header and send it on its way
		currentRequest.setRequest(message)
		return