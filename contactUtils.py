#!/usr/bin/env python
#
# Main frame class for Contacts app
# (c)2005 Mal Minhas <mal@xosia.com>
#

import re, time
#import win32com.client	# if you want to do things with Outlook...
import cStringIO
import cPickle
import quopri	# quoted printable support
import base64	# base64 support
from logUtils import log

KEY_ID		= 'Id'			# id (from Symbian)
KEY_TYPE	= 'type'		# type
KEY_ACCESSCOUNT = 'AccessCount'		# access count
#
KEY_PREFIX	= 'prefix' 		# prefix
KEY_FIRSTNAME	= 'first name' 		# forename
KEY_MIDDLENAME	= 'middle name' 	# middlename
KEY_SURNAME	= 'last name'		# surname
KEY_SUFFIX	= 'suffix' 		# suffix
#
KEY_COMPANYNAME = 'company name'	# company name
KEY_JOBTITLE 	= 'job title'		# jobtitle
KEY_UUID	= 'uuid'		# UUID
KEY_PHONENUMBERS= 'phone numbers'	# phone numbers
KEY_PHONETYPE	= 'phonetype'		# phonetype array
KEY_PHONEVALUE  = 'value'		# phone num. value
KEY_LABEL	= 'label'		# phone num. label
KEY_ADDRESSES	= 'street addresses'	# addresses
KEY_POBOX	= 'pobox'		# 1. pobox
KEY_EXTENSION   = 'extension'		# 2. extension
KEY_STREET	= 'street'		# 3. street
KEY_CITY	= 'city'		# 4. city
KEY_STATE	= 'state'		# 5. state
KEY_ZIPCODE	= 'postal code'		# 6. zipcode
KEY_COUNTRY	= 'country'		# 7. country
KEY_EMAILS	= 'email addresses'	# emails
KEY_URLS	= 'URLs'		# urls
KEY_IMS		= 'IMs'			# IM accounts
KEY_VALUE  	= 'value'		# simpletype value
KEY_BIRTHDAY	= 'birthday'		# birthday
KEY_DATE	= 'date'		# date
KEY_RINGTONE	= 'ringtone'		# ringtone
KEY_NOTE	= 'notes'		# note
KEY_PHOTO	= 'image'		# image - binary data
KEY_MEMBERS	= 'members'		# group members
KEY_SYSTEMGRP	= 'system group'	# system group
#
VCARD_VERSION   = 'VERSION'		# version key
VCARD_UID	= 'UID'			# UID
VCARD_NAME	= 'N'			# name
VCARD_FNAME	= 'FN'			# formatted name
VCARD_ORG	= 'ORG'			# company
VCARD_JOBTITLE  = 'TITLE'		# jobtitle
VCARD_ADR  	= 'ADR'			# address
VCARD_TEL  	= 'TEL'			# telephone
VCARD_EMAIL  	= 'EMAIL'		# email
VCARD_URL  	= 'URL'			# URL
VCARD_RINGTONE  = 'X-RINGTONE'		# ringtone
VCARD_BIRTHDAY  = 'BDAY'		# birthday
VCARD_NOTE  	= 'NOTE'		# note
VCARD_PHOTO	= 'PHOTO'		# photo
#
VCARD_MOD_HOME  = 'HOME'		# home
VCARD_MOD_WORK  = 'WORK'		# work
VCARD_MOD_OTHER = 'OTHER'		# other
VCARD_MOD_PREF  = 'PREF'		# preferred
VCARD_MOD_FAX   = 'FAX'			# fax
VCARD_MOD_VOICE = 'VOICE'		# landline
VCARD_MOD_CELL  = 'CELL'		# mobile
VCARD_MOD_PAGER = 'PAGER'		# pager

class symplaContactAddress:
	def __init__(self,pobox=None,extaddr=None,street=None,city=None,region=None,zipcode=None,country=None,type=["other"]):
		# NOTE: Based on vCard 7 field address: [1:pobox, 2:extension, 3:street, 4:city, 5:region, 6:zipcode, 7:country]
		log.debug("symplaContactAddress::__init__")
		self.pobox=pobox		# field 0
		self.extaddr=extaddr		# field 1
		self.street=street		# field 2
		self.city=city			# field 3
		self.region=region		# field 4
		self.zipcode=zipcode		# field 5
		self.country=country		# field 6
		self.type=type
		
	def setAddressField(self,pobox=None,extaddr=None,street=None,city=None,region=None,zipcode=None,country=None):
		if pobox: 
			self.pobox=pobox		# field 0
		if extaddr: 
			self.extaddr=extaddr		# field 1
		if street:
			self.street=street		# field 2
		if city:
			self.city=city			# field 3
		if region:
			self.region=region		# field 4
		if zipcode:
			self.zipcode=zipcode		# field 5
		if country:
			self.country=country		# field 6
		
	def addressType(self):
		return self.type
		
	def addressParts(self):
		return ([self.pobox,self.extaddr,self.street,self.city,self.region,self.zipcode,self.country])

	def serialize(self):
		# Serialize as a dictionary consisting a list of 7 different address fields + a type
		# eg. 'd' + 's4:type' + 's4:home' + 's6:streets10:1 mystreet' + 'e'
		pieces=[]
		# TYPE
		typename=KEY_TYPE
		pieces.append('ds%s:%s' % (len(typename),typename))
		typearr=self.addressType()
		# NOTE: this should be a list with just ONE value (ie. simpletype)...
		for typestr in typearr:
			pieces.append('s%s:%s' % (len(typestr),typestr))
		# VALUES - go through all 7 fields
		if self.pobox:
			pieces.append('s%s:%s' % (len(KEY_POBOX),KEY_POBOX))
			pieces.append('s%s:%s' % (len(self.pobox),self.pobox))
		if self.extaddr:
			pieces.append('s%s:%s' % (len(KEY_EXTENSION),KEY_EXTENSION))
			pieces.append('s%s:%s' % (len(self.extaddr),self.extaddr))
		if self.street:
			pieces.append('s%s:%s' % (len(KEY_STREET),KEY_STREET))
			pieces.append('s%s:%s' % (len(self.street),self.street))
		if self.city:
			pieces.append('s%s:%s' % (len(KEY_CITY),KEY_CITY))
			pieces.append('s%s:%s' % (len(self.city),self.city))
		if self.region:
			pieces.append('s%s:%s' % (len(KEY_STATE),KEY_STATE))
			pieces.append('s%s:%s' % (len(self.region),self.region))
		if self.zipcode:
			pieces.append('s%s:%s' % (len(KEY_ZIPCODE),KEY_ZIPCODE))
			pieces.append('s%s:%s' % (len(self.zipcode),self.zipcode))
		if self.country:
			pieces.append('s%s:%s' % (len(KEY_COUNTRY),KEY_COUNTRY))
			pieces.append('s%s:%s' % (len(self.country),self.country))
		pieces.append('e')
		return ''.join(pieces)

class symplaContactPhoneNumber:
	def __init__(self,phonenumber,phonetype):
		log.debug("symplaContactPhoneNumber::__init__")
		self.phonenumber=phonenumber
		self.phonetype=phonetype
		#self.phonelabel=phonelabel
		
	def phoneType(self):
		return self.phonetype
		
	def phoneNumber(self):
		return self.phonenumber

	def serialize(self):
		# Serialize as a dictionary consisting of an array of type strings + a phone number string
		# eg. 'd' + 's9:phonetype' + 'ls4:homee' + 's5:value' + 's11:02083334444' + 'e'
		pieces=[]
		typename=KEY_PHONETYPE
		pieces.append('ds%s:%s' % (len(typename),typename))
		pieces.append('l')
		typearr=self.phoneType()
		for typestr in typearr:
			pieces.append('s%s:%s' % (len(typestr),typestr))
		pieces.append('e')
		typename=KEY_PHONEVALUE
		pieces.append('s%s:%s' % (len(typename),typename))
		number=self.phoneNumber()
		pieces.append('s%s:%s' % (len(number),number))
		pieces.append('e')
		return ''.join(pieces)

