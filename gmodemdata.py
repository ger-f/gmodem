import sys
import imaplib
import email
import datetime
import os
from threading import Thread
import time

from dotenv import load_dotenv
load_dotenv()

class PacketGetter:
	def __init__(self, refresh=60):
		self.M = get_mailbox()
		self.packets = self.get_backlog()
		self.refresh = refresh
		self.run = False
		self.thread = None

	def start(self):
		self.run = True
		self.thread = Thread(target=self.update_thread, args=[])
		self.thread.start()

	def stop(self):
		self.run = False
		self.thread.join()

	def update_thread(self):
		while self.run:
			print('checking the emails!')
			print(len(self.packets))
			print('\n'*10)
			time.sleep(self.refresh)
			self.check_for_updates()


	def get_backlog(self):
		return self.process_mailbox(mode='ALL')

	def get_latest(self):
		return self.process_mailbox(mode='UNSEEN')

	def check_for_updates(self):
		p = [i for i in self.get_latest() if len(i)]
		if not len(p):
			return
		self.packets.extend(p)

	def process_mailbox(self, mode):
		rv, data = self.M.search(None, mode)
		if rv != 'OK':
			print("No messages found!")
			return
		p = [self._parse_mail(i) for i in data[0].split()]
		p = [i for i in p if len(i)]
		return p

	def _parse_mail(self, i):
		rv, data = self.M.fetch(i, '(RFC822)')
		if rv != 'OK':
			print("ERROR getting message", i)
			return []
		msg = email.message_from_string(data[0][1].decode('utf-8'))
		email_time = get_email_time(msg['Date'])
		try:
			packet = parsetelem(msg.get_payload()[1].get_payload(decode=True))
		except IndexError:
			return []
		packet['emailtime'] = email_time
		return packet

def get_mailbox():
	M = imaplib.IMAP4_SSL('imap.gmail.com')
	M.login(os.environ['gmod_email'], os.environ['gmod_pwd'])
	rv, _ = M.select("INBOX")
	if rv != 'OK':
		raise Exception('Unable to login!')
	return M

def get_email_time(d):
	date_tuple = email.utils.parsedate_tz(d)
	unix_ts = email.utils.mktime_tz(date_tuple)
	local_date = datetime.datetime.utcfromtimestamp(unix_ts)
	return local_date

def parsetelem(telem):
	telemlist = telem.decode('utf-8').split('|')
	data = {}
	data['time'] = maketime(telemlist[0])
	data['flightstate'], data['asicstate'], data['siphrastate'] = makestatus(telemlist[1])
	data['counts'] = makefloat(telemlist[2])
	data['volts'] = makefloat(telemlist[3])
	data['setvolts'] = makefloat(telemlist[4])
	data['settemp'] = makefloat(telemlist[5])
	data['coeff'] = makefloat(telemlist[6])
	data['lat'] = makefloat(telemlist[7])
	data['lon'] = makefloat(telemlist[8])
	data['alt'] = makefloat(telemlist[9])
	data['sipmtemp'] = makefloat(telemlist[10])
	data['inttemp'] = makefloat(telemlist[11])
	data['exttemp'] = makefloat(telemlist[12])
	data['pressure'] = makefloat(telemlist[13])
	return data

def makefloat(string):
	try:
		number = float(string)
	except:
		number = None
	return number

def maketime(string):
	try:
		thetime = datetime.datetime.strptime(string, '%H%M%S').time()
	except:
		thetime = None
	return thetime

def makestatus(string):
	flightstate = string[0]
	asicstate = string[1]
	siphrastate = string[2]
	return flightstate, asicstate, siphrastate
