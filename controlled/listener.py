# import the required libraries
from email import encoders
import shutil, pickle, os, os.path, base64, datetime, tkinter
import pyautogui, psutil, pystray, re, winreg, mimetypes
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup	# to decode email body
from pandas import DataFrame
from tkinter import messagebox
from tkinter import *
from threading import Timer, Thread
from pynput.keyboard import Listener
from PIL import Image
from cv2 import VideoCapture, imwrite, VideoWriter, VideoWriter_fourcc

SECRET_KEY = '019250304'
SOFTWARE_NAME = 'PC Remote Control Using Email'
TEMPORARY_FILES_PATH = 'temp'
TOKEN_FILE = 'token.pickle'
DATETIME_FORMAT = '%Y-%m-%d-%H-%M-%S'
LIMIT_VIDEO_LENGTH = 30

def gui_print(msg = str):
	txt.config(state = NORMAL)
	txt.insert(index = END, chars = msg + '\n')
	txt.pack()
	txt.see(index = END)
	txt.config(state = DISABLED)

valid_subjects = [
	'SHUTDOWN',
	'RESTART',
	'COPY FILE',
	'SCREEN CAPTURE',
	'WEBCAM CAPTURE',
	'WEBCAM RECORD',
	'LIST PROCESSES',
	'KILL PROCESS',
	'KEYPRESS',
	'REGISTRY KEY'
]