class symplaContactEmail:
	def __init__(self,email,emailtype):
		log.debug("symplaContactEmail::__init__")
		self.email=email
		self.emailtype=emailtype
		
	def emailType(self):
		return self.emailtype
		
	def emailName(self):
		return self.email

	def serialize(self):
		# Serialize as a dictionary consisting of a simple type string + an email string
		# eg. 'd' + 's4:type' + 's4:home' + 's5:value' + 's12:mickey@mouse' + 'e'
		pieces=[]
		typename=KEY_TYPE
		pieces.append('ds%s:%s' % (len(typename),typename))
		typearr=self.emailType()
		# NOTE: this should be a list with just ONE value (ie. simpletype)...
		for typestr in typearr:
			pieces.append('s%s:%s' % (len(typestr),typestr))
		typename=KEY_VALUE
		pieces.append('s%s:%s' % (len(typename),typename))
		email=self.emailName()
		pieces.append('s%s:%s' % (len(email),email))
		pieces.append('e')
		return ''.join(pieces)
		
class symplaContactUrl:
	def __init__(self,urlname,urltype):
		log.debug("symplaContactUrl::__init__")
		self.urlname=urlname
		self.urltype=urltype
		
	def urlType(self):
		return self.urltype
		
	def urlName(self):
		return self.urlname

	def serialize(self):
		# Serialize as a dictionary consisting of a simple type string + an url string
		# eg. 'd' + 's4:type' + 's4:work' + 's5:value' + 's17:http://mickey.com' + 'e'
		pieces=[]
		typename=KEY_TYPE
		pieces.append('ds%s:%s' % (len(typename),typename))
		typearr=self.urlType()
		# NOTE: this should be a list with just ONE value (ie. simpletype)...
		for typestr in typearr:
			pieces.append('s%s:%s' % (len(typestr),typestr))
		typename=KEY_VALUE
		pieces.append('s%s:%s' % (len(typename),typename))
		url=self.urlName()
		pieces.append('s%s:%s' % (len(url),url))
		pieces.append('e')
		return ''.join(pieces)

