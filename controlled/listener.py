# import the required libraries
import mimetypes
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import shutil
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import base64
import email
from bs4 import BeautifulSoup	# to decode email body
import os
import datetime
import pandas as pd
from tkinter import *
from tkinter import messagebox
import pyautogui	# to take screenshot
import psutil	# to get running processes

SECRET_KEY = '019250304'
SOFTWARE_NAME = 'PC Remote Control Using Email'
TEMPORARY_FILES_PATH = '.\Temporary'

# Create a folder for temporary files
if not os.path.isdir(TEMPORARY_FILES_PATH):
	os.makedirs(TEMPORARY_FILES_PATH)

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
print('SUCCESS: Connected to Gmail service')

auth_email_address = gmail.users().getProfile(userId = 'me').execute()['emailAddress']

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
			return None, 'Secret key not found!'
		
		email = {'subject':subject, 'sender':sender, 'context':body}
		
		# Mark the email as READ
		gmail.users().messages().modify(
			userId = 'me',
			id = msg['id'],
			body = {'removeLabelIds': ['UNREAD']}
		).execute()

		print('SUCCESS: Got a new request email [{}].'.format(subject))
		return email, "No Error"

	except Exception as error:
		err_message = 'An error occurred while getting email!\n' + str(error)
		print('FAILED: ' + err_message)
		return None, err_message

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
		
		print('SUCCESS: File part has been built, content type = {}'.format(content_type))
		return msg

	except Exception as err:
		print('FAILED: Build file part unsuccessful: ' + str(err))
		messagebox.showwarning(SOFTWARE_NAME, 'Build File Part Failed: ' + str(err))

def create_email(sender = str, receiver = str, subject = str, text = str, attachment_path = None | str):
	'''
	Create an email.
	-------
	PARAMS:
	___sender (dtype = str): email address of the sender.
	___receiver (dtype = str): email address of the receiver.
	___subject (dtype = str): subject of the email.
	___text (dtype = str): text part of the email.
	___attachment_path (dtype = str or None): Optional, is the path to attachment file.
	-------
	RETURNS:
	The raw body data of the email.
	'''
	try:
		mime_message = MIMEMultipart()

		mime_message['To'] = receiver
		mime_message['From'] = sender
		mime_message['Subject'] = subject

		text_part = MIMEText(text)
		mime_message.attach(text_part)

		if attachment_path != None:
			attachment = build_file_part(file = attachment_path)
			mime_message.attach(attachment)
		
		encoded_message = base64.urlsafe_b64encode(mime_message.as_string().encode('utf-8'))
		print('SUCCESS: An email has been created.')
		return {
			'raw': encoded_message.decode('utf-8')
		}
	except Exception as err:
		print('FAILED: Create email unsuccessfull: ' + str(err))
		messagebox.showwarning(SOFTWARE_NAME, 'Create email failed: ' + str(err))


def send_email(service, user_id, body):
	'''
	Send an email.
	---------------------------------
	PARAMS:
	___service: the Gmail service object.
	___user_id: dtype = str, The user's email address. The special value 'me' can be used to indicate the authenticated user.
	___body: dtype = dict, the raw data of email body.
	---------------------------------
	RETURNS:
	___message: dtype = dict, contains info about the successfully sent email.
	___None: send email failed.
	'''
	try:
		message = service.users().messages().send(userId=user_id, body=body).execute()
		print('SUCCESS: Sent an email.')
		return message
	except Exception as e:
		print('FAILED: Send email unsuccessfull: ' + str(e))
		messagebox.showerror(SOFTWARE_NAME, 'Send Email Failed: ' + str(e))
		return None

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
			print('SUCCESS: Scheduled to restart this PC at {}.'.format(time_str))
			return True, "No error"

	except Exception as error:
		err_message = str(error)
		print('FAILED: Schedule restart failed: ' + err_message)
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
			print('SUCCESS: Scheduled to shutdown this PC at {}.'.format(time_str))
			return True, "No Error"

	except Exception as err:
		print('FAILED: schedule shutdown failed: ' + str(err))
		return None, str(err)