def read_email():
	'''
	Reads 1 latest unread request email from the authenticated Gmail user.
	----------------------------------
	PARAMS:
	No parameter.
	----------------------------------
	RETURNS:
	___Email, "No Error": dtype = dict, str; if no error occured, return a email as a
	dictionary with 3 keys {'subject', 'sender', 'context'}
	___None, ErrorMessage: dtype = None, str; if error occurred, error's info in ErrorMessage
	'''
	fucking_msg = dict()
	# Use try-except to avoid any Errors
	try:
		# Get 1 latest unread email
		result = gmail.users().messages().list(
			maxResults = 1,
			userId = 'me',
			labelIds = ['INBOX', 'UNREAD']
		).execute()

		size = int(result['resultSizeEstimate'])

		if size == 0:
			raise Exception("UNREAD mail box is empty")
		
		# messages is a list of dictionaries where each dictionary contains a message id.
		messages = result.get('messages')

		if messages == None:
			raise Exception("UNREAD mail box is empty")

		email = {}
		if messages != None:
			fucking_msg = messages[0]

		# Get the message from its id, txt is a dictionary
		txt = gmail.users().messages().get(userId='me', id=fucking_msg['id']).execute()
		# Get value of 'payload'
		payload = txt['payload']
		headers = payload['headers']

		# Look for Subject and Sender Email in the headers
		for d in headers:
			if d['name'] == 'Subject':
				subject = d['value']
			if d['name'] == 'From':
				sender = d['value']

		if not subject in valid_subjects:
			# Mark the email as READ
			gmail.users().messages().modify(
				userId = 'me',
				id = fucking_msg['id'],
				body = {'removeLabelIds': ['UNREAD']}
			).execute()
			raise Exception('Invalid subject')

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
			raise Exception('Secret key not found')
		
		email = {'subject':subject, 'sender':sender, 'context':body}
		
		# Mark the email as READ
		gmail.users().messages().modify(
			userId = 'me',
			id = fucking_msg['id'],
			body = {'removeLabelIds': ['UNREAD']}
		).execute()

		gui_print('SUCCESS: Got a new request email [{}].'.format(subject))
		return email, "No Error"

	except Exception as error:
		return None, str(error)

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

		file_size = round(os.stat(file).st_size / (1024.0 * 1024), ndigits = 2)

		content_type, encoding = mimetypes.guess_type(file)

		if content_type is None or encoding is not None:
			content_type = 'application/octet-stream'

		main_type, sub_type = content_type.split('/', 1)

		if main_type == 'text':
			with open(file, 'r') as opened_file:
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

		if main_type != 'text':
			encoders.encode_base64(msg)
		
		gui_print('SUCCESS: File part has been built, content type = {}, attachment\'s size = {} MB'.format(content_type, str(file_size)))
		return msg

	except Exception as err:
		gui_print('FAILED: Build file part unsuccessful: ' + str(err))

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
		gui_print('Creating email...')
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
		gui_print('SUCCESS: An email has been created.')
		return {
			'raw': encoded_message.decode('utf-8')
		}
	except Exception as err:
		gui_print('FAILED: Create email unsuccessfull: ' + str(err))
		return None

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
		gui_print('Sending an email...')
		message = service.users().messages().send(userId=user_id, body=body).execute()
		gui_print('SUCCESS: Sent an email.')
		return message
	except Exception as e:
		try:
			gui_print('FAILED: Send email failed: {}'.format(str(e)))
			gui_print('Trying to send again...')
			prepare_for_listen()
			message = service.users().messages().send(userId=user_id, body=body).execute()
			gui_print('SUCCESS: Sent an email.')
			return message
		except Exception as e:
			gui_print('FAILED: Can\'t send email: ' + str(e))
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

		# If error when parsing time string, raise exception
		if (restart_time == None):
			raise Exception('Parse time error')

		# If restart time is unreachable, raise exception
		if restart_time < current_time:
			raise Exception('Restart time [' + time_str + '] < current time')

		# Countdown to restart (in seconds)
		countdown = (restart_time - current_time).seconds

		# Schedule the restart
		os.system('shutdown -a')
		os.system('shutdown /r /t ' + str(countdown))

		# Ask current PC user whether he/she want to cancel the scheduled restart or not
		if messagebox.askyesno (
			title = SOFTWARE_NAME,
			message = "This PC is scheduled to restart at " + time_str + ' due to a request email\nDo you want to cancel it?'
		) == True:

			# If current pc user want to cancel the scheduled shutdown, do it
			os.system('shutdown -a')
			messagebox.showinfo(SOFTWARE_NAME, 'RESTART SCHEDULE CANCELED')
			raise Exception('PC\'s current user refused to restart at ' + time_str)
		
		else:
			gui_print('SUCCESS: Scheduled to restart this PC at {}.'.format(time_str))
			return True, "No error"

	except Exception as error:
		err_message = str(error)
		gui_print('FAILED: Schedule restart failed: ' + err_message)
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

		# If error while parsing the time string, raise exception
		if shutdown_time == None:
			raise Exception(err_msg)
		
		current_time = datetime.datetime.now()

		# If shutdown time is unreachable, raise exception
		if shutdown_time < current_time:
			raise Exception('Shutdown time [' + time_str + '] < Current time')
		
		# Countdown to shutdown (in seconds)
		countdown = (shutdown_time - current_time).seconds

		# Schedule the shutdown
		os.system('shutdown -a')
		os.system('shutdown /s /t ' + str(countdown))

		# Ask current PC user if he want to cancel the scheduled shutdown.
		if messagebox.askyesno(
			title = SOFTWARE_NAME,
			message = 'This PC is scheduled to shutdown at ' + time_str + ' due to a request email.\nDo you want to cancel it?\n'
		) == True:
			# If user want to cancel the scheduled shutdown, do it
			os.system('shutdown -a')
			messagebox.showinfo(
				title = SOFTWARE_NAME,
				message = 'Canceled shutdown schedule.'
			)
			raise Exception('Current PC\'s user refused to shutdown at ' + time_str)
		else:
			# User accepted the shutdown schedule.
			gui_print('SUCCESS: Scheduled to shutdown this PC at {}.'.format(time_str))
			return True, "No Error"

	except Exception as err:
		gui_print('FAILED: schedule shutdown failed: ' + str(err))
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
		gui_print('FAILED: Can\'t get sender\'s email address')
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
		# Get the time string from email's context
		tokens = [str.strip() for str in email['context'].splitlines()]
		TIME_POS = 1
		time = tokens[TIME_POS]

		# Schedule the restart
		action, err_message = restart(time)

		# Send a response email to the requester
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

		if send_email(gmail, 'me', response) == None:
			raise Exception("Send email failed.")

		gui_print('SUCCESS: RESTART request email has been successfully executed.')
	
	except Exception as err:
		gui_print('FAILED: {} request email execution failed: {}'.format(email['subject'], str(err)))

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
		# Get the shutdown time string from email's context
		tokens = [str.strip() for str in email['context'].splitlines()]
		time = tokens[1]

		# Schedule the shutdown
		action, err_msg = shutdown(time)

		# Send a response email to the requester
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

		if send_email(gmail, 'me', response) == None:
			raise Exception("Send email failed.")
		gui_print('SUCCESS: SHUTDOWN request email has been successfully executed.')

	except Exception as err:
		gui_print('FAILED: {} request email execution failed: {}'.format(email['subject'], str(err)))

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
		
		gui_print('SUCCESS: Copied file {} to {}'.format(src_path, result_path))
		return True, result_path

	except Exception as err:
		gui_print("FAILED: can't copy file: " + str(err))
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
		# Get the source file path and destination path from email's context
		tokens = [str.strip() for str in email['context'].splitlines()]
		src_path = tokens[1]
		dest_path = tokens[2]

		# Try copy file
		copy_result, msg = copy_file(src_path, dest_path)

		# Send response email to requester
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

		if send_email(gmail, 'me', response) == None:
			raise Exception("Send email failed.")
		gui_print('SUCCESS: COPY request email has been successfully executed.')

	except Exception as err:
		gui_print('FAILED: {} request email execution failed: {}'.format(email['subject'], str(err)))

