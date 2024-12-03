from flask import current_app
from apps import db, mail
from flask_mail import Message
from authentication.models import Reminder

def send_reminder_email(reminder_id):
    reminder = Reminder.query.get(reminder_id)
    if reminder:
        msg = Message(
            subject=f"Reminder: {reminder.title}",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[reminder.email],
            body=f"Don't forget your reminder: {reminder.description}"
        )
        mail.send(msg)
