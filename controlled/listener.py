# import the required libraries
from ast import Raise
from email import message
import mimetypes
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import shutil
from turtle import shape
from urllib import response
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import base64
import email
from bs4 import BeautifulSoup	# to decode email body
import os
import time
import datetime
from tkinter import *
from tkinter import messagebox
from numpy import take
from psutil import users
import pyautogui	# to take screenshot

SECRET_KEY = '019250304'
SOFTWARE_NAME = 'PC Remote Control Using Email'
SCREENSHOT_PATH = './Screenshot'

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
	This function reads 1 latest unread email from the authenticated Gmail user.
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

def build_file_part(file):
	'''
	Build the file part for creating email with attachment.
	-----------------------
	PARAMS:
	___file (dtype = str): path to file to attach to email.
	-----------------------
	RETURNS:
	___An object to attach to MIME Message.
	'''
	try:
		# Check if file exist:
		if not os.path.isfile(file):
			raise Exception('File ' + file + ' not exist.')

		content_type, encoding = mimetypes.guess_type(file)

		if content_type is None or encoding is not None:
			content_type = 'application/octet-stream'

		main_type, sub_type = content_type.split('/', 1)

		if main_type == 'text':
			with open(file, 'rb') as opened_file:
				msg = MIMEText(opened_file.read(), _subtype=sub_type)
		elif main_type == 'image':
			with open(file, 'rb') as opened_file:
				msg = MIMEImage(opened_file.read(), _subtype=sub_type)
		elif main_type == 'audio':
			with open(file, 'rb') as opened_file:
				msg = MIMEAudio(opened_file.read(), _subtype=sub_type)
		else:
			with open(file, 'rb') as opened_file:
				msg = MIMEBase(main_type, sub_type)
				msg.set_payload(opened_file.read())

		filename = os.path.basename(file)
		msg.add_header('Content-Disposition', 'attachment', filename=filename)
		return msg

	except Exception as err:
		messagebox.showwarning(SOFTWARE_NAME, 'Built Email Body Failed: ' + str(err))

def create_email_with_attachment(sender = str, to = str, subject = str, text = str, attachment_path = str):
	'''
	Create Email with attachment.
	-------------
	PARAMS:
	___sender (dtype = str): email address of sender.
	___to (dtype = str): email address of receiver.
	___subject (dtype = str): subject of email.
	___text (dtype = str): text content of email.
	___attachment_path (dtype = str): path to attachment file.
	-------------
	RETURNS:
	No returns.
	'''
	try:
		mime_message = MIMEMultipart()
		mime_message['To'] = to
		mime_message['From'] = sender
		mime_message['Subject'] = subject
		text_part = MIMEText(text)
		mime_message.attach(text_part)
		attachment = build_file_part(file = attachment_path)
		mime_message.attach(attachment)
		encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
		return {
			'raw': encoded_message
		}
	except Exception as err:
		messagebox.showwarning(SOFTWARE_NAME, 'Create email with attachment failed: ' + str(err))

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
	___message: dtype = dict, contains info about the successfully sent email.
	___None: send email failed.
	'''
	try:
		message = service.users().messages().send(userId=user_id, body=message).execute()
		return message
	except Exception as e:
		messagebox.showerror(SOFTWARE_NAME, 'Send Email Failed: ' + str(e))
		return None


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
			message = "This PC is scheduled to restart at " + time_str + ' due to a request email\nDo you want to cancel it?'
		) == True:

			# If current pc user doesn't accept to restart, cancel the shutdown schedule
			os.system('shutdown -a')
			messagebox.showinfo(SOFTWARE_NAME, 'RESTART SCHEDULE CANCELED')
			raise Exception('PC\'s current user refused to restart at ' + time_str)
		else:
			return True, "No error"

	except Exception as error:
		err_message = str(error)
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
			message = 'This PC is scheduled to shutdown at ' + time_str + ' due to a request email.\nDo you want to cancel it?\n'
		) == True:
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

def do_restart_request(email):
	'''
	Execute the RESTART request from email and send a response email to the request email.
	--------------
	PARAMS:
	___email (dtype = dict): the request email, contain 3 keys {'subject':str, 'sender':str, 'context':str}.
	--------------
	RETURNS:
	No Returns.
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
		err_msg = 'RESTART SCHEDULE FAILED\n' + str(error)
		messagebox.showwarning(SOFTWARE_NAME, err_msg)