def take_screenshot(save_dir = str):
	'''
	Take screenshot and save to file.
	-------------
	PARAMS:
	___save_dir (dtype = str): directory to save image file, image file name
	will be generated by screenshot time. Format: 'save_dir/%Y-%m-%d-%H-%M-%S.png'
	-------------
	RETURNS:
	___None, error_message (dtype = None, str): if error occurred.
	___True, path_to_saved_image (dtype = bool, str): if no error occurred.
	'''
	try:
		# Take screenshot
		sc = pyautogui.screenshot()
		
		# Make directory if it is not already exist
		if not os.path.isdir(save_dir):
			os.makedirs(save_dir)

		# File name is screenshot time.png
		file_name = str(datetime.datetime.now().strftime('[{}][screenshot].png'.format(DATETIME_FORMAT)))
		save_path = os.path.join(save_dir, file_name)

		# Save the screenshot image file
		sc.save(save_path)

		gui_print('SUCCESS: Screenshot taken.')
		return True, save_path

	except Exception as err:
		gui_print("FAILED: Can't take screenshot: " + str(err))
		return None, str(err)

def do_capture_request(email):
	'''
	Execute SCREEN CAPTURE request email.
	--------------
	PARAMS:
	___email (dtype = dict): the request email, contains 3 keys {'subject', 'sender', 'context'}.
	--------------
	RETURNS:
	No returns.
	'''
	try:
		# Try take screenshot
		sc, msg = take_screenshot(save_dir = TEMPORARY_FILES_PATH)
		
		# Send response email to requester	
		if sc == None:
			text = 'Take screenshot failed\nInfo: ' + msg
			screenshot_path = None
		else:
			text = ''
			screenshot_path = msg

		response = create_email (
			sender = auth_email_address,
			receiver = get_sender_address(email),
			subject = 'SCREEN CAPTURE',
			text = text,
			attachment_path = screenshot_path
		)

		# Delete the screenshot image after create email successfully
		if sc != None:
			os.remove(screenshot_path)

		if send_email(gmail, 'me', response) == None:
			raise Exception("Send email failed.")
		gui_print('SUCCESS: SCREEN CAPTURE request email has been executed.')

	except Exception as err:
		gui_print('FAILED: {} request email execution failed: {}'.format(email['subject'], str(err)))

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

		gui_print('SUCCESS: Got list of running processes.')
		return data, 'No error'

	except Exception as err:
		gui_print("FAILED: Can't get running processes list: " + str(err))
		return None, str(err)

