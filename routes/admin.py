from flask import Blueprint, render_template
from flask_login import login_required
from functools import wraps
from models.user import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to access this page.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
def index():
    return "Admin dashboard (placeholder)"

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """View and manage users"""
    return render_template('admin/users.html')

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Detailed analytics and reports"""
    return render_template('admin/analytics.html') 