class symplaContact:
	"""
	IMPORTANT NOTE: Data is stored in the contacts model as UTF8 encoded bytestrings.
	Thus any time data is extracted for display (eg. in list ctrl or in contact view 
	panel) it MUST be converted to unicode for correct viewing...
	"""
	def __init__(self,dico=None,vcard=None):
		log.debug("symplaContact::__init__")
		self.dico=dico
		if not self.dico:
			self.dico={}
		self.currentLabel=""
		self.currentValue=""
		self.inVcard=False
		self.supportedLabels=[VCARD_VERSION,VCARD_NAME,VCARD_FNAME,VCARD_UID,VCARD_ORG,VCARD_JOBTITLE,VCARD_BIRTHDAY,VCARD_RINGTONE,VCARD_ADR,VCARD_URL,VCARD_TEL,VCARD_EMAIL,VCARD_PHOTO,VCARD_NOTE]
		if vcard:
			self.importFromVcard(vcard)
	
	###################### Single field key values #################################
	
	def id(self):
		return self.dico.get(KEY_ID)
		
	def setId(self,id):
		""" this should be the id assigned by Symbian engine """
		self.dico[KEY_ID]=id

	def type(self):
		return self.dico.get(KEY_TYPE)
		
	def setType(self,type):
		self.dico[KEY_TYPE]=type

	def forename(self):
		return self.dico.get(KEY_FIRSTNAME)
		
	def setForename(self,name):
		self.dico[KEY_FIRSTNAME]=name
		
	def surname(self):
		return self.dico.get(KEY_SURNAME)

	def setSurname(self,name):
		self.dico[KEY_SURNAME]=name

	def otherNames(self):
		return (self.dico.get(KEY_PREFIX),self.dico.get(KEY_MIDDLENAME),self.dico.get(KEY_SUFFIX))
		
	def setOtherNames(self,prefix=None,middlename=None,suffix=None):
		if prefix: 
			self.dico[KEY_PREFIX]=prefix
		if middlename: 
			self.dico[KEY_MIDDLENAME]=middlename
		if suffix: 
			self.dico[KEY_SUFFIX]=suffix
	
	def company(self):
		return self.dico.get(KEY_COMPANYNAME)

	def setCompany(self,name):
		self.dico[KEY_COMPANYNAME]=name

	def jobtitle(self):
		return self.dico.get(KEY_JOBTITLE)
		
	def setJobtitle(self,name):
		self.dico[KEY_JOBTITLE]=name
		
	def birthday(self):
		return self.dico.get(KEY_BIRTHDAY)
		
	def setBirthday(self,bday):
		self.dico[KEY_BIRTHDAY]=bday

	def ringtone(self):
		return self.dico.get(KEY_RINGTONE)
		
	def setRingtone(self,file):
		self.dico[KEY_RINGTONE]=file

	def note(self):
		return self.dico.get(KEY_NOTE)
		
	def setNote(self,note):
		self.dico[KEY_NOTE]=note

	def photo(self):
		return self.dico.get(KEY_PHOTO)
		
	def setPhoto(self,photo):
		self.dico[KEY_PHOTO]=photo

	def setPhotoFromFile(self,imagefile):
		file=open(imagefile,mode='rb')
		rawbuf=file.read(-1)	# slurp the whole file into rawbuf
		file.close()
		self.dico[KEY_PHOTO]=rawbuf

	###################### Multiple field key values ################################

	def clear(self):
		""" clears everything from contact dico 
		TODO: We're retaining the photo for the time being - we still need to add support
		to deal with resetting the photo field..."""
		photo=self.photo()
		self.dico={}
		self.setPhoto(photo)
				
	def phoneNumbers(self):
		phones=self.dico.get(KEY_PHONENUMBERS)
		if phones==None: phones=[]
		return phones

	def setPhoneNumber(self,phonenumber,type):
		# insert phone number into dico
		phs=self.dico.get(KEY_PHONENUMBERS)
		if phs==None: phs=[]
		phoneitem=symplaContactPhoneNumber(phonenumber,type)
		phs.append(phoneitem)	# append to end of list
		self.dico[KEY_PHONENUMBERS]=phs

	def emails(self):
		return self.dico.get(KEY_EMAILS)

	def setEmail(self,email,type):
		# insert email into dico
		ems=self.dico.get(KEY_EMAILS)
		if ems==None: ems=[]
		emailitem=symplaContactEmail(email,type)
		ems.append(emailitem)	# append to end of list
		self.dico[KEY_EMAILS]=ems

	def urls(self):
		return self.dico.get(KEY_URLS)

	def setUrl(self,url,type):
		# insert url into dico
		urls=self.dico.get(KEY_URLS)
		if urls==None: urls=[]
		urlitem=symplaContactUrl(url,type)
		urls.append(urlitem)	# append to end of list
		self.dico[KEY_URLS]=urls

	def addresses(self):
		return self.dico.get(KEY_ADDRESSES)
		#adds=self.dico.get(KEY_ADDRESSES)
		#if adds==None: adds=[]
		#return adds

	def setAddress(self,pobox=None,extaddr=None,street=None,city=None,region=None,zipcode=None,country=None,type=["other"]):
		# insert new full address into dico
		adds=self.dico.get(KEY_ADDRESSES)
		if adds==None: adds=[]
		addressitem=symplaContactAddress(pobox,extaddr,street,city,region,zipcode,country,type)
		adds.append(addressitem)	# append to end of list
		self.dico[KEY_ADDRESSES]=adds

	def setAddressField(self,pobox=None,extaddr=None,street=None,city=None,region=None,zipcode=None,country=None,type=["other"]):
		""" For updating address field in dico if present """
		adds=self.dico.get(KEY_ADDRESSES)
		# We only support three address fields - "other","home","work"
		if adds==None:
			adds=[]
		found=False
		for addr in adds:
			if addr.addressType()[0]==type[0]:
				# found a suitable address block in dico.  Let's update it.
				addr.setAddressField(pobox,extaddr,street,city,region,zipcode,country)
				found=True
		if not found: # create the address if it doesn't exist
			addressitem=symplaContactAddress(pobox,extaddr,street,city,region,zipcode,country,type)
			adds.append(addressitem)	# append to end of list
			self.dico[KEY_ADDRESSES]=adds

	###################### Import/Export #################################
	def importFromVcard(self,vcard):
		""" Converts passed in vcard into a contact 
		NOTES: 
		* We assume the input contains lines are terminated with \r\n since that's what 
		the vCard 2.1 spec says but we can handle lines terminated with only \n as well
		* If \r is present then that is removed using rstrip (Python chomp)
		* Split the line on presence of first : into candidate (label,value) tuple
		* If valid tuple NOT found, add to current tuple.
		* If valid tuple found, process and finish with current tuple and set new 
		valid tuple to be the new current one.
		
		"""
		lines=vcard.split('\n')
		for line in lines:
			line=line.rstrip()			# equivalent of chomp in Python
			r1=re.compile(r'([^:]*):\s*(.*)')	# non-greedy match up to first :
			match=r1.match(line)
			if match:
				# We have at least one : in the line.
				(label,value)=match.groups()		# easier to deal with the match object
				if label=="BEGIN" and value=="VCARD":
					log.debug("Found START of vCard")
					self.inVcard=True
				elif label=="END" and value=="VCARD":
					log.debug("Found END of vCard - finish here")
					self.importFieldDataFromTuple(self.currentLabel,self.currentValue)
					self.currentValue=""
					self.currentLabel=""
					self.inVcard=False
				elif self.checkIfValidFieldtype(label,value) and self.inVcard:
					# This is a valid NEW tuple - process old one first
					log.debug("Found valid tuple: \"%s\":\"%s\"" % (label,value))
					if self.currentLabel:
						self.importFieldDataFromTuple(self.currentLabel,self.currentValue)
					self.currentLabel=label
					self.currentValue=value
				else:
					# This is NOT a valid new tuple - add to old one and carry on...
					log.debug("Found invalid tuple: \"%s\"" % line)
					self.currentValue+="\r\n"+line	# need to do this to make sure QP encoding is handled properly
			else:
				# No tuple found - add to old one and carry on...
				log.debug("Found continuation value: \"%s\":\"%s\"" % (self.currentLabel,line))
				if self.currentLabel[:5]=="PHOTO":
					line=line.lstrip()	# remove leading whitespaces for PHOTO continuation line.
				self.currentValue+="\r\n"+line	# need to do this to make sure QP encoding is handled properly

	"""
	def checkIfValidFieldtype(self,label,value):
		fieldtype=label.split(';')
		if fieldtype=="N" or "VERSION" or "UID" or "ORG" or "TITLE" or "BDAY" or "TEL" or "EMAIL" or "URL" or "ADR" or "X-RINGTONE" or "PHOTO" or "NOTE":
			return True
		else:
			return False
	"""
	def checkIfValidFieldtype(self,label,value):
		fieldtype=label.split(';')
		for field in self.supportedLabels:
			#print "field is \"%s\", fieldtype is \"%s\"" % (field,fieldtype)
			if field==fieldtype[0]:
				return True
		return False
	
	def importFieldDataFromTuple(self,label,value):
		type=[]
		modifiers=[]
		isqpdecode=jpge=b64decode=utf8=isfile=False
		log.debug("%s:%s" % (label,value))
		# STEP 1: pick up all label modifiers.  eg. "HOME","WORK","ENCODING=..."
		r1=re.compile(r'([^;]*);\s*(.*)')		# non-greedy match up to first ; to pick up basic fieldtype
		match=r1.match(label)
		if match:
			(fieldtype,mods)=match.groups(0)	# easier to deal with the match object
			modifiers=mods.split(';')
		else:
			fieldtype=label				# there are no modifiers
		log.debug("Found FIELD \"%s\", MODIFIERS %s,\n\tVALUE \"%s\"" % (fieldtype,modifiers,value))
		
		# STEP 2: Look at modifiers for this tuple
		for modifier in modifiers:
			# Pick up all the different modifiers we can have here
			if modifier==VCARD_MOD_HOME:
				type.append("home")
			elif modifier==VCARD_MOD_WORK:
				type.append("work")
			elif modifier==VCARD_MOD_OTHER:
				type.append("other")
			elif modifier==VCARD_MOD_FAX:
				type.append("fax")
			elif modifier==VCARD_MOD_VOICE:
				type.append("voice")
			elif modifier==VCARD_MOD_CELL:
				type.append("mobile")
			elif modifier==VCARD_MOD_PAGER:
				type.append("pager")
			elif modifier==VCARD_MOD_PREF:
				type.append("pref")
			elif modifier=="ENCODING=QUOTED-PRINTABLE" or modifier=="QUOTED-PRINTABLE":
				qpdecode=True
			elif modifier=="TYPE=JPEG":
				jpeg=True
			elif modifier=="ENCODING=BASE64" or modifier=="BASE64":
				b64decode=True
			elif modifier=="CHARSET=UTF8":
				utf8=True
			elif modifier=="TYPE=FILE" or "FILE":
				isfile=True
			else:
				raise "Unknown modifier %s from %s" % (modifier,modifiers)
			
		# STEP 3: fieldtype will hold the basic vcard field
		value=quopri.decodestring(value)
		if fieldtype==VCARD_VERSION:
			log.debug("Found vCARD VERSION %s" % value)
		elif fieldtype==VCARD_UID:
			log.debug("Found vCARD UID %s" % value)
		elif fieldtype==VCARD_NAME:
			namefields=value.split(';')			
			log.debug("Found vCARD N %s" % namefields)
			forename=namefields[1]
			surname=namefields[0]
			self.setForename(forename)
			self.setSurname(surname)
			if len(namefields)==5:
				middlename=namefields[2]
				prefix=namefields[3]
				suffix=namefields[4]
				self.setOtherNames(prefix,middlename,suffix)
		elif fieldtype==VCARD_FNAME:
			log.debug("Found vCARD FN %s" % value)			
		elif fieldtype==VCARD_ORG:
			org=""
			orgfields=value.split(';')
			log.debug("Found vCARD ORG %s" % orgfields)
			for orgfield in orgfields:
				if orgfield:
					org+=orgfield
			self.setCompany(org)
		elif fieldtype==VCARD_JOBTITLE:
			log.debug("Found vCARD TITLE %s" % value)
			self.setJobtitle(value)
		elif fieldtype==VCARD_BIRTHDAY:
			log.debug("Found vCARD BDAY %s" % value)
			self.setBirthday(value)
		elif fieldtype==VCARD_TEL:
			log.debug("Found vCARD TEL %s" % value)
			self.setPhoneNumber(value,type)
		elif fieldtype==VCARD_EMAIL:
			log.debug("Found vCARD EMAIL %s" % value)
			self.setEmail(value,type)
		elif fieldtype==VCARD_URL:
			log.debug("Found vCARD URL %s" % value)
			self.setUrl(value,type)
		elif fieldtype==VCARD_ADR:
			# IMPORTANT: we are delaying the processing of addr fields until
			# we register a change in label.
			adrfields=value.split(';')
			log.debug("Found vCARD ADR %s" % adrfields)
			self.setAddress(adrfields[0],adrfields[1],adrfields[2],adrfields[3],adrfields[4],adrfields[5],adrfields[6],type)
		elif fieldtype==VCARD_RINGTONE:
			# The value here should be a file
			if isfile:
				self.setRingtone(value)
			else:
				raise "Cannot process an inline ringtone"
		elif fieldtype==VCARD_NOTE:
			# Need to cope with multi-line fields....
			log.debug("Found vCARD NOTE %s" % value)
			self.setNote(value)
		elif fieldtype==VCARD_PHOTO:
			value=self.currentValue[2:]		# strip leading \r\n from value
			value+="\r\n"				# add trailing \r\n to value
			log.debug("Found vCARD PHOTO - decoding from base64...: \"%s\"" % value)
			# Decode raw base64 data...
			rawdata=base64.b64decode(value)
			self.setPhoto(rawdata)
		else:
			raise "Unknown fieldtype %s" % fieldtype
	
	def exportAsVcard(self):
		""" Converts current contact into a vCard 2.1 format vcard string for export """
		isqp=""
		str="BEGIN:VCARD\r\nVERSION:2.1\r\n"
		if self.surname() or self.forename() or self.otherNames():
			qpsurname=qpforename=qpmiddlename=qpprefix=qpsuffix=""
			prefix=self.otherNames()[0]
			middlename=self.otherNames()[1]
			suffix=self.otherNames()[2]
			if prefix:
				qpprefix=quopri.encodestring(prefix)
				if qpprefix != prefix:
					isqp=";ENCODING=QUOTED-PRINTABLE"
			if self.forename():
				qpforename=quopri.encodestring(self.forename())
				if qpforename != self.forename():
					isqp=";ENCODING=QUOTED-PRINTABLE"
			if middlename:
				qpmiddlename=quopri.encodestring(middlename)
				if qpmiddlename != middlename:
					isqp=";ENCODING=QUOTED-PRINTABLE"
			if self.surname():
				qpsurname=quopri.encodestring(self.surname())
				if qpsurname != self.surname():
					isqp=";ENCODING=QUOTED-PRINTABLE"
			if suffix:
				qpsuffix=quopri.encodestring(suffix)
				if qpsuffix != suffix:
					isqp=";ENCODING=QUOTED-PRINTABLE"
			str+="N%s:%s;%s;%s;%s;%s\r\n" % (isqp,qpsurname,qpforename,qpmiddlename,qpprefix,qpsuffix)
			isqp=""
		if self.company():
			qpcompany=quopri.encodestring(self.company())
			if qpcompany != self.company():
				isqp=";ENCODING=QUOTED-PRINTABLE"
			str+="ORG%s:%s\r\n" % (isqp,qpcompany)
			isqp=""
		if self.jobtitle():
			qpjobtitle=quopri.encodestring(self.jobtitle())
			if qpjobtitle != self.jobtitle():
				isqp=";ENCODING=QUOTED-PRINTABLE"
			str+="TITLE%s:%s\r\n" % (isqp,qpjobtitle)
			isqp=""
		#--------------------- Start Multi-fields -------------------------------
		if self.phoneNumbers():
			for i in self.phoneNumbers():
				typefield=self.exportTypefield(i.phoneType())
				qpphonenumber=quopri.encodestring(i.phoneNumber())
				if qpphonenumber != i.phoneNumber():
					isqp=";ENCODING=QUOTED-PRINTABLE"					
				str+="TEL%s%s:%s\r\n" % (typefield,isqp,qpphonenumber)
				isqp=""
		if self.emails():
			for i in self.emails():
				typefield=self.exportTypefield(i.emailType())
				qpemail=quopri.encodestring(i.emailName())
				if qpemail != i.emailName():
					isqp=";ENCODING=QUOTED-PRINTABLE"
				str+="EMAIL%s%s:%s\r\n" % (typefield,isqp,qpemail)
				isqp=""
		if self.urls():
			for i in self.urls():
				typefield=self.exportTypefield(i.urlType())
				qpurl=quopri.encodestring(i.urlName())
				if qpurl != i.urlName():
					isqp=";ENCODING=QUOTED-PRINTABLE"
				str+="URL%s%s:%s\r\n" % (typefield,isqp,qpurl)
				isqp=""
		if self.addresses():
			for i in self.addresses():
				typefield=self.exportTypefield(i.addressType())
				adr=""
				for p in i.addressParts():
					if p:
						qppart=quopri.encodestring(p)
						if qppart != p:
							isqp=";ENCODING=QUOTED-PRINTABLE"
						adr+=qppart+";"
					else:
						adr+=";"
				# Remove trailing ; - we don't need that
				leng=len(adr)
				adr=adr[0:leng-1]
				str+="ADR%s%s:%s\r\n" % (typefield,isqp,adr)
				isqp=""
		#--------------------- End Multi-fields ------------------------------
		if self.birthday():
			str+="BDAY:%s\r\n" % self.birthday()
		if self.note():
			#print "NOTE field is set to \"%s\"" % self.note()
			qpnote=quopri.encodestring(self.note())
			#print "QP NOTE field is set to \"%s\"" % qpnote
			if qpnote != self.note():
				isqp=";ENCODING=QUOTED-PRINTABLE"
			str+="NOTE%s:%s\r\n" % (isqp,qpnote)
			isqp=""
		if self.photo():
			b64photo=base64.b64encode(self.photo())
			# TODO: manipulate this info to print properly (line length 64 etc.)
			str+="PHOTO;TYPE=JPEG;ENCODING=BASE64:\r\n%s\r\n" % self.ib64lines(b64photo)
		str+="END:VCARD\r\n"
		return str

	def exportTypefield(self,typearr):
		typefield=""
		for t in typearr:
			if t=="home":
				typefield+=";HOME"
			elif t=="work":
				typefield+=";WORK"
			elif t=="other":
				typefield+=";OTHER"
			elif t=="voice":
				typefield+=";VOICE"
			elif t=="pager":
				typefield+=";PAGER"
			elif t=="pref":
				typefield+=";PREF"
			elif t=="fax":
				typefield+=";FAX"
			elif t=="mobile":
				typefield+=";CELL"
		return typefield
		
	def ib64lines(self,input,maxlinelen=64):
		""" input is a whole slurped base64 encoded photo 
		output should be reorg'd to have justified lines etc.
		"""
		output=""
		offset=0
		lenToCome=len(input)
		while lenToCome>0:
			if lenToCome<maxlinelen:
				output+='    '+input[offset:offset+lenToCome]+'\r\n'
				lenToCome=0
			else:
				output+='    '+input[offset:offset+maxlinelen]+'\r\n'
				lenToCome-=maxlinelen
				offset+=maxlinelen
		return output;

	###################### Other utilities #################################
	def serialize(self):
		# This method will serialize the contents of the contact as an
		# iPhone compliant text string.
		pieces=[]
		pieces.append('d')
		for key,value in self.dico.items():
			# STEP 1: Serialize KEY
			pieces.append('s%s:%s' % (len(key),key))
			# STEP 2: Serialize VALUE
			if key==KEY_PHONENUMBERS:	# array of dictionary...
				arr=value
				pieces.append('l')		# start of array
				for ph in arr:			# process each dictionary
					pieces.append(ph.serialize())
				pieces.append('e')		# end of array
				#
			elif key==KEY_EMAILS:		# array of dictionary...
				arr=value
				pieces.append('l')		# start of array
				for em in arr:			# process each dictionary
					pieces.append(em.serialize())
				pieces.append('e')		# end of array
				#
			elif key==KEY_URLS:		# array of dictionary...
				arr=value
				pieces.append('l')		# start of array				
				for url in arr:			# process each dictionary
					pieces.append(url.serialize())
				pieces.append('e')		# end of array
				#
			elif key==KEY_ADDRESSES:	# array of dictionary...
				arr=value
				pieces.append('l')		# start of array
				for addr in arr:		# process each dictionary
					pieces.append(addr.serialize())
				pieces.append('e')		# end of array
				#
			elif key==KEY_BIRTHDAY:		# dictionary with a single date in it				
				# Serialize as a dictionary consisting of a simple type string + a date string
				# eg. 'd' + 's4:date' + 's8:25/12/03' + 'e'
				pieces.append('d')
				typename=KEY_DATE				
				pieces.append('s%s:%s' % (len(typename),typename))				
				pieces.append('s%s:%s' % (len(value),value))
				pieces.append('e')
			elif key==KEY_PHOTO:		# raw image buffer
				# We are now assuming that the input here is just raw binary data for conversion to .jpg for viewing
				pieces.append('r%s:%s' % (len(value),value))
			else: # Normal string
				pieces.append('s%s:%s' % (len(value),value))
		pieces.append('e')
		return ''.join(pieces)

	def deserializeGroup(self,input,listtype):
		# For deserializing a 'd'+'ls2:58s2:34e'+'s12:system groups1:0s4:names6:Onlines4:types5:group'+'e' sequence
		offset=0
		count=0
		memberlist=[]
		groupid=0
		name=""
		#log.debug("\"%s\"" % input[offset:])
		if input[:1]=='l':
			log.debug("Found start of %s group member list" % listtype)
			offset+=1
			moretocome=1;
			while moretocome:
				if input[offset:offset+1]=='e':
					log.debug("Found end of %s group member list" % listtype)
					offset+=1
					moretocome=0
				else:
					(val,offs)=self.deserializeString(input[offset:])
					log.debug("MEMBER=%s" % val)
					memberlist.append(val)
					offset+=offs
			# Now we can process the rest...
			moretocome=1
			while moretocome:
				# STEP 1: Deserialize the KEY - expecting 's%s:%s'
				(key,offs)=self.deserializeString(input[offset:])
				offset+=offs
				(type,offs)=self.deserializeString(input[offset:])
				if key=="name":
					name=type
				if key=="Id":
					groupid=type
				#log.debug("KEY=%s, VALUE=%s" % (key,type))
				offset+=offs
				if input[offset:offset+1]=='e':
					moretocome=0
					#log.debug("\"%s\"" % input[offset:])
		else:
			log.debug("Invalid %s input stream 4" % listtype)
			raise "Invalid %s input stream 4" % listtype
		return (memberlist,groupid,name,offset)
		
	def deserializeMultivalue(self,input,listtype):
		# For deserializing a 'l'+'d'+'s4:types4:home'+'s5:values16:mickey@mouse.com'+'e'+'e' sequence
		offset=0
		count=0
		elist=[]
		if input[:1]=='l':
			log.debug("Found start of %s list" % listtype)
			dictionaries=1
			offset+=1
			while dictionaries:
				if input[offset:offset+1]=='d':
					offset+=1
					count+=1
					moretocome=1
					type=''
					value=''
					label=''
					log.debug("Found start of %s dictionary %d" % (listtype,count))
					while moretocome:
						# STEP 1: Deserialize the KEY - expecting 's%s:%s'
						(key,offs)=self.deserializeString(input[offset:])
						offset+=offs
						if key==KEY_TYPE:
							(type,offs)=self.deserializeString(input[offset:])
							log.debug("KEY=%s, VALUE=%s" % (key,type))
						elif key==KEY_VALUE:
							(value,offs)=self.deserializeString(input[offset:])
							log.debug("KEY=%s, VALUE=%s" % (key,value))
						elif key==KEY_LABEL:
							(label,offs)=self.deserializeString(input[offset:])
							log.debug("KEY=%s, VALUE=%s" % (key,value))							
						else:
							log.error("Invalid %s input stream 1.  key=%s" % (listtype,key))
							raise "Invalid %s input stream 1" % listtype
						offset+=offs
						if input[offset:offset+1]=='e':
							moretocome=0
							offset+=1
							log.debug("Found end of %s dictionary %d" % (listtype,count))
					# We processed full email - now create our email
					if listtype=="emails":
						em=symplaContactEmail(value,[type])
						elist.append(em)
					elif listtype=="urls":
						url=symplaContactUrl(value,[type])
						elist.append(url)
				elif input[offset:offset+1]=='e':
					log.debug("Found end of %s list" % listtype)
					offset+=1
					dictionaries=0
				else:
					log.debug("Invalid %s input stream 2" % listtype)
					raise "Invalid %s input stream 2" % listtype
			count=len(elist)
			log.debug("Processed %d %s in all" % (count,listtype))
		else:
			log.debug("Invalid %s input stream 3" % listtype)
			raise "Invalid %s input stream 3" % listtype
		return (elist,offset)
		
	def deserializeAddresses(self,input):		
		# For deserializing a 'l' + 'd' + 's4:type' + 's4:home' + 's5:value' + 'ls6:streets10:1 mystreete' + 'e' + 'e'
		offset=0
		count=0
		addrs=[]
		if input[:1]=='l':
			log.debug("Found start of address list")
			dictionaries=1
			offset+=1
			while dictionaries:
				if input[offset:offset+1]=='d':
					offset+=1
					count+=1
					moretocome=1
					addrtype=''
					pb=ext=st=cty=zip=reg=cntry=None
					log.debug("Found start of address dictionary %d" % count)
					while moretocome:
						# STEP 1: Deserialize the KEY - expecting 's%s:%s'
						(key,offs)=self.deserializeString(input[offset:])
						offset+=offs
						if key==KEY_TYPE:
							(addrtype,offs)=self.deserializeString(input[offset:])
							log.debug("KEY=%s, VALUE=%s" % (key,addrtype))
						elif key==KEY_POBOX:
							(pb,offs)=self.deserializeString(input[offset:])
							log.debug("KEY=%s, POBOX=%s" % (key,pb))
						elif key==KEY_EXTENSION:
							(ext,offs)=self.deserializeString(input[offset:])
							log.debug("KEY=%s, EXTENSION=%s" % (key,ext))
						elif key==KEY_STREET:
							(st,offs)=self.deserializeString(input[offset:])
							log.debug("KEY=%s, STREET=%s" % (key,st))
						elif key==KEY_CITY:
							(cty,offs)=self.deserializeString(input[offset:])
							log.debug("KEY=%s, CITY=%s" % (key,cty))
						elif key==KEY_STATE:
							(reg,offs)=self.deserializeString(input[offset:])
							log.debug("KEY=%s, STATE=%s" % (key,reg))
						elif key==KEY_ZIPCODE:
							(zip,offs)=self.deserializeString(input[offset:])
							log.debug("KEY=%s, ZIPCODE=%s" % (key,zip))
						elif key==KEY_COUNTRY:
							(cntry,offs)=self.deserializeString(input[offset:])
							log.debug("KEY=%s, COUNTRY=%s" % (key,cntry))							
						else:
							log.error("Invalid address input stream 1 %s" % key)
							raise "Invalid address input stream 1"
						offset+=offs
						if input[offset:offset+1]=='e':
							moretocome=0
							offset+=1
							log.debug("Found end of address dictionary %d" % count)
					# We processed full address - now create our symplaContactAddress
					#def __init__(self,pobox=None,street=None,city=None,zipcode=None,region=None,country=None,addresstype="other"):
					addr=symplaContactAddress(pobox=pb,extaddr=ext,street=st,city=cty,region=reg,zipcode=zip,country=cntry,type=[addrtype])
					addrs.append(addr)				
				elif input[offset:offset+1]=='e':
					log.debug("Found end of address list")
					offset+=1
					dictionaries=0
				else:
					log.debug("Invalid address input stream 2")
					raise "Invalid address input stream 2"
			count=len(addrs)
			log.debug("Processed %d addresses in all" % count)
		else:
			log.debug("Invalid address input stream 3")
			raise "Invalid address input stream 3"
		return (addrs,offset)

	def deserializePhonetype(self,input):
		# For deserializing a 'ls4:homes6:mobilee' list sequence
		offset=0
		count=0
		phonetype=[]
		if input[:1]=='l':
			log.debug("Found start of phone type list")
			moretocome=1
			offset+=1
			while moretocome:
				# STEP 1: Deserialize the KEY - expecting 's%s:%s'
				(type,offs)=self.deserializeString(input[offset:])
				offset+=offs
				phonetype.append(type)
				if input[offset:offset+1]=='e':
					moretocome=0
					offset+=1
					log.debug("Found end of phonetype list")
			count=len(phonetype)
			log.debug("Processed %d phonetype fields for this phone number: %s" % (count,phonetype))
		else:
			log.debug("Invalid phone type input stream")
			raise "Invalid phone type input stream"
		return (phonetype,offset)
			
	def deserializePhoneNumbers(self,input):
		# For deserializing a 'l'+'d'+'s9:phonetypels4:homes6:mobilee'+'s5:values11:02087456746'+'s5:labels5:label'+'e'+'e' sequence
		# Return end offset into input + list of parsed symplaContactPhoneNumbers
		count=0;
		offset=0
		phoneNumbers=[]
		if input[:1]=='l':
			log.debug("Found start of phone number list")
			offset+=1
			dictionaries=1
			while dictionaries:
				if input[offset:offset+1]=='d':
					offset+=1
					count+=1
					moretocome=1
					phtype=[]
					label=''
					value=''
					log.debug("Found start of phone dictionary %d" % count)
					while moretocome:
						# STEP 1: Deserialize the KEY - expecting 's%s:%s'
						(key,offs)=self.deserializeString(input[offset:])
						offset+=offs
						# STEP 2: Deserialize the VALUE - depends on the key
						#log.debug("KEY=%s" % key)
						if key==KEY_PHONETYPE:
							(phtype,offs)=self.deserializePhonetype(input[offset:])
						elif key==KEY_PHONEVALUE:
							(value,offs)=self.deserializeString(input[offset:])
							log.debug("KEY=%s, VALUE=%s" % (key,value))
						elif key==KEY_LABEL:
							(label,offs)=self.deserializeString(input[offset:])
							log.debug("KEY=%s, VALUE=%s" % (key,label))
						else:
							log.error("Invalid phone number input stream 1")
							raise "Invalid phone number input stream 1"
						offset+=offs
						if input[offset:offset+1]=='e':
							moretocome=0
							offset+=1
							log.debug("Found end of phone dictionary %d" % count)
					# We processed full phoneNumber - now create our symplaContactPhoneNumber
					ph=symplaContactPhoneNumber(value,phtype)
					phoneNumbers.append(ph)
				elif input[offset:offset+1]=='e':
					log.debug("Found end of phone number list")
					offset+=1
					dictionaries=0
				else:
					log.debug("Invalid phone number input stream 2")
					raise "Invalid phone number input stream 2"
			count=len(phoneNumbers)
			log.debug("Processed %d phone numbers in all" % count)
		else:
			log.debug("Invalid phone number input stream 3")
			raise "Invalid phone number input stream 3"
		return (phoneNumbers,offset)

	def deserializeBirthday(self,input):
		# For deserializing a 'ds%s:%ss%s:%se' sequence
		log.debug("Attempting to deserialize birthday \"%s\"" % input[:20])
		offset=0
		if input[:1]=='d':
			log.debug("Found start of birthday dictionary")
			offset+=1
			(type,offs)=self.deserializeString(input[offset:])
			offset+=offs
			(datebuf,offs)=self.deserializeString(input[offset:])
			offset+=offs
			if input[offset:offset+1]=='e':
				offset+=1
				log.debug("Found end of birthday dictionary")
			else:
				log.error("Invalid birthday:\n%s" % input)
				raise "problem deserializing birthday data"
		else:
			log.error("Invalid birthday:\n%s" % input)
			raise "problem deserializing birthday data"
		return (datebuf,offset)
		
	def deserializeImage(self,input):
		# For deserializing a 'r%s:%s' sequence
		offset=0
		r1=re.compile(r'r([^:]*):(.*)')
		m=r1.match(input[offset:])
		if m:
			buflen=int(m.groups()[0])
			offset+=1+len(m.groups()[0])+1
			buffer=input[offset:offset+buflen]
			offset+=len(buffer)
			log.debug("**** Deserialized image of len %s bytes ****" % buflen)
		else:
			log.error("Invalid image:\n%s" % input)
			raise "problem deserializing image data"
		return (buffer,offset)
		
	def deserializeString(self,input):
		# For deserializing a 's%s:%s' sequence 
		offset=0
		r1=re.compile(r's([^:]*):(.*)')
		m=r1.match(input[offset:])
		if m:
			strlen=int(m.groups()[0])
			offset+=1+len(m.groups()[0])+1
			str=input[offset:offset+strlen]
			offset+=len(str)
		else:	
			log.error("Invalid string:\n%s" % input[offset:])
			raise "problem deserializing string"
		return (str,offset)

	def deserialize(self,input):
		# "How long is a piece of string?"
		# This method will deserialize the contents of the input string
		# and use it to populate the contact details
		# NOTE: This method will throw exceptions if the input cannot be handled.
		offset=0
		inputlen=len(input)
		if input[:1]=='d' and input[-1:]=='e':
			log.debug("Found start of contact dictionary")
			offset+=1
			moretocome=inputlen-offset
			while moretocome:
				offs=0
				# STEP 1: Deserialize the KEY - expecting 's%s:%s'
				(key,offs)=self.deserializeString(input[offset:])
				offset+=offs
				# STEP 2: Deserialize the VALUE - could be multivalue or not, depends on the key
				#log.debug("KEY=%s, REMAINDER=%s" % (key,input[offset:offset+10]+'...'))
				if key==KEY_PHONENUMBERS:  	# expecting an array of dictionary...
					phs=()
					(phs,offs)=self.deserializePhoneNumbers(input[offset:])
					self.dico[KEY_PHONENUMBERS]=phs
				elif key==KEY_EMAILS:
					ems=()
					(ems,offs)=self.deserializeMultivalue(input[offset:],"emails")
					self.dico[KEY_EMAILS]=ems
				elif key==KEY_URLS:
					urls=()
					(urls,offs)=self.deserializeMultivalue(input[offset:],"urls")
					self.dico[KEY_URLS]=urls
				elif key==KEY_ADDRESSES:
					adds=()
					(adds,offs)=self.deserializeAddresses(input[offset:])
					self.dico[KEY_ADDRESSES]=adds
				elif key==KEY_BIRTHDAY:
					(date,offs)=self.deserializeBirthday(input[offset:])
					self.dico[key]=date
				elif key==KEY_PHOTO:
					image=''
					(image,offs)=self.deserializeImage(input[offset:])
					self.dico[KEY_PHOTO]=image
				elif key==KEY_MEMBERS:	# For groups, expecting a 's%s:%s' sequence 
					members=()
					(members,groupid,name,offs)=self.deserializeGroup(input[offset:],"members")
					log.debug("KEY=%s, VALUE=%s" % (key,members))
					# IMPORTANT: we are not processing groups currently so we comment this line out:
					self.dico[KEY_MEMBERS]=members
					self.dico[KEY_FIRSTNAME]=name
					self.dico[KEY_ID]=groupid
					self.dico[KEY_TYPE]="group"
					log.warning("group \"%s\" of id %s with members %s found and ignored" % (name,id,members))
				else:	# expecting a 's%s:%s' sequence 
					(value,offs)=self.deserializeString(input[offset:])
					self.dico[key]=value
					log.debug("KEY=%s, VALUE=%s" % (key,value))
				offset+=offs
				#log.debug("KEY=%s, REMAINDER=%s" % (key,input[offset:offset+10]+'...'))
				if input[offset:offset+1]=='e':
					moretocome=0
					offset+=1
					log.debug("Found end of contact dictionary")
		else:
			log.error("Invalid input stream")
			raise "Invalid contact dictionary"
		return offset

	def dump(self):
		log.debug("-------- %s --------" % self.name())
		for key,value in self.dico.items():
			if key==KEY_PHONENUMBERS:	# array of values
				arr=value
				log.debug("\tphone numbers:")
				for ph in arr:
					tuplestr='\t\t%s:%s' % (ph.phoneNumber(),ph.phoneType())
					log.debug(tuplestr)
			elif key==KEY_EMAILS:	# array of values...
				arr=value
				log.debug("\temails:")
				for em in arr:
					tuplestr='\t\t%s:%s' % (em.emailName(),em.emailType())
					log.debug(tuplestr)
			elif key==KEY_URLS:	# array of values...
				arr=value
				log.debug("\turls:")
				for url in arr:
					tuplestr='\t\t%s:%s' % (url.urlName(),url.urlType())
					log.debug(tuplestr)
			elif key==KEY_ADDRESSES:	# array of values...
				arr=value
				log.debug("\taddresses:")
				for add in arr:
					tuplestr='\t\t%s:%s' % (add.addressParts(),add.addressType())
					log.debug(tuplestr)
			elif key==KEY_PHOTO:
				tuplestr='\t%s:%s...%s' % (key,value[:20],value[-20:])				
				log.debug(tuplestr)
			else:
				tuplestr='\t%s:%s' % (key,value)
				log.debug(tuplestr)

	def name(self):
		prefix=self.dico.get(KEY_PREFIX)
		firstname=self.dico.get(KEY_FIRSTNAME)
		middlename=self.dico.get(KEY_MIDDLENAME)
		surname=self.dico.get(KEY_SURNAME)
		suffix=self.dico.get(KEY_SUFFIX)
		companyname=self.dico.get(KEY_COMPANYNAME)
		name=''
		if prefix:
			name+=prefix+" "
		if firstname:
			name+=firstname+" "
		if middlename:
			name+=middlename+" "
		if surname:
			name+=surname+" "
		if suffix:
			name+=suffix+" "
		if name!='':
			name=name[:len(name)-1]	# get rid of trailing " "
		elif companyname:	# set to company name
			name+=companyname
		else:
			name="(none)"
		return name
		
		"""
		if firstname and surname:
			name+=firstname + " " + surname
		elif firstname:
			name=firstname
		elif surname:
			name=surname
		elif companyname:
			name=companyname
		else:
			name="(none)"
		return name
		"""