def do_running_process_request(email):
	'''
	Execute the LIST PROCESSES request email.
	----------------
	PARAMS:
	___email (dtype = dict): the request email. Must contains key 'sender'
	----------------
	RETURNS:
	None.
	'''
	try:
		# Try get running processes
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
			data = DataFrame(running_processes)
			save_file = datetime.datetime.now().strftime('[{}][running-processes].csv'.format(DATETIME_FORMAT))
			save_path = os.path.join(TEMPORARY_FILES_PATH, save_file)
			data.to_csv(save_path, header = True, index = False)
		
		response = create_email (
			sender = auth_email_address,
			receiver = get_sender_address(email),
			subject = 'LIST PROCESSES',
			text = text,
			attachment_path = save_path
		)

		# Delete the running processes csv file after successfully create the email
		if running_processes != None:
			os.remove(save_path)

		if send_email(gmail, 'me', response) == None:
			raise Exception("Send email failed.")
		gui_print('SUCCESS: LIST PROCESSES request email has been executed.')

	except Exception as err:
		gui_print('FAILED: {} request email execution failed: {}'.format(email['subject'], str(err)))

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
		# Get the process name before killing it
		process_name = psutil.Process(pid = int(pid)).name()
		res = os.system('taskkill.exe /F /PID ' + str(pid))
		
		# If kill process failed, raise exception
		if res != 0:
			raise Exception('Kill process {} failed.'.format(pid))

		gui_print('SUCCESS: Process {}, ID = {} has been killed.'.format(process_name, pid))

		return True, process_name

	except Exception as err:
		gui_print("FAILED: Can't kill process PID {}: ".format(pid) + str(err))
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
		# Get the PID of target process from email's context
		tokens = [str.strip() for str in email['context'].splitlines()]
		pid = tokens[1]

		# Try killing that process
		kill, msg = kill_processes(pid)

		# Send response email to requester
		if kill == None:
			# If Kill process Failed
			text = 'Kill process [pid = {}] failed.\nInfo: {}'.format(pid, msg)
		else:
			# If Kill process Completed
			text = 'Successfully killed process [pid = {}, name = {}].'.format(pid, msg)
		
		response = create_email (
			sender = auth_email_address,
			receiver = get_sender_address(email),
			subject = 'KILL PROCESS',
			text = text,
			attachment_path = None
		)

		if send_email(gmail, 'me', response) == None:
			raise Exception("Send email failed.")
		gui_print('SUCCESS: KILL PROCESS request email has been executed.')
	
	except Exception as err:
		gui_print('FAILED: {} request email execution failed: {}'.format(email['subject'], str(err)))

def on_press(key):
	key = str(key).lower().replace("key.","").replace("'","")
	keylog = str(datetime.datetime.now()) + "\t" + key + "\n"
	with open(KEYLOG_PATH, "a") as fkeylog:
		fkeylog.write(keylog)

def key_log(time = int):
	try:
		global KEYLOG_PATH
		KEYLOG_PATH = os.path.join(TEMPORARY_FILES_PATH, "keylog.txt")

		if os.path.isfile(KEYLOG_PATH):
			os.remove(KEYLOG_PATH)

		with Listener(on_press = on_press) as keylogger:
			Timer(time, keylogger.stop).start()
			gui_print("Keylogging Started. Stop after {} seconds.".format(time))
			keylogger.join()
			gui_print("Keylogging Stopped.")

		return True, ""

	except Exception as err:
		gui_print("FAILED: keylogging failed: " + str(err))
		return None, str(err)

def do_catchkeys_request(email):
	try:
		# Get the seconds to catch key from email's context
		tokens = [str.strip() for str in email['context'].splitlines()]
		seconds = tokens[1]

		# Catch key and write to log file
		result, msg = key_log(time = int(seconds))
        
        # Send response email
		if result == None:
			text_content = "Key logging failed.\nInfo: " + msg
			attachment_file = None
		else:
			text_content = ""
			attachment_file = KEYLOG_PATH

		response = create_email (
            sender = auth_email_address,
            receiver = get_sender_address(email),
            subject = "KEYPRESS",
            text = text_content,
            attachment_path = attachment_file
        )

		if result != None:
			os.remove(KEYLOG_PATH)

		result = send_email(gmail, 'me', response)

		if result == None:
			raise Exception("Send email failed.")

		gui_print('SUCCESS: KEYPRESS request email has been executed.')
	
	except Exception as err:
		gui_print('FAILED: {} request email execution failed: {}'.format(email['subject'], str(err)))

