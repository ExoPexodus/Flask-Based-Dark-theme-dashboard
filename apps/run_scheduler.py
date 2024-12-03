# run_scheduler.py

from apps import create_app
from apps.home.scheduler import scheduler

app = create_app('config.DebugConfig')  # Replace with your config

with app.app_context():
    scheduler.start()

print("Scheduler is running. Press Ctrl+C to exit.")
try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
