# import the required libraries
from ast import Raise
from email import message
from email.mime.text import MIMEText
import mimetypes
from turtle import shape
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import base64
import email
from bs4 import BeautifulSoup
import os
import time
import datetime
from tkinter import *
from tkinter import messagebox
from psutil import users

SECRET_KEY = '019250304'
SOFTWARE_NAME = 'PC Remote Control Using Email'

# if you modify this SCOPES, you need to delete file token.pickle first
# unless the code will not run
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

creds = None

if os.path.exists('token.pickle'):
	with open('token.pickle', 'rb') as token:
		creds = pickle.load(token)

# If credentials are not available or are invalid, ask the user to log in.
if not creds or not creds.valid:
	if creds and creds.expired and creds.refresh_token:
		creds.refresh(Request())
	else:
		flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
		creds = flow.run_local_server(port=0)
	# Save the access token in token.pickle file for the next run
	with open('token.pickle', 'wb') as token:
		pickle.dump(creds, token)

# Connect to the Gmail API
gmail = build('gmail', 'v1', credentials=creds)

# this function reads the latest unread email, and marks it as read
def read_email():
	'''
	This function reads 1 latest unread email from the Gmail user saved in access token.
	----------------------------------
	PARAMS:
	No parameter.
	----------------------------------
	RETURNS:
	___Email, "No Error": dtype = dict, str; if no error occured, return a email as a
	dictionary with 3 keys {'subject', 'sender', 'context'}
	
	___None, ErrorMessage: dtype = None, str; if error occurred, error's info in ErrorMessage
	'''
	# Get 1 latest unread email
	result = gmail.users().messages().list(
		maxResults = 1,
		userId = 'me',
		labelIds = ['INBOX', 'UNREAD']
	).execute()
	
	# messages is a list of dictionaries where each dictionary contains a message id.
	messages = result.get('messages')

	email = {}
	msg = messages[0]

	# Get the message from its id, txt is a dictionary
	txt = gmail.users().messages().get(userId='me', id=msg['id']).execute()

	# Use try-except to avoid any Errors
	try:
		# Get value of 'payload'
		payload = txt['payload']
		headers = payload['headers']

		# Look for Subject and Sender Email in the headers
		for d in headers:
			if d['name'] == 'Subject':
				subject = d['value']
			if d['name'] == 'From':
				sender = d['value']

		# Get body data, depends on mimeType of the Email
		mimeType = payload['mimeType']
		if mimeType == 'text/plain' or mimeType == 'text/html':
			data = payload['body']['data']
		else:
			parts = payload.get('parts')[0]
			data = parts['body']['data']
		
		# The Body of the message is in Encrypted format. So, we have to decode it.
		# Get the data and decode it with base 64 decoder.
		data = data.replace("-","+").replace("_","/")
		decoded_data = base64.b64decode(data)

		# Now, the data obtained is in lxml. So, we will parse
		# it with BeautifulSoup library
		soup = BeautifulSoup(decoded_data, 'lxml')
		body = str(soup.find('p').contents[0])
		
		# Check secret key
		if body.find(SECRET_KEY) == -1:
			raise Exception('Secret Key not found')
		
		email = {'subject':subject, 'sender':sender, 'context':body}
		
		# Mark the email as READ
		gmail.users().messages().modify(
			userId = 'me',
			id = msg['id'],
			body = {'removeLabelIds': ['UNREAD']}
		).execute()

		return email, "No Error"

	except Exception as error:
		err_message = 'Oops!\nAn error occurred while getting email!\n' + str(error)
		return None, err_message

# function parse a string of time [hh:mm:ss] to a datetime object
def time_parser(time_string):
	'''
	This function parse a string of time into a datetime object.
	----------------------------------
	PARAMS:
	___time_string: dtype = str, represents a time as format hh:mm:ss
	----------------------------------
	RETURNS:
	___Datetime, "No Error": dtype = datetime, str; if no error occured, return a datetime object
	with h,m,s as passed and day,month,year,... as today.
	
	___None, ErrorMessage: dtype = None, str; if error occurred, error's info in ErrorMessage
	'''
	try:
		# time_string format: hh:mm:ss (24 hour)
		parsed_time = datetime.datetime.strptime(time_string, "%H:%M:%S")

		# other info (day, month, year,...) is today
		parsed_time = datetime.datetime.combine(datetime.datetime.today(), parsed_time.time())
		return parsed_time, "No Error"
	
	except Exception as err:
		return None, str(err)

# function restart pc at a specific time
def restart(time_str):
	'''
	This function restart the pc.
	------------------------------
	PARAMS:
	___time_str: dtype = str, the time to do the restart.
	------------------------------
	RETURNS:
	___True, "No Error": dtype = bool, str; if restart command successfully scheduled.
	___None, ErrorMessage: dtype = None, str; if restart was canceled by current pc user
	or any other reasons (error's info in ErrorMessage).
	'''
	try:
		current_time = datetime.datetime.now()
		restart_time, err_message = time_parser(time_str)

		if (restart_time == None):
			raise Exception('Parse time error')

		if restart_time < current_time:
			raise Exception('Restart time [' + time_str + '] < current time')

		countdown = (restart_time - current_time).seconds

		os.system('shutdown -a')
		os.system('shutdown /r /t ' + str(countdown))

		# Ask current PC user whether he/she accepts to restart PC or not
		if messagebox.askyesno (
			title = SOFTWARE_NAME,
			message = "This PC is going to restart at " + time_str + ' due to a request email\nDo you agree to restart?'
		) == False:

			# If current pc user doesn't accept to restart, cancel the shutdown schedule
			os.system('shutdown -a')
			messagebox.showinfo(SOFTWARE_NAME, 'RESTART SCHEDULE CANCELED')
			raise Exception('PC\'s current user refused to restart at ' + time_str)
		else:
			return True, "No error"

	except Exception as error:
		err_message = 'Oops!\nERROR while restarting this pc!\n' + str(error)
		return None, err_message

def shutdown(time_str=str):
	'''
	Schedule a shutdown for this computer at a specific time.
	--------------
	PARAMS:
	___time_str (dtype = str): time to shutdown as format hh:mm:ss.
	--------------
	RETURNS:
	___True, "No Error" (dtype = bool, str): if no error occurred.
	___None, ErrorMessage (dtype = None, str): if error occurred.
	'''
	try:
		shutdown_time, err_msg = time_parser(time_str)

		if shutdown_time == None:
			raise Exception(err_msg)
		
		current_time = datetime.datetime.now()

		if shutdown_time < current_time:
			raise Exception('Shutdown time [' + time_str + '] < Current time')
		
		countdown = (shutdown_time - current_time).seconds

		os.system('shutdown -a')
		os.system('shutdown /s /t ' + str(countdown))

		# Ask current PC user to shutdown
		if messagebox.askyesno(
			title = SOFTWARE_NAME,
			message = 'This PC is going to shutdown at ' + time_str + ' due to a request email.\nDo you agree to shutdown?\n'
		) == False:
			# User refused to shutdown, cancel the scheduled shutdown.
			os.system('shutdown -a')
			messagebox.showinfo(
				title = SOFTWARE_NAME,
				message = 'Canceled shutdown schedule.'
			)
			raise Exception('Current PC\'s user refused to shutdown at ' + time_str)
		else:
			# User accepted the shutdown schedule.
			return True, "No Error"

	except Exception as err:
		return None, str(err)

def create_message(sender, to, subject, message_text):
	'''
	This function create a message for an email.
	----------------------------------
	PARAMS:
	___sender: dtype = str, representing the email address of the sender.
	___to: dtype = str, representing the email address of the receiver.
	___subject: dtype = str, representing the subject of the email.
	___message_text: dtype = str, representing the context of email.
	----------------------------------
	RETURNS:
	___A dictionary with keys {'raw'} contains the decoded raw data of email body.
	'''
	message = MIMEText(message_text)
	message['to'] = to
	message['from'] = sender
	message['subject'] = subject
	raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
	return {
		'raw': raw_message.decode("utf-8")
	} 

def send_message(service, user_id, message):
	'''
	Send an email.
	---------------------------------
	PARAMS:
	___service: the Gmail service object.
	___user_id: dtype = str, The user's email address. The special value 'me' can be used to indicate the authenticated user.
	___message: dtype = dict, the raw data of email body.
	---------------------------------
	RETURNS:
	___None, errorMessage: dtype = None, str; when error occurred.
	___message: dtype = dict, contains info about the successfully sent email.
	'''
	try:
		message = service.users().messages().send(userId=user_id, body=message).execute()
		return message
	except Exception as e:
		return None, str(e)

def do_restart_request(email):
	'''
	Execute the RESTART request from email and send a response email to the request email.
	--------------
	PARAMS:
	___email (dtype = dict): the request email, contain 3 keys {'subject':str, 'sender':str, 'context':str}.
	--------------
	RETURNS:
	___None, errorMessage (dtype = None, str): if any fucking error occurred.
	'''
	try:
		tokens = [str.strip() for str in email['context'].splitlines()]
		TIME_POS = 1
		time = tokens[TIME_POS]
		action, err_message = restart(time)

		# send a response email to sender
		if action == None:
			msg_content = 'Restart FAILED\nInfo: ' + err_message
		else:
			msg_content = 'The computer is scheduled to restart at ' + time
		
		sender_mail = email['sender'].replace('<','').replace('>','').split(' ')[-1]

		response_context = create_message (
			sender = gmail.users().getProfile(userId='me').execute()['emailAddress'],
			to = sender_mail,
			subject = 'RESTART',
			message_text = msg_content
		)

		send_message(gmail, 'me', response_context)
	
	except Exception as error:
		return None, str(error)

def do_shutdown_request(email):
	'''
	Execute the SHUTDOWN request email and send a response email to the sender of request email.
	---------
	PARAMS:
	___email (dtype = dict): the request email, contains 3 keys {'subject', 'sender', 'context'}
	---------
	RETURNS:
	___None, ErrorMessage (dtype = None, str): if error occurred.
	___
	'''
	try:
		tokens = [str.strip() for str in email['context'].splitlines()]
		time = tokens[1]
		action, err_msg = shutdown(time)

		if action == None:
			msg_text = 'Shutdown FAILED\nInfo: ' + err_msg
		else:
			msg_text = 'The computer is scheduled to shutdown at ' + time
		
		response = create_message (
			sender = gmail.users().getProfile(userId='me').execute()['emailAddress'],
			to = email['sender'].replace('<','').replace('>','').split(' ')[-1],
			subject = 'SHUTDOWN',
			message_text = msg_text
		)

		send_message(gmail, 'me', response)

	except Exception as err:
		return None, str(err)


# Loop waiting for a valid REQUEST email and DO it
# run .py script as background process with pythonw
while True:
	email, err_message = read_email()
	if (email != None):
		subject = email['subject']
		if subject == 'RESTART':
			do_restart_request(email)
		elif subject == 'SHUTDOWN':
			do_shutdown_request(email)