def webcam_shot():
	try:
		camera_port = 0
		camera = VideoCapture(camera_port)
		result, image = camera.read()
		
		if result == False:
			raise Exception("Take webcam-shot failed")
		
		file_name = datetime.datetime.now().strftime("[{}][webcam-capture].png".format(DATETIME_FORMAT))
		save_path = os.path.join(TEMPORARY_FILES_PATH, file_name)
		imwrite(filename = save_path, img = image)
		gui_print("SUCCESS: Webcam captured.")
		return True, save_path
	
	except Exception as err:
		return None, str(err)
			
def do_webcam_capture_request(email):
	try:
		result, message = webcam_shot()

		if result == None:
			text = "Webcam capture failed.\nInfo: " + message
			attachment = None
		else:
			text = ""
			attachment = message
		
		response = create_email (
			sender = auth_email_address,
			receiver = get_sender_address(email),
			subject = "WEBCAM CAPTURE",
			text = text,
			attachment_path = attachment
		)

		if result == True:
			os.remove(message)

		result = send_email(gmail, "me", response)
		if result == None:
			raise Exception("Send email failed")

		gui_print('SUCCESS: WEBCAM CAPTURE request email has been executed.')

	except Exception as err:
		gui_print('FAILED: {} request email execution failed: {}'.format(email['subject'], str(err)))

def parse_data(full_path):
    try:
        full_path = re.sub(r'/', r'\\', full_path)
        hive = re.sub(r'\\.*$', '', full_path)
        if not hive:
            raise ValueError('Invalid \'full_path\' param.')
        if len(hive) <= 4:
            if hive == 'HKLM':
                hive = 'HKEY_LOCAL_MACHINE'
            elif hive == 'HKCU':
                hive = 'HKEY_CURRENT_USER'
            elif hive == 'HKCR':
                hive = 'HKEY_CLASSES_ROOT'
            elif hive == 'HKU':
                hive = 'HKEY_USERS'
        reg_key = re.sub(r'^[A-Z_]*\\', '', full_path)
        reg_key = re.sub(r'\\[^\\]+$', '', reg_key)
        reg_value = re.sub(r'^.*\\', '', full_path)
        # return hive, reg_key, reg_value
        return {'hive':hive, 'reg_key':reg_key, 'reg_value':reg_value}
    except:
        return {'hive':None, 'reg_key':None, 'reg_value':None}

def query_value(full_path):
    values = parse_data(full_path)
    try:
        opened_key = winreg.OpenKey(getattr(winreg, values['hive']), values['reg_key'], 0, winreg.KEY_READ)
        winreg.QueryValueEx(opened_key, values['reg_value'])
        winreg.CloseKey(opened_key)
        return True
    except:
        return False


def get_value(full_path):
    values = parse_data(full_path)
    try:
        opened_key = winreg.OpenKey(getattr(winreg, values['hive']), values['reg_key'], 0, winreg.KEY_READ)
        value_of_value, value_type = winreg.QueryValueEx(opened_key, values['reg_value'])
        winreg.CloseKey(opened_key)
        return ["1", value_of_value]
    except:
        return False

def dec_value(c):
    c = c.upper()
    if ord('0') <= ord(c) and ord(c) <= ord('9'):
        return ord(c) - ord('0')
    if ord('A') <= ord(c) and ord(c) <= ord('F'):
        return ord(c) - ord('A') + 10
    return 0

def str_to_bin(s):
    res = b""
    for i in range(0, len(s), 2):
        a = dec_value(s[i])
        b = dec_value(s[i + 1])
        res += (a * 16 + b).to_bytes(1, byteorder='big')
    return res

