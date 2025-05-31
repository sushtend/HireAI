from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    # Temporarily disabled login
    return redirect(url_for('index'))
    
    # Original login code (commented out)
    # user = User(1, "test@example.com", "admin")
    # login_user(user)
    # flash('Logged in successfully!')
    # next_page = request.args.get('next')
    # if next_page:
    #     return redirect(next_page)
    # return redirect(url_for('index'))

@auth_bp.route('/logout')
# @login_required  # Temporarily disabled
def logout():
    # Temporarily disabled logout
    return redirect(url_for('index'))
    
    # Original logout code (commented out)
    # logout_user()
    # flash('Logged out successfully!')
    # return redirect(url_for('index')) 