import sys
import imaplib
import email
import datetime
import os

from dotenv import load_dotenv
load_dotenv()

M = imaplib.IMAP4_SSL('imap.gmail.com')

def get_email_time(d):
	date_tuple = email.utils.parsedate_tz(d)
	unix_ts = email.utils.mktime_tz(date_tuple)
	local_date = datetime.datetime.utcfromtimestamp(unix_ts)
	return local_date

def process_mailbox(M):
	packets = []
	rv, data = M.search(None, "ALL")
	if rv != 'OK':
		print("No messages found!")
		return packets

	for num in data[0].split():
		rv, data = M.fetch(num, '(RFC822)')
		if rv != 'OK':
			print("ERROR getting message", num)
			return packets
		msg = email.message_from_string(data[0][1].decode('utf-8'))
		email_time = get_email_time(msg['Date'])

		try:
			packet = parsetelem(msg.get_payload()[1].get_payload(decode=True))
			packet['emailtime'] = email_time
			packets.append(packet)
		except IndexError:
			pass
	return packets

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
		time = datetime.datetime.strptime(string, '%H%M%S').time()
	except:
		time = None
	return time

def makestatus(string):
	flightstate = string[0]
	asicstate = string[1]
	siphrastate = string[2]
	return flightstate, asicstate, siphrastate

def get_latest_packets():
	packets = []
	try:
		M.login(os.environ['gmod_email'], os.environ['gmod_pwd'])
	except imaplib.IMAP4.error:
		print("LOGIN FAILED!!! ")
		return packets
	rv, data = M.select("INBOX")
	if rv == 'OK':
		packets = process_mailbox(M)
		M.close()
	M.logout()
	return packets

if __name__ == '__main__':
	print(get_latest_packets())