def str_to_dec(s):
    s = s.upper()
    res = 0
    for i in range(0, len(s)):
        v = dec_value(s[i])
        res = res*16 + v
    return res


def set_value(full_path, value, value_type):
    values = parse_data(full_path)
    try:
        winreg.CreateKey(getattr(winreg, values['hive']), values['reg_key'])
        opened_key = winreg.OpenKey(getattr(winreg, values['hive']), values['reg_key'], 0, winreg.KEY_WRITE)
        if 'REG_BINARY' in value_type:
            if len(value) % 2 == 1:
                value += '0'
            value = str_to_bin(value)
        if 'REG_DWORD' in value_type:
            if len(value) > 8:
                value = value[:8]
            value = str_to_dec(value)
        if 'REG_QWORD' in value_type:
            if len(value) > 16:
                value = value[:16]
            value = str_to_dec(value)                 
        
        winreg.SetValueEx(opened_key, values['reg_value'], 0, getattr(winreg, value_type), value)
        winreg.CloseKey(opened_key)
        return True
    except:
        return False


def delete_value(full_path):
    values = parse_data(full_path)
    try:
        opened_key = winreg.OpenKey(getattr(winreg, values['hive']), values['reg_key'], 0, winreg.KEY_WRITE)
        winreg.DeleteValue(opened_key, values['reg_value'])
        winreg.CloseKey(opened_key)
        return True
    except:
        return False


def query_key(full_path):
    values = parse_data(full_path)
    try:
        opened_key = winreg.OpenKey(getattr(winreg, values['hive']), values['reg_key'] + r'\\' + values['reg_value'], 0, winreg.KEY_READ)
        winreg.CloseKey(opened_key)
        return True
    except:
        return False


def create_key(full_path):
    values = parse_data(full_path)
    try:
        winreg.CreateKey(getattr(winreg, values['hive']), values['reg_key'] + r'\\' + values['reg_value'])
        return True
    except:
        return False


def delete_key(full_path):
    values = parse_data(full_path)
    try:
        winreg.DeleteKey(getattr(winreg, values['hive']), values['reg_key'] + r'\\' + values['reg_value'])
        return True
    except:
        return False

def do_registry_request(email):
	try:
		# Extract information from email's context
		tokens = [str.strip() for str in email['context'].splitlines()]
		request = tokens[1]
		full_path = tokens[2]
		value = tokens[3]
		value_type = tokens[4]

		# Try executing the request
		if request.lower() == 'delete':
			result = delete_value(full_path)
		elif request.lower() == 'set':
			result = set_value(full_path, value, value_type)
		
		# If failed, then raise exception
		if result == False:
			raise Exception("{} registry value failed.".format(request))

		gui_print("SUCCESS: Executed {} registry value request email.".format(request))

	except Exception as err:
		gui_print('FAILED: {} request email execution failed: {}'.format(email['subject'], str(err)))

def webcam_record(record_time = int):
    try:
		# Limit the file size to under 25MB
        if record_time > LIMIT_VIDEO_LENGTH:
            record_time = LIMIT_VIDEO_LENGTH

        file_name = datetime.datetime.now().strftime('[{}][webcam-record].mp4'.format(DATETIME_FORMAT))
        save_path = os.path.join(TEMPORARY_FILES_PATH, file_name)

        camera_port = 0
        video_codec = VideoWriter_fourcc(*'MP4V')
        fps = 24.0
        video_writer = VideoWriter(save_path, video_codec, fps, (640, 480))
        video_capture = VideoCapture(camera_port)

        total_frame = fps * float(record_time)
        writed_frame = 0

        gui_print('Started webcam recording, stop after {} second(s)'.format(str(record_time)))
        while True:
            frame = video_capture.read()[1]
            video_writer.write(frame)
            writed_frame += 1
            if writed_frame >= total_frame:
                break
        gui_print('Stopped webcam recording')

        video_capture.release()
        video_writer.release()

        return True, save_path

    except Exception as err:
        return None, str(err)

