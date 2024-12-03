from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("You need to log in first.", "warning")
                return redirect(url_for('auth_blueprint.login'))
            
            if current_user.role != required_role:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for('home_blueprint.index'))
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
