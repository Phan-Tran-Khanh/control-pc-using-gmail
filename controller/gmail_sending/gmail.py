import unittest

import send_email
from base_test import BaseTest
from googleapiclient.errors import HttpError


class Gmail(BaseTest):

    SECRET_KEY = '019250304'

    """
    TODO: GET GMAIL.USER from AUTHORIZATION
    TODO: READ USER'S EMAIL and DELETE IT
    """

    @classmethod
    def setUpClass(cls):
        super(Gmail, cls).setUpClass()

    def setUp(self):
        super(Gmail, self).setUp()

    def tearDown(self):
        super(Gmail, self).tearDown()

    # [START testing functions]
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
        self.assertIsNotNone(sent_message)


    # [END testing functions]

    @classmethod
    def setUpRecipient(cls, email_address: str):
        """Set up receiver's email address

        Args:
        email_address: Receiver's email address

        Returns:
        None
        """

        cls.RECIPIENT = email_address

    # BUTTON "SHUTDOWN"
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

    # BUTTON "RESTART"
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

    # BUTTON "FILE COPYING"
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

    # BUTTON "FULLSCREEN CAPTURE"
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

    # BUTTON "WEBCAM CAPTURE"
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

    # BUTTON "LIST PROCESSES"
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
    
    # BUTTON "KILL PROCESS"
    def send_kill_process(self, process_name: str):
        """Send a message requesting your personal computer to kill a running process.

        Args:
        process_name<name.exe>: Process' name.

        Returns:
        error: string (exception).
        """
        
        msg_text = self.SECRET_KEY + '\n' + process_name
        message = send_email.create_message(Gmail.USER,
                                            Gmail.RECIPIENT,
                                            'KILL PROCESS',
                                            msg_text)
        try:
            sent_message = send_email.send_message(self.service, 'me', message)
        except HttpError as error:
            return str(error)

    # BUTTON "DETECT KEYPRESS"
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

    # BUTTON "EDIT VALUE of a REGISTRY KEY"
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

        msg_text = self.SECRET_KEY + '\n' + regis_path
        if value and value_type:
            msg_text += '\n' + value + '\n' + value_type
        message = send_email.create_message(Gmail.USER,
                                            Gmail.RECIPIENT,
                                            'REGISTRY KEY',
                                            msg_text)
        try:
            sent_message = send_email.send_message(self.service, 'me', message)
        except HttpError as error:
            return str(error)

if __name__ == '__main__':
    unittest.main()
    """ a = Gmail()
    a.setUpClass()
    a.test_send_email() """