def do_webcam_record_request(email):
	try:
		tokens = [str.strip() for str in email['context'].splitlines()]
		time = int(tokens[1])

		record_result, return_message = webcam_record(time)

		if record_result == None:
			text = 'Webcam record failed.\nInfo: {}'.format(return_message)
			attachment = None
		else:
			text = ''
			if time > LIMIT_VIDEO_LENGTH:
				text = 'Sorry, we have to limit the record time to {} seconds because of limit of Gmail API in sending email.'.format(LIMIT_VIDEO_LENGTH)
			attachment = return_message

		response = create_email (
			sender = auth_email_address,
			receiver = get_sender_address(email),
			subject = email['subject'],
			text = text,
			attachment_path = attachment
		)

		if record_result != None:
			os.remove(return_message)

		send_result = send_email(gmail, 'me', response)

		if send_result == None:
			raise Exception('Send email failed')

		gui_print('SUCCESS: Webcam Record request email has been executed')
		
	except Exception as err:
		gui_print('FAILED: {} request email execution failed: {}'.format(email['subject'], str(err)))

def prepare_for_listen():
	try:
		global SCOPES, creds, auth_email_address, gmail

		auth_email_address = "Undefined"
		creds = None

		# Create a folder for temporary files
		if not os.path.isdir(TEMPORARY_FILES_PATH):
			os.makedirs(TEMPORARY_FILES_PATH)

		# if you modify this SCOPES, you need to delete file token.pickle first
		# unless the code will not run
		SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

		# Load the credentials
		# Credential is saved in token.pickle
		if os.path.exists(TOKEN_FILE):
			with open(TOKEN_FILE, 'rb') as token:
				creds = pickle.load(token)

		# If credentials are not available or are invalid, ask the user to log in.
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				messagebox.showinfo(SOFTWARE_NAME, "Please log in to your Google account.")
				flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
				creds = flow.run_local_server(port=0)
			# Save the access token in token.pickle file for the next run
			with open(TOKEN_FILE, 'wb') as token:
				pickle.dump(creds, token)

			# Connect to the Gmail API
		gmail = build('gmail', 'v1', credentials=creds)

		# Email address if authenticated Gmail user.
		auth_email_address = gmail.users().getProfile(userId = 'me').execute()['emailAddress']
		gui_print('SUCCESS: Connected to Gmail service.\nAuthenticated user: {}'.format(auth_email_address))
	
	except Exception:
		# If error occurred, try log in again
		if os.path.isfile(TOKEN_FILE):
			os.remove(TOKEN_FILE)
		prepare_for_listen()

request_dict = {
	'SHUTDOWN' : do_shutdown_request,
	'RESTART' : do_restart_request,
	'COPY FILE' : do_copy_request,
	'SCREEN CAPTURE' : do_capture_request,
	'WEBCAM CAPTURE' : do_webcam_capture_request,
	'WEBCAM RECORD' : do_webcam_record_request,
	'LIST PROCESSES' : do_running_process_request,
	'KILL PROCESS' : do_kill_process_request,
	'KEYPRESS' : do_catchkeys_request,
	'REGISTRY KEY' : do_registry_request
}

def listen():
	global SCOPES, creds, gmail, auth_email_address
	try:
		global stop_listen
		stop_listen = False

		gui_print("Listening...")
		while not stop_listen:
			email = read_email()[0]
			if (email != None):
				request_dict[email['subject']](email)
				gui_print("Listening...")

	except Exception as err:
		messagebox.showerror(SOFTWARE_NAME, 'Error while listening: ' + str(err))

def terminate_mainloop():
	global stop_listen
	really = messagebox.askyesno(SOFTWARE_NAME, "Are you sure you want to exit the program?")
	if really == True:
		save_account =  messagebox.askyesno (
			title = SOFTWARE_NAME,
			message = "Do you want to save current email account [{}] for using next time?".format(auth_email_address)
		)

		if save_account == False:
			if os.path.isfile(TOKEN_FILE):
				os.remove(TOKEN_FILE)

		stop_listen = True
		icon.stop()
		main_window.destroy()

