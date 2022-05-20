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
	print('Start build file part ' + file)
	try:
		# Check if file exist:
		if not os.path.isfile(file):
			raise Exception('File ' + file + ' not exist.')

		print('Guess file type now')
		content_type, encoding = mimetypes.guess_type(file)

		if content_type is None or encoding is not None:
			content_type = 'application/octet-stream'

		print('Content Type = ' + content_type)

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
		
		print('Build file part SUCCESS')
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
	print('Start creating email with attachments.')
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
		print('Create email with attachment SUCCESS')
		return {
			'raw': encoded_message
		}
	except Exception as err:
		messagebox.showwarning(SOFTWARE_NAME, 'Create email with attachment failed: ' + str(err))

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
				# Get process name & pid from process object.
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
		return data, 'No error'

	except Exception as err:
		return None, str(err)

data, msg = list_processes()

df = pd.DataFrame(data)

save_file = datetime.datetime.now().strftime('[%d-%m-%Y-%H-%M-%S][running-processes].csv')
save_path = os.path.join(TEMPORARY_FILES_PATH, save_file)

df.to_csv(save_path, header = True, index = False)

attachment = build_file_part(save_path)
print(type(attachment))

os.remove(save_path)