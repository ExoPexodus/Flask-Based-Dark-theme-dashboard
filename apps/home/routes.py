# apps/home/routes.py

from apps.home import blueprint
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime
from apps import db
from apps.authentication.models import Reminder  # Adjust import as needed
from apps.decorators import role_required
from jinja2 import TemplateNotFound
from datetime import datetime

# ---------------------------
# Routes for Reminder Management
# ---------------------------

@blueprint.route('/reminders', methods=['GET', 'POST'])
@login_required
def reminders():
    """View and manage reminders."""
    if request.method == 'POST':
        email = request.form.get('email')
        message = request.form.get('message')
        reminder_time = request.form.get('reminder_time')

        # Log the received data for debugging
        current_app.logger.debug(f"Received form data: email={email}, message={message}, reminder_time={reminder_time}")

        try:
            # Try parsing the date, support both 'YYYY-MM-DD HH:MM:SS' and 'HH:MM'
            if len(reminder_time) == 5 and reminder_time.count(':') == 1:  # HH:MM format
                # Get today's date and combine it with the time
                reminder_time = datetime.combine(datetime.today(), datetime.strptime(reminder_time, '%H:%M').time())
            else:  # Full datetime format
                reminder_time = datetime.strptime(reminder_time, '%Y-%m-%d %H:%M:%S')

            current_app.logger.debug(f"Parsed reminder time: {reminder_time}")

            # Create the new reminder object, including the current user's ID
            new_reminder = Reminder(
                email=email,
                message=message,
                reminder_time=reminder_time,
                sent=False,  # Default value for new reminders
                user_id=current_user.id  # Use the current user's ID
            )

            # Log the created reminder object before adding it to the session
            current_app.logger.debug(f"New reminder object: {new_reminder}")

            # Add the reminder to the session
            db.session.add(new_reminder)
            db.session.commit()

            # Log the success of the commit
            current_app.logger.debug("Reminder added successfully!")

            flash('Reminder added successfully!', 'success')

        except ValueError:
            current_app.logger.error("Invalid date format received.")
            flash('Invalid date format. Use YYYY-MM-DD HH:MM:SS or HH:MM.', 'danger')
        except Exception as e:
            current_app.logger.error(f"Error occurred while adding reminder: {e}")
            flash('An error occurred. Please try again.', 'danger')

    reminders = Reminder.query.order_by(Reminder.reminder_time).all()
    return render_template('home/reminders.html', reminders=reminders)


@blueprint.route('/delete_reminder/<int:reminder_id>', methods=['POST'])
@login_required
def delete_reminder(reminder_id):
    """Delete a specific reminder."""
    reminder = Reminder.query.get_or_404(reminder_id)
    db.session.delete(reminder)
    db.session.commit()
    flash('Reminder deleted successfully!', 'success')
    return redirect(url_for('home_blueprint.reminders'))

# ---------------------------
# Routes for Dashboards
# ---------------------------

@blueprint.route('/index')
@login_required
def index():
    """Redirect user to the appropriate dashboard based on their role."""
    if current_user.role == 'admin':
        return redirect(url_for('home_blueprint.admin_dashboard'))
    elif current_user.role == 'viewer':
        return redirect(url_for('home_blueprint.viewer_dashboard'))
    return render_template('home/index.html', segment='index')


@blueprint.route('/dashboard')
@login_required
def dashboard():
    """Serve the dashboard based on user role."""
    if current_user.role == 'admin':
        return render_template('home/admin-dashboard.html', segment='dashboard')
    elif current_user.role == 'viewer':
        return render_template('home/viewer-dashboard.html', segment='dashboard')
    return render_template('home/index.html', segment='dashboard')


@blueprint.route('/admin-dashboard')
@login_required
@role_required('admin')  # Admin-only route
def admin_dashboard():
    """Admin dashboard."""
    return render_template('home/admin-dashboard.html', segment='admin-dashboard')


@blueprint.route('/viewer-dashboard')
@login_required
@role_required('viewer')  # Viewer-only route
def viewer_dashboard():
    """Viewer dashboard."""
    return render_template('home/viewer-dashboard.html', segment='viewer-dashboard')


# ---------------------------
# General Route Handling
# ---------------------------

@blueprint.route('/<template>')
@login_required
def route_template(template):
    """Serve arbitrary templates under the 'home' directory."""
    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page for segment highlighting
        segment = get_segment(request)
        return render_template(f"home/{template}", segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except Exception:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):
    """Extract the current page segment from the request URL."""
    try:
        segment = request.path.split('/')[-1]
        return segment if segment else 'index'
    except Exception:
        return None