def about_info():
	message = "PC Remote Control Using Email v1.0"
	message = message + "\nDeveloped by Bao-Anh Tran\nContact via: tranbaoanh.student.hcmus@gmail.com"
	messagebox.showinfo("About", message)

def how_to_use():
	try:
		global auth_email_address
		README_PATH = "README.md"
		with open(README_PATH, "rt") as instructions:
			message = "Send request emails to this email address: {}\n\n".format(auth_email_address)
			message = message + instructions.read().replace("*","")
			messagebox.showinfo("How to use this software?", message)
	except Exception as err:
		message = "Send request emails to this email address: {}\n{}\n".format(auth_email_address, str(err))
		messagebox.showerror("How to use this software?", message)

def show_window():
	global hide_or_show, icon
	main_window.after(0, func = main_window.deiconify)
	hide_or_show = 'Hide'
	icon.update_menu()

def system_tray_icon():
	global icon, pause_or_continue, hide_or_show
	pause_or_continue = 'Pause'
	hide_or_show = 'Hide'
	image = Image.open("icon.ico")
	menu = (
		pystray.MenuItem(lambda text: hide_or_show, show_hide_window),
		pystray.MenuItem(lambda text: pause_or_continue, pause_listen),
		pystray.MenuItem('About', about_info),
		pystray.MenuItem('How to use?', how_to_use),
		pystray.MenuItem('Quit', terminate_mainloop)
	)
	icon = pystray.Icon("email-remote-control-icon", image, SOFTWARE_NAME, menu)
	icon.run()

def hide_window():
	global hide_or_show, icon
	main_window.withdraw()
	hide_or_show = 'Show'
	icon.update_menu()

def show_hide_window():
	global icon, hide_or_show

	if hide_or_show == 'Hide':
		hide_window()
	elif hide_or_show == 'Show':
		show_window()

def pause_listen():
	global stop_listen, btn_pause, pause_or_continue, icon

	if btn_pause['text'] == 'Pause':
		stop_listen = True
		btn_pause['text'] = 'Continue'
		pause_or_continue = 'Continue'
		icon.update_menu()
		gui_print("Paused listening...")

	elif btn_pause['text'] == 'Continue':
		Thread(target = listen, daemon = True).start()
		btn_pause['text'] = 'Pause'
		pause_or_continue = 'Pause'
		icon.update_menu()
		gui_print("Continued listening...")

def graphical_UI():
	global main_window, txt, btn_exit, btn_hide, btn_about, btn_pause

	main_window = tkinter.Tk()
	main_window.title(SOFTWARE_NAME)
	main_window.iconbitmap("icon.ico")
	main_window.geometry("800x450")
	main_window.resizable(width=False, height=False)

	txt = Text(main_window, width=700)

	buttons = Frame(main_window)
	buttons.pack(side = TOP)

	btn_pause = Button(buttons, text = "Pause", command = pause_listen)
	btn_pause.pack(side = LEFT, padx = 5)

	btn_how_to_use = Button(buttons, text = "How to use?", command = how_to_use)
	btn_how_to_use.pack(side = LEFT, padx = 5)

	btn_about = Button(buttons, text = "About", command = about_info)
	btn_about.pack(side = LEFT, padx = 5)

	btn_hide = Button(buttons, text = "Hide", command = hide_window)
	btn_hide.pack(side = LEFT, padx = 5)

	btn_exit = Button(buttons, text="Exit", command = terminate_mainloop)
	btn_exit.pack(side = LEFT, padx = 5)

	main_window.protocol('WM_DELETE_WINDOW', hide_window)
	
	prepare_for_listen()

	global auth_email_address
	receiver = Label (
		master = main_window,
		text = "Email to receive request: {}".format(auth_email_address)
	)

	receiver.pack(side = BOTTOM)

	start_listen = Thread(target = listen, daemon = True)
	start_listen.start()
	main_window.mainloop()

main_ui = Thread(target = graphical_UI)
tray_icon = Thread(target = system_tray_icon, daemon = True)
main_ui.start()
tray_icon.start()