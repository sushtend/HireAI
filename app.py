from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask_login import LoginManager, login_required, current_user
import os
from dotenv import load_dotenv
# from posthog import Posthog
# from supabase import create_client, Client
from models.user import User

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# --- PostHog Initialization (Server-side - not used for client-side tracking) ---
# posthog = Posthog(
#     project_api_key=os.getenv('POSTHOG_API_KEY'),
#     host=os.getenv('POSTHOG_HOST', 'https://app.posthog.com')
# )
# ------------------------------------------------------------------------------

# --- PostHog Client-Side Config ---
POSTHOG_API_KEY = os.getenv('POSTHOG_API_KEY')
POSTHOG_HOST = os.getenv('POSTHOG_HOST', 'https://us.i.posthog.com') # Use provided host

@app.context_processor
def inject_posthog_vars():
    """Inject PostHog environment variables into all templates."""
    return {
        'posthog_api_key': POSTHOG_API_KEY,
        'posthog_host': POSTHOG_HOST
    }
# ----------------------------------

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Import blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.recruiter import recruiter_bp
from routes.candidate import candidate_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(recruiter_bp)
app.register_blueprint(candidate_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return 'Hello, World!'

@app.route('/protected')
@login_required
def protected():
    return f'Protected page - Logged in as {current_user.email}'

if __name__ == '__main__':
    print("Starting test server...")
    print("Templates folder:", app.template_folder)
    print("Static folder:", app.static_folder)
    print("Environment variables loaded:", bool(os.getenv('SECRET_KEY')))
    print(f"PostHog API Key loaded: {bool(POSTHOG_API_KEY)}")
    print(f"PostHog Host loaded: {POSTHOG_HOST}")
    app.run(debug=True) 