def get_sender_address(email):
	'''
	Get email address of sender.
	---------
	PARAMS:
	___email (dtype = dict): contains 3 keys {'sender', 'subject', 'context'}
	---------
	RETURNS:
	___None: error occurred.
	___Email address of email's sender (dtype = str): no error occurred.
	'''
	try:
		email_address = email['sender'].replace('<','').replace('>','').split(' ')[-1]
		return email_address
	except Exception:
		print('FAILED: Can\'t get sender\'s email address')
		return None

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

		response = create_email (
			sender = auth_email_address,
			receiver = get_sender_address(email),
			subject = 'RESTART',
			text = msg_content,
			attachment_path = None
		)

		send_email(gmail, 'me', response)
		print('SUCCESS: RESTART request email has been successfully executed.')
	
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
		
		response = create_email (
			sender = auth_email_address,
			receiver = get_sender_address(email),
			subject = 'SHUTDOWN',
			text = msg_text,
			attachment_path = None
		)

		send_email(gmail, 'me', response)
		print('SUCCESS: SHUTDOWN request email has been successfully executed.')

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
		
		print('SUCCESS: Copied file {} to {}'.format(src_path, result_path))
		return True, result_path

	except Exception as err:
		print("FAILED: can't copy file: " + str(err))
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
		
		response = create_email (
			sender = auth_email_address,
			receiver = get_sender_address(email),
			subject = 'COPY FILE',
			text = msg_text,
			attachment_path = None
		)

		send_email(gmail, 'me', response)
		print('SUCCESS: COPY request email has been successfully executed.')

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
		file_name = str(datetime.datetime.now().strftime('[%d-%m-%Y-%H-%M-%S][screenshot].png'))
		save_path = os.path.join(save_dir, file_name)

		sc.save(save_path)

		print('SUCCESS: Screenshot taken.')
		return True, save_path

	except Exception as err:
		print("FAILED: Can't take screenshot: " + str(err))
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
		sc, msg = take_screenshot(save_dir = TEMPORARY_FILES_PATH)
		
		# Send response email		
		if sc == None:
			text = 'Take screenshot failed\nInfo: ' + msg
			screenshot_path = None
		else:
			text = ''
			screenshot_path = msg

		response = create_email (
			sender = auth_email_address,
			receiver = get_sender_address(email),
			subject = 'CAPTURE',
			text = text,
			attachment_path = screenshot_path
		)

		if sc != None:
			os.remove(screenshot_path)

		send_email(gmail, 'me', response)
		print('SUCCESS: CAPTURE request email has been executed.')

	except Exception as err:
		messagebox.showwarning(SOFTWARE_NAME, 'SCREEN CAPTURE FAILED\n' + str(err))

def list_processes():
	'''
	Get list of running processes.
	--------------
	PARAMS:
	No params
	--------------
	RETURNS:
	___data, 'No error' (dtype = dict, str): data contains 3 keys = name, id and num_of_thread.
	___None, err_message (dtype = None, str): if any error occurred.
	'''
	try:
		names = list()
		IDs = list()
		num_of_threads = list()

		for proc in psutil.process_iter():
			try:
				# Get process name, pid, number of threads from process object.
				name = proc.name()
				pid = proc.pid
				threads = proc.num_threads()
				names.append(str(name))
				IDs.append(str(pid))
				num_of_threads.append(str(threads))
			except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
				pass

		data = {
			'name' : names,
			'id' : IDs,
			'num_of_thread' : num_of_threads
		}
		print('SUCCESS: Got list of running processes.')
		return data, 'No error'

	except Exception as err:
		print("FAILED: Can't get running processes list: " + str(err))
		return None, str(err)

def do_running_process_request(email):
	'''
	Execute the RUNNING PROCESSES request email.
	----------------
	PARAMS:
	___email (dtype = dict): the request email. Must contains key 'sender'
	----------------
	RETURNS:
	None.
	'''
	try:
		running_processes, msg = list_processes()

		if running_processes == None:
			# If get running processes failed, send a response email
			# with error message.
			text = 'LIST RUNNING PROCESSES FAILED\nInfo: ' + msg
			save_path = None
		else:
			# If get running processes successful, send a response email
			# with a csv attachment file contains running processes' info
			text = ''
			data = pd.DataFrame(running_processes)
			save_file = datetime.datetime.now().strftime('[%d-%m-%Y-%H-%M-%S][running-processes].csv')
			save_path = os.path.join(TEMPORARY_FILES_PATH, save_file)
			data.to_csv(save_path, header = True, index = False)
		
		response = create_email (
			sender = auth_email_address,
			receiver = get_sender_address(email),
			subject = 'RUNNING PROCESSES',
			text = text,
			attachment_path = save_path
		)

		if running_processes != None:
			os.remove(save_path)

		send_email(gmail, 'me', response)
		print('SUCCESS: RUNNING PROCESSES request email has been executed.')

	except Exception as err:
		messagebox.showerror (
			SOFTWARE_NAME,
			'FAILED WHILE EXECUTING RUNNING PROCESSES REQUEST EMAIL\nInfo: ' + str(err)
		)

def kill_processes(pid = str):
	'''
	Kill a process by its pid.
	--------------
	PARAMS:
	___pid (dtype = str): process id.
	--------------
	RETURNS:
	___True, process_name (dtype = bool, str): if killed successfully.
	___None, error_message (dtype = None, str): if error occurred.
	'''
	try:
		# os.kill(int(pid), signal.SIGKILL)
		process_name = psutil.Process(pid = int(pid)).name()
		res = os.system('taskkill.exe /F /PID ' + str(pid))
		
		if res != 0:
			raise Exception('Kill process {} failed.'.format(pid))

		return True, process_name
	except Exception as err:
		print("FAILED: Can't kill process PID {}: ".format(pid) + str(err))
		return None, str(err)

def do_kill_process_request(email):
	'''
	Execute the KILL PROCESS request email.
	----------
	PARAMS:
	___email (dtype = dict): the request email, must contain key 'sender'
	----------
	RETURNS:
	None
	'''
	try:
		tokens = [str.strip() for str in email['context'].splitlines()]
		pid = tokens[1]
		kill, msg = kill_processes(pid)

		if kill == None:
			# Kill process Failed
			text = 'Kill process [pid = {}] failed.\nInfo: {}'.format(pid, msg)
			attachment = None
		else:
			# Kill process Completed
			text = ''
			running_processes, res_msg = list_processes()

			if running_processes == None:
				raise Exception(res_msg)

			data = pd.DataFrame(running_processes)
			save_file = datetime.datetime.now().strftime('[%d-%m-%Y-%H-%M-%S][running-processes].csv')
			save_path = os.path.join(TEMPORARY_FILES_PATH, save_file)
			data.to_csv(save_path, header = True, index = False)

			attachment = save_path
		
		response = create_email (
			sender = auth_email_address,
			receiver = get_sender_address(email),
			subject = 'KILL PROCESS',
			text = text,
			attachment_path = attachment
		)

		if kill != None:
			os.remove(attachment)

		send_email(gmail, 'me', response)
		print('SUCCESS: KILL PROCESS request email has been executed.')
	
	except Exception as err:
		messagebox.showerror (
			SOFTWARE_NAME,
			'Execute KILL PROCESS request email FAILED.\nInfo: ' + str(err)
		)

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
		elif subject == 'RUNNING PROCESSES':
			do_running_process_request(email)
		elif subject == 'KILL PROCESS':
			do_kill_process_request(email)
