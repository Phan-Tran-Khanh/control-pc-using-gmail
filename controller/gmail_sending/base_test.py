from __future__ import print_function
import os
import unittest

from apiclient import discovery

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

CREDENTIALS_PATH = 'controller/gmail_sending/credentials.json'
TOKEN_PATH = 'controller/gmail_sending/token.json'

class BaseTest(unittest.TestCase):

    RECIPIENT = 'computer.networking.team.18@gmail.com'
    USER = 'laxohajc@gmail.com'

    @classmethod
    def setUpClass(cls):
        cls.service = cls.create_service()

    @classmethod
    def create_credentials(cls):
        scope = ['https://www.googleapis.com/auth/gmail.compose',
                 'https://www.googleapis.com/auth/gmail.send',
                 'https://www.googleapis.com/auth/gmail.labels',
                 'https://www.googleapis.com/auth/gmail.settings.basic',
                 'https://www.googleapis.com/auth/gmail.settings.sharing',
                 'https://mail.google.com/']

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, scope)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, scope)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        return creds

    @classmethod
    def create_service(cls):
        credentials = cls.create_credentials()
        return discovery.build('gmail', 'v1', credentials=credentials)


if __name__ == '__main__':
    unittest.main()