def do_shutdown_request(email):
	'''
	Execute the SHUTDOWN request email and send a response email to the sender of request email.
	---------
	PARAMS:
	___email (dtype = dict): the request email, contains 3 keys {'subject', 'sender', 'context'}
	---------
	RETURNS:
	No returns.
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
		err_msg = 'SHUTDOWN SCHEDULE FAILED\n' + str(err)
		messagebox.showwarning(SOFTWARE_NAME, err_msg)

def copy_file(src_path, dest_path):
	'''
	Copy a file. Auto make directory if not exist.
	-------------------
	PARAMS:
	___src_path (dtype = str): path to source file
	___dest_path (dtype = str): path to destination (maybe directory or file name)
	-------------------
	RETURNS:
	___None, ErrMessage (dtype = None, str): if error occurred.
	___True, copied_file_path (dtype = bool, str): if copy successfully
	'''
	try:
		# Check if source file exists
		if not os.path.isfile(src_path):
			raise Exception('Source file ' + src_path + ' not exist')
		
		# Copy file
		try:
			result_path = shutil.copy(src_path, dest_path)
		except IOError:
			os.makedirs(os.path.dirname(dest_path))
			result_path = shutil.copy(src_path, dest_path)
		
		return True, result_path

	except Exception as err:
		return None, str(err)

def do_copy_request(email):
	'''
	Execute COPY request email.
	--------------
	PARAMS:
	___email (dtype = dict): the request email, contains 3 keys {'subject', 'sender', 'context'}.
	--------------
	RETURNS:
	No returns.
	'''
	try:
		tokens = [str.strip() for str in email['context'].splitlines()]
		src_path = tokens[1]
		dest_path = tokens[2]

		copy_result, msg = copy_file(src_path, dest_path)

		# Send response email
		if copy_result == None:
			msg_text = 'Copy FAILED\nInfo: ' + msg
		else:
			msg_text = msg
		
		response = create_message (
			sender = gmail.users().getProfile(userId = 'me').execute()['emailAddress'],
			to = email['sender'].replace('<','').replace('>','').split(' ')[-1],
			subject = 'COPY FILE',
			message_text = msg_text
		)

		send_message(gmail, 'me', response)

	except Exception as err:
		err_msg = 'COPY FILE FAILED\n' + str(err)
		messagebox.showwarning(SOFTWARE_NAME, err_msg)

def take_screenshot(save_dir = str):
	'''
	Take screenshot and save to file.
	-------------
	PARAMS:
	___save_dir (dtype = str): directory to save image file, image file name
	will be generated by screenshot time. Format: 'save_dir/%d-%m-%Y-%H-%M-%S.png'
	-------------
	RETURNS:
	___None, error_message (dtype = None, str): if error occurred.
	___True, path_to_saved_image (dtype = bool, str): if no error occurred.
	'''
	try:
		sc = pyautogui.screenshot()
		
		# Make directory if it not already exist
		if not os.path.isdir(save_dir):
			os.makedirs(save_dir)

		# File name is screenshot time.png
		file_name = str(datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S.png'))
		save_path = os.path.join(save_dir, file_name)

		sc.save(save_path)

		return True, save_path

	except Exception as err:
		return None, str(err)

def do_capture_request(email):
	'''
	Execute CAPTURE request email.
	--------------
	PARAMS:
	___email (dtype = dict): the request email, contains 3 keys {'subject', 'sender', 'context'}.
	--------------
	RETURNS:
	No returns.
	'''
	try:
		sc, msg = take_screenshot(save_dir = SCREENSHOT_PATH)
		
		# Send response email
		sender = gmail.users().getProfile(userId = 'me').execute()['emailAddress']
		receiver = email['sender'].replace('<','').replace('>','').split(' ')[-1]
		subject = 'CAPTURE'

		if sc == None:
			response = create_message (
				sender = sender,
				to = receiver,
				subject = subject,
				message_text = 'Take screenshot failed\nInfo: ' + msg
			)
		else:
			response = create_email_with_attachment (
				sender = sender,
				to = receiver,
				subject = subject,
				text = '',
				attachment_path = msg 
			)
		
		send_message (
			service = gmail,
			user_id = 'me',
			message = response
		)

	except Exception as err:
		messagebox.showwarning(SOFTWARE_NAME, 'SCREEN CAPTURE FAILED\n' + str(err))

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
		elif subject == 'COPY FILE':
			do_copy_request(email)
		elif subject == 'CAPTURE':
			do_capture_request(email)
