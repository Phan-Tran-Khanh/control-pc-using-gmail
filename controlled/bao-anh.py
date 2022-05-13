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

SECRET_KEY = '*019250304*'

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
	# We can also pass maxResults to get any number of emails. Like this:
	result = gmail.users().messages().list(
		maxResults = 1,
		userId = 'me',
		labelIds = ['INBOX', 'UNREAD']
	).execute()
	
	messages = result.get('messages')
	# messages is a list of dictionaries where each dictionary contains a message id.

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
	try:
		# time_string format: hh:mm:ss (24 hour)
		parsed_time = datetime.datetime.strptime(time_string, "%H:%M:%S")
		parsed_time = datetime.datetime.combine(datetime.datetime.today(), parsed_time.time())
		return parsed_time, "No Error"
	except:
		err_message = 'error parsing time'
		return None, err_message

# function restart pc at a specific time
def restart(time_str):
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
			title = '[NOTIFICATION] Email Remote Control',
			message = "This PC is going to restart at " + time_str + ' due to a request email\nDo you agree to restart?'
		) == False:
			os.system('shutdown -a')
			messagebox.showinfo('Email Remote Control', 'RESTART SCHEDULE CANCELED')
			raise Exception('PC\'s current user refused to restart')
		else:
			return True, "No error"

	except Exception as error:
		err_message = 'Oops!\nERROR while restarting this pc!\n' + str(error)
		return None, err_message

def create_message(sender, to, subject, message_text):
	message = MIMEText(message_text)
	message['to'] = to
	message['from'] = sender
	message['subject'] = subject
	raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
	return {
		'raw': raw_message.decode("utf-8")
	} 

def send_message(service, user_id, message):
  try:
    message = service.users().messages().send(userId=user_id, body=message).execute()
    print('Message Id: %s' % message['id'])
    return message
  except Exception as e:
    print('An error occurred: %s' % e)
    return None

def do_restart_request(email):
	try:
		tokens = [str.strip() for str in email['context'].splitlines()]
		TIME_POS = 1
		time = tokens[TIME_POS]
		action, err_message = restart(time)
		if action == None:
			sender_mail = email['sender'].replace('<','').replace('>','').split(' ')[-1]
			# send a response email to sender
			response_context = create_message (
				sender = gmail.users().getProfile(userId='me').execute()['emailAddress'],
				to = sender_mail,
				subject = '[REPLY] RESTART FAILED',
				message_text = err_message
			)
			send_message(gmail, 'me', response_context)
			raise Exception('Restart Failed')
	except Exception as error:
		return None

# Loop waiting for a valid REQUEST email and DO it
# run .py script as background process with pythonw
while True:
	email, err_message = read_email()
	if (email != None):
		subject = email['subject']
		if subject == 'RESTART':
			do_restart_request(email)
