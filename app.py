from flask import Flask, render_template, request, redirect, url_for, flash
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

# Initialize PostHog
# posthog = Posthog(
#     project_api_key=os.getenv('POSTHOG_API_KEY'),
#     host=os.getenv('POSTHOG_HOST', 'https://app.posthog.com')
# )

# Initialize Supabase
# supabase: Client = create_client(
#     os.getenv('SUPABASE_URL'),
#     os.getenv('SUPABASE_KEY')
# )

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
    app.run(debug=True) 