if __name__ == '__main__':
	#
	# Basic tests
	log.debug("create some fake friends")
	tom=symplaContact({KEY_FIRSTNAME:"tom",KEY_SURNAME:"trojan",KEY_COMPANYNAME:"eurotunnel"})
	tom.setNote("This is a note")
	tom.setBirthday("25/12/73")
	dick=symplaContact({KEY_FIRSTNAME:"dick",KEY_SURNAME:"trojan",KEY_COMPANYNAME:"eurotunnel"})
	harry=symplaContact({KEY_FIRSTNAME:"harry",KEY_SURNAME:"trojan",KEY_COMPANYNAME:"eurotunnel"})
	log.debug("---- handle Tom ---")
	tom.dump()
	name=tom.name()
	log.debug("Tom's name: \"%s\"" % name)	
	log.debug("---- handle Dick ---")
	dick.dump()
	name=dick.name()
	log.debug("Dick's name: \"%s\"" % name)	
	log.debug("---- handle Harry ---")
	harry.dump()	
	name=harry.name()
	log.debug("Harry's name: \"%s\"" % name)
	
	# Testing empty contact
	sally=symplaContact()
	log.debug("---- handle Sally ---")
	sally.dump()
	name=sally.name()
	log.debug("Sally's name: \"%s\"" % name)
	sally.setCompany("EuroBubble")
	name=sally.name()
	log.debug("Sally's name: \"%s\"" % name)
	sally.setId("74")
	sally.setType("contact")
	sally.setForename("Sally")
	sally.setSurname("Jones")
	sally.setPhoneNumber("020893939393",["home"])
	sally.setPhoneNumber("020874747474",["work","mobile"])
	sally.setEmail("sally@home.com",["home"])
	sally.setEmail("sally@work.com",["work"])
	sally.setUrl("http://www.sally.home.com",["home"])
	sally.dump()
	name=sally.name()
	phonenums=sally.phoneNumbers()
	log.debug("Phone numbers only:")
	for i in phonenums:
		log.debug("\t%s:%s" % (i.phoneNumber(),i.phoneType()))
	emails=sally.emails()
	log.debug("Emails only:")
	for i in emails:
		log.debug("\t%s:%s" % (i.emailName(),i.emailType()))
	addresses=sally.addresses()
	log.debug("Addresses only:")
	if addresses:
		for i in addresses:
			log.debug("\t%s:%s" % (i.addressParts(),i.addressType()))
	sally.setAddress(pobox="sally pobox",extaddr="sally house name",city="sally city",country="uk",type=["home"])
	log.debug("Addresses only:")
	addresses=sally.addresses()
	for i in addresses:
		log.debug("\t%s:%s" % (i.addressParts(),i.addressType()))	
	log.debug("Sally's name: \"%s\"" % name)
	sally.dump()

	# Testing serialization-deserialization
	log.debug("---- handle Johnny ---")
	johnny=symplaContact()
	johnny.setId("74")
	johnny.setType("contact")
	johnny.setForename("John")
	johnny.setSurname("Jones")
	johnny.setPhoneNumber("020893939393",["home"])
	johnny.setPhoneNumber("020874747474",["work","mobile"])
	johnny.setEmail("johnny@vegas.com",["work"])
	johnny.setEmail("johnny@vegas2.com",["home"])
	johnny.setEmail("johnny@vegas3.com",["other"])
	johnny.setUrl("http://www.johnnyvegas.com",["home"])
	johnny.setBirthday("25/01/03")
	# Handling image: need to read the image file into a buffer
	#johnny.setPhotoFromFile("image.jpg")
	johnny.setAddress(pobox="P.O.Box 100",extaddr="Suite 101",street="35 Gibson Street",city="London",region="GLC",zipcode="Z24 3BH",country="uk",type=["home"])
	johnny.dump()
	str=cPickle.dumps(johnny.dico)
	#log.debug("Result of dumps of johnny:\n%s" % str)
	# Can't get pickling to work....  Let's try our own serialization routine
	str=johnny.serialize()
	if len(str) <800:
		log.debug("johnny serialized:\n%s" % str)		
	else:
		log.debug("johnny serialized:\n%s" % str[:150]+'...'+str[-150:])
	johnny1=symplaContact()
	log.debug("about to deserialize johnny...")	
	proclen=johnny1.deserialize(str)
	johnny1.dump()
	# Check that processed len is the same as len of serialized data	
	if proclen==len(str):
		log.debug("Successfully processed all %d chars in serialized input for johnny" % proclen)
	else:
		log.error("Only processed %d chars from a length of %d" % (proclen,len(str)))
		raise "FAILED test 1"
	str1=johnny1.serialize()
	if len(str) <800:
		log.debug("johnny deserialized then serialized again:\n%s" % str1)
	else:
		log.debug("johnny deserialized then serialized again:\n%s" % str1[:150]+'...'+str1[-150:])
	if len(str)==len(str1):
		log.debug("johnny PASSED deserialization-serialization identity check (length of serialized strings identical)")
	else:
		log.error("Differences found in johnny deserialization-serialization identity check")
		raise "FAILED test 2"
	johnny1.deserialize(str1)
	str2=johnny1.serialize()
	if str1==str2:
		log.debug("johnny PASSED deserialization-serialization identity check (str1 is equal to str2)")
	else:
		log.error("Differences found in johnny deserialization-serialization identity check")
		raise "FAILED test 3"
	
	log.debug("---- handle Andy ---")
	str="ds16:street addresseslds7:countrys2:UKs4:citys7:Hanwells6:streets16:40 St Marks Roads4:types4:homeees15:email address\
eslds4:types4:homes5:values21:andy@andymcewan.co.ukeds4:types4:works5:values14:andy@xosia.comees13:phone numberslds9:phonetypels6:\
mobilees5:values13:+447769673611eds9:phonetypels4:homes5:voicees5:values11:02085799727ees12:company names5:Xosias10:first names4:A\
ndys9:last names6:McEwans11:AccessCounts1:1s4:uuids37:337eada00cb28390-00e0d6beb1c44ff0-105s2:Ids3:105s4:types7:contacte"
	andy=symplaContact()
	proclen=andy.deserialize(str)
	if proclen==len(str):
		log.debug("Successfully processed all %d chars in serialized input for Andy" % proclen)
	else:
		log.error("Only processed %d chars from a length of %d" % (proclen,len(str)))
		raise "FAILED test 4"
	andy.dump()
	
	# Testing vcard exporter
	log.debug("---- vCard import and export ---:")
	mickey=symplaContact()
	mickey.setId("74")
	mickey.setType("contact")
	mickey.setForename("Mickey")
	mickey.setSurname("Mouse")
	mickey.setCompany("Disney")
	mickey.setJobtitle("Clown")
	mickey.setPhoneNumber("020893939393",["home"])
	mickey.setPhoneNumber("020874747474",["work","mobile"])
	mickey.setEmail("mickey@disney.com",["work"])
	mickey.setEmail("mickey2@disney.com",["home"])
	mickey.setEmail("mickey3@disney.com",["other"])
	mickey.setUrl("http://www.disney.com",["home"])
	mickey.setBirthday("25/01/40")
	mickey.setNote("We\'re deliberately going to put some strange characters like =!(\"*&*(& into this note.... We\'re also going to make it really long just to see what happens when it goes over three lines.")
	# Handling image: need to read the image file into a buffer
	mickey.setPhotoFromFile("DATA/image.jpg")
	mickey.setAddress(pobox="P.O.Box 100",extaddr="Suite 101",street="35 Gibson Street",city="London",region="Greater London",zipcode="Z24 3BH",country="uk",type=["home"])
	str=mickey.serialize()
	if len(str) <1200:
		log.debug("mickey serialized:\n%s" % str)
	else:
		log.debug("mickey serialized:\n%s" % str[:150]+'...'+str[-150:])
	str=mickey.exportAsVcard()
	log.debug("---- Mickey vCard2.1 ---:\n%s" % str)
	mickey1=symplaContact(vcard=str)
	mickey1.dump()
	str1=mickey1.exportAsVcard()
	log.debug("---- Mickey vCard2.1 AGAIN ---:\n%s" % str1)
	if str==str1:
		log.debug("---- mickey PASSED vcard import-export identity check ----")
	else:
		log.error("Differences found in mickey import-export identity check")
		log.debug("Initial card:\n\"%s\"" %str)
		log.debug("Final card:\n\"%s\"" %str1)
		raise "FAILED test 5"
	
	fH=open('DATA/adam.vcf','rb')
	str=fH.read()
	cont=symplaContact()
	cont.importFromVcard(str)
	log.debug("---- Adam vCard2.1 ---:\n%s" % str)	
	cont.dump()
	str1=cont.exportAsVcard()
	cont1=symplaContact(vcard=str1)
	str2=cont1.exportAsVcard()
	log.debug("---- Adam vCard2.1 PROCESSED ---:\n%s" % str1)
	if str2==str1:
		log.debug("---- mickey PASSED vcard import-export identity check ----")
	else:
		log.error("Differences found in test import-export identity check")
		log.debug("Initial card:\n\"%s\"" %str)
		log.debug("Final card:\n\"%s\"" %str1)	
		raise "FAILED test 6"
	fH.close()
	
	mickey=symplaContact()
	mickey.setId("74")
	mickey.setType("contact")
	mickey.setForename("Mickey")
	mickey.setSurname("Mouse")
	mickey.setOtherNames("Mr.","\"Big Boy\"","Esq.")	# prefix,middlenames,suffix
	mickey.setCompany("Disney")
	mickey.setJobtitle("Clown")
	mickey.setPhoneNumber("020893939393",["home"])
	mickey.setPhoneNumber("020874747474",["work","mobile"])
	mickey.setEmail("mickey@disney.com",["work"])
	mickey.setEmail("mickey3@disney.com",["other"])
	mickey.setUrl("http://www.disney.com",["home"])
	mickey.setAddress(pobox="P.O.Box 100",extaddr="Suite 101",street="Penn. Ave.",city="Tampa",region="FL",zipcode="Z1P EE",country="U.S.",type=["home"])
	mickey.setAddressField(pobox="P.O.Box 103",type=["home"])
	mickey.setAddressField(city="Miami",type=["home"])
	mickey.setAddressField(street="13 New Street",type=["work"])
	mickey.setAddressField(city="Chicago",type=["work"])
	mickey.setAddressField(city="New York",type=["other"])
	mickey.setBirthday("25/01/40")
	mickey.setNote("CATEGORY: something")
	mickey.dump()
	str=mickey.exportAsVcard()
	log.debug("---- Mickey vCard2.1 ---:\n%s" % str)	
	mickey1=symplaContact(vcard=str)
	mickey1.dump()
	str1=mickey1.exportAsVcard()
	log.debug("---- Mickey vCard2.1 ---:\n%s" % str1)
	if str==str1:
		log.debug("---- mickey PASSED vcard import-export identity check ----")
	else:
		log.error("Differences found in test import-export identity check")
		log.debug("Initial card:\n\"%s\"" %str)
		log.debug("Final card:\n\"%s\"" %str1)	
		raise "FAILED test 7"
	
	#str="ds7:membersles12:system groups1:0s4:names0:s4:uuids35:0d39fe9c00000000-00e0d757f44c83ee-2s2:Ids1:2s4:types5:groupe"
	str="ds7:membersls2:58s2:33es12:system groups1:0s4:names6:Onlines4:uuids37:008ff70005b5662a-00e0ea8b5d621650-112s2:Ids3:112s4:types5:groupe"
	#str="ds12:system groups1:0s4:names0:s4:uuids35:0d39fe9c00000000-00e0d757f44c83ee-2s2:Ids1:2s4:types5:groupe"	# This works fine
	group=symplaContact()
	proclen=group.deserialize(str)
	if proclen==len(str):
		log.debug("Successfully processed all %d chars in serialized input for Group" % proclen)
	else:
		log.error("Only processed %d chars from a length of %d" % (proclen,len(str)))
		raise "FAILED test 8"
	group.dump()
		
	log.debug("----------------------------------------")
	log.debug("---- PASSED ALL SYMPLA CONTACT TESTS ----")
	log.debug("----------------------------------------")
