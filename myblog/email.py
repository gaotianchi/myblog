"""
Summary: Email servive.
Created at: 2023-12-06
Author: Gao Tianchi
"""

from flask_mail import Message

from .config import get_config
from .flaskexten import mail

config = get_config()


def send_email(subject, recipients, body):
    message = Message(
        subject=subject, recipients=recipients, body=body, sender=config.MAIL_USERNAME
    )
    mail.send(message)
