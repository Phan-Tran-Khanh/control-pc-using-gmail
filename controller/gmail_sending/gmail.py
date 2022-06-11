import unittest
import send_email
import base64
import os
from base_test import BaseTest
from googleapiclient.errors import HttpError

class Gmail(BaseTest):

    SECRET_KEY = '019250304'

    @classmethod
    def setUpClass(cls):
        super(Gmail, cls).setUpClass()

    def setUp(self):
        super(Gmail, self).setUp()

    def tearDown(self):
        super(Gmail, self).tearDown()

    # [START testing functions]
    """ 
    def test_create_message(self):
        message = send_email.create_message(Gmail.USER,
                                            Gmail.RECIPIENT,
                                            'Test',
                                            'Hello!')
        self.assertIsNotNone(message)  # Weak assertion

    def test_create_message_with_attachment(self):
        message = send_email.create_message_with_attachment(Gmail.USER,
                                                            Gmail.RECIPIENT,
                                                            'Test',
                                                            'Hello!',
                                                            'files/photo.jpg')
        self.assertIsNotNone(message)  # Weak assertion

    def test_create_draft(self):
        message = send_email.create_message(Gmail.USER,
                                            Gmail.RECIPIENT,
                                            'Test',
                                            'Hello!')
        draft = send_email.create_draft(self.service, 'me', message)
        self.assertIsNotNone(draft)
        self.service.users().drafts().delete(userId='me', id=draft.get('id'))

    def test_send_email(self):
        message = send_email.create_message_with_attachment(Gmail.USER,
                                                            Gmail.RECIPIENT,
                                                            'Test',
                                                            'Hello!',
                                                            'files/photo.jpg')
        sent_message = send_email.send_message(self.service, 'me', message)
        self.assertIsNotNone(sent_message) """


    # [END testing functions]

    @classmethod
    def setUpRecipient(cls, email_address: str):
        """Set up receiver's email address

        Args:
        email_address: Receiver's email address.

        Returns:
        None
        """

        cls.RECIPIENT = email_address

    def receive_email(self, subject: str):
        """
        Reads response email on subject from controlled computer.
        
        Args:
        subject: Subject of the email.
        attachment: Whether the email attached file or not.
        
        Returns:
        plain_text: Plain text of the email.
        attachments: Attachments' save location.
        error: None

        Remember to leave attachment folder empty.
        Remove files from attachment folder after this method carries out successful.

        Exception:
        None, None, error: string
        """

        query = "is:unread from:(" + self.RECIPIENT + ") subject:" + subject

        try:
            # Get one latest unread email
            result = self.service.users().messages().list(
                maxResults = 1,
                userId = 'me',
                q = query,
                labelIds = ['INBOX']
            ).execute()

            # If result returns no email
            if result['resultSizeEstimate'] == 0:
                raise Exception("No response at the moment.")
            
            # Messages is a list of dictionaries where each dictionary contains a message id.
            email = result.get('messages')[0]

            if not email:
                raise Exception("No response at the moment.")

            # Get the message from its id, content is a dictionary.
            content = self.service.users().messages().get(userId='me', id=email['id']).execute()

            # Get value of 'payload' - the parsed email structure in the message parts.
            payload = content['payload']

            # Get body data, depends on mimeType of the Email
            mimeType = payload['mimeType']
            if mimeType == 'text/plain' or mimeType == 'text/html':
                data = payload['body']['data']
            else:
            # This only applies to container MIME message parts, for example multipart/*.
                data = None
                parts = payload.get('parts')[0]
                mimeType = parts['mimeType']
                while (mimeType != 'text/plain' and mimeType != 'text/html') and 'parts' in parts:
                    part = parts.get('parts')[0]
                    mimeType = part['mimeType']
                    parts = part
                if parts['body']['data']:
                    data = parts['body']['data']

            
            # The Body of the message is in Encrypted format. So, we have to decode it.
            # Get the data and decode it with base 64 decoder.
            plain_text = None
            # If this email has text
            if data:
                data = data.replace("-","+").replace("_","/")
                decoded_data = base64.b64decode(data)
                plain_text = decoded_data.decode('utf-8')

            # Now, the data obtained is in lxml. So, we will parse
            # it with BeautifulSoup library
            """ soup = BeautifulSoup(decoded_data, 'lxml')
            plain_text = str(soup.find('p').contents[0]) """

            attachments = None
            
            # If this message is not plain text only.
            if 'parts' in payload:
                # running in folder gmail_sending
                save_location = os.getcwd() + "\\attachment"
                attachments = []
                # Searches for attachment part.
                for msgPayload in payload['parts']:
                    # Get attachment's file name.
                    filename = msgPayload['filename']
                    body = msgPayload['body']
                    # If this message part contains attachment.
                    if 'attachmentId' in body:
                        attachment_enc = self.service.users().messages().attachments().get(
                            userId = 'me',
                            messageId = email['id'],
                            id = body['attachmentId']
                        ).execute()
                        attachment_dec = base64.urlsafe_b64decode(attachment_enc.get('data').encode('UTF-8'))

                        # Saves the attachment on user computer.
                        filepath = os.path.join(save_location, filename)
                        attachments.append(filepath)
                        with open(filepath, 'wb') as file:
                            file.write(attachment_dec)
            
            # Marks this email as READ
            self.service.users().messages().modify(
                userId = 'me',
                id = email['id'],
                body = {'removeLabelIds': ['UNREAD']}
            ).execute()

            return plain_text, attachments, None

        except Exception as error:
            return None, None, str(error)

    # BUTTON [SHUTDOWN]
    def send_shutdown(self, time: str):
        """Send a message requesting your personal computer to shut down.

        Args:
        time<hh:mm:ss>: Shutdown time

        Returns:
        error: string (exception).
        """
        
        msg_text = self.SECRET_KEY + '\n' + time
        message = send_email.create_message(Gmail.USER,
                                            Gmail.RECIPIENT,
                                            'SHUTDOWN',
                                            msg_text)
        try:
            sent_message = send_email.send_message(self.service, 'me', message)
        except HttpError as error:
            return str(error)

    # BUTTON [RESTART]
    def send_restart(self, time: str):
        """Send a message requesting your personal computer to restart.

        Args:
        time<hh:mm:ss>: Restart time

        Returns:
        error: string (exception).
        """
        
        msg_text = self.SECRET_KEY + '\n' + time
        message = send_email.create_message(Gmail.USER,
                                            Gmail.RECIPIENT,
                                            'RESTART',
                                            msg_text)
        try:
            sent_message = send_email.send_message(self.service, 'me', message)
        except HttpError as error:
            return str(error)

    # BUTTON [FILE COPYING]
    def send_copy_file(self, src_path: str, des_path: str):
        """Send a message requesting your personal computer to copy file.

        Args:
        src_path: File's old path.
        des_path: File's new path.

        Returns:
        error: string (exception).
        """
        
        msg_text = self.SECRET_KEY + '\n' + src_path + '\n' + des_path
        message = send_email.create_message(Gmail.USER,
                                            Gmail.RECIPIENT,
                                            'COPY FILE',
                                            msg_text)
        try:
            sent_message = send_email.send_message(self.service, 'me', message)
        except HttpError as error:
            return str(error)

    # BUTTON [FULLSCREEN CAPTURE]
    def send_capture_screen(self):
        """Send a message requesting your personal computer to capture fullscreen.

        Args:
        None

        Returns:
        error: string (exception).
        """
        
        msg_text = self.SECRET_KEY
        message = send_email.create_message(Gmail.USER,
                                            Gmail.RECIPIENT,
                                            'SCREEN CAPTURE',
                                            msg_text)
        try:
            sent_message = send_email.send_message(self.service, 'me', message)
        except HttpError as error:
            return str(error)

    # BUTTON [WEBCAM CAPTURE]
    def send_capture_webcam(self):
        """Send a message requesting your personal computer to capture its webcam.

        Args:
        None

        Returns:
        error: string (exception).
        """
        
        msg_text = self.SECRET_KEY
        message = send_email.create_message(Gmail.USER,
                                            Gmail.RECIPIENT,
                                            'WEBCAM CAPTURE',
                                            msg_text)
        try:
            sent_message = send_email.send_message(self.service, 'me', message)
        except HttpError as error:
            return str(error)

    # BUTTON [WEBCAM RECORD]
    def send_record_webcam(self, time: str):
        """Send a message requesting your personal computer to record its webcam.

        Args:
        time<integer>: Recording time

        Returns:
        error: string (exception).
        """
        
        msg_text = self.SECRET_KEY + '\n' + time
        message = send_email.create_message(Gmail.USER,
                                            Gmail.RECIPIENT,
                                            'WEBCAM RECORD',
                                            msg_text)
        try:
            sent_message = send_email.send_message(self.service, 'me', message)
        except HttpError as error:
            return str(error)

    # BUTTON [LIST PROCESSES]
    def send_list_processes(self):
        """Send a message requesting your personal computer to list running processes.

        Args:
        None

        Returns:
        error: string (exception).
        """
        
        msg_text = self.SECRET_KEY
        message = send_email.create_message(Gmail.USER,
                                            Gmail.RECIPIENT,
                                            'LIST PROCESSES',
                                            msg_text)
        try:
            sent_message = send_email.send_message(self.service, 'me', message)
        except HttpError as error:
            return str(error)
    
    # BUTTON [KILL PROCESS]
    def send_kill_process(self, process_id: str):
        """Send a message requesting your personal computer to kill a running process.

        Args:
        process_id: PID.

        Returns:
        error: string (exception).
        """
        
        msg_text = self.SECRET_KEY + '\n' + process_id
        message = send_email.create_message(Gmail.USER,
                                            Gmail.RECIPIENT,
                                            'KILL PROCESS',
                                            msg_text)
        try:
            sent_message = send_email.send_message(self.service, 'me', message)
        except HttpError as error:
            return str(error)

    # BUTTON [DETECT KEYPRESS]
    def send_keypress(self, time: str):
        """Send a message requesting your personal computer to detect keypress from its user.

        Args:
        time<integer>: Detecting time

        Returns:
        error: string (exception).
        """
        
        msg_text = self.SECRET_KEY + '\n' + time
        message = send_email.create_message(Gmail.USER,
                                            Gmail.RECIPIENT,
                                            'KEYPRESS',
                                            msg_text)
        try:
            sent_message = send_email.send_message(self.service, 'me', message)
        except HttpError as error:
            return str(error)

    # BUTTON [EDIT VALUE of a REGISTRY KEY]
    def send_registry_key(self, regis_path: str, value: str, value_type: str):
        """Send a message requesting your personal computer to edit value of a registry key.

        Args:
        regis_path: Full path of registry key.
        value: Registry's value (can be None).
        value_type: Type of value (can be None).

        If both value and value_type are None, it will delete registry key's value.

        Returns:
        error: string (exception).
        """

        msg_text = None
        if value and value_type:
            msg_text = 'set' + '\n' + regis_path + '\n' + value + '\n' + value_type
        else:
            msg_text = 'delete' + '\n' + regis_path
        msg_text = self.SECRET_KEY + '\n' + msg_text

        message = send_email.create_message(Gmail.USER,
                                            Gmail.RECIPIENT,
                                            'REGISTRY KEY',
                                            msg_text)
        try:
            sent_message = send_email.send_message(self.service, 'me', message)
        except HttpError as error:
            return str(error)

def open_file(locations: list):
    for location in locations:
        os.system(location)

if __name__ == '__main__':
    unittest.main()

    """
    Step 1: Call setUpClass() method
        Explanation: Because access token can be expired.
        And we need to check it and request if needed.

        Always call this function before using any Gmail service 
        like: send email, receive email, etc.
    Step 2: Call send_*() method. 
        With parameters from user's input.
    Step 3: Call receive_email() method.
        GUI can use plain_text or error for window message.
    Step 4: Call open_file() if there's attachment in the email.
        This will use command line code to open attachment on user's computer.
        So, no need GUI handle this (I guess).
    """
