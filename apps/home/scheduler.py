from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import SchedulerEvent
from apscheduler.schedulers.base import SchedulerNotRunningError
from datetime import datetime
from flask import current_app
from apps.authentication.models import Reminder
from flask_mail import Message

scheduler = BackgroundScheduler()

def send_reminders():
    """Send email reminders for unsent tasks."""
    with current_app.app_context():
        now = datetime.utcnow()
        reminders = Reminder.query.filter(Reminder.reminder_time <= now, Reminder.sent == False).all()

        for reminder in reminders:
            msg = Message('Reminder', recipients=[reminder.email])
            msg.body = reminder.message
            current_app.mail.send(msg)

            reminder.sent = True
            current_app.db.session.commit()

def initialize_scheduler(app):
    """Configure and start the scheduler."""
    scheduler.add_job(send_reminders, 'interval', minutes=1)  # Run every minute
    scheduler.start()

    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        """Shut down the scheduler gracefully on app shutdown."""
        try:
            scheduler.shutdown(wait=False)
        except SchedulerNotRunningError:
            # The scheduler is not running, so no need to shut it down.
            pass
