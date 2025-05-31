from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from utils.pdf_extractor import extract_text_from_pdf
from utils.gemini import parse_resume_with_gemini

candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')

# Temporary storage for candidate profiles (replace with database later)
candidate_profiles = {}

@candidate_bp.route('/', methods=['GET', 'POST'])
# @login_required  # Temporarily disabled
def index():
    # Check if user is logged in
    # if not current_user.is_authenticated:
    #     return redirect(url_for('auth.login', next=request.url))
        
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        github = request.form.get('github')
        linkedin = request.form.get('linkedin')
        
        # Validate required fields
        if not all([full_name, email, github, linkedin]):
            flash('All fields are required', 'error')
            return redirect(url_for('candidate.index'))
        
        # Handle resume upload
        if 'resume' not in request.files:
            flash('No resume file uploaded', 'error')
            return redirect(url_for('candidate.index'))
        
        resume_file = request.files['resume']
        if resume_file.filename == '':
            flash('No resume file selected', 'error')
            return redirect(url_for('candidate.index'))
        
        if not resume_file.filename.endswith('.pdf'):
            flash('Only PDF files are allowed', 'error')
            return redirect(url_for('candidate.index'))
        
        # Extract text from PDF
        resume_text = extract_text_from_pdf(resume_file)
        if not resume_text:
            flash('Error extracting text from PDF', 'error')
            return redirect(url_for('candidate.index'))
        
        # Parse resume using Gemini
        resume_data, raw_response = parse_resume_with_gemini(resume_text)
        if not resume_data:
            flash('Error parsing resume', 'error')
            return redirect(url_for('candidate.index'))
        
        # Store profile data (temporarily in memory)
        profile = {
            'full_name': full_name,
            'email': email,
            'github': github,
            'linkedin': linkedin,
            'resume_filename': secure_filename(resume_file.filename),
            'raw_gemini_response': raw_response,  # Store the raw Gemini response
            'parsed_data': resume_data   # Store the parsed data
        }
        # Use a default ID since we're not using login
        candidate_profiles['default'] = profile
        
        return render_template('candidate/preview.html', 
                             profile=profile,
                             resume_data=resume_data)
    
    # GET request - show the form
    return render_template('candidate/dashboard.html')

@candidate_bp.route('/profile')
def profile():
    return "Candidate profile page (placeholder)"

@candidate_bp.route('/resume/upload', methods=['GET', 'POST'])
@login_required
def upload_resume():
    """Upload and parse resume"""
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['resume']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            # TODO: Implement resume parsing and storage
            flash('Resume uploaded successfully')
            return redirect(url_for('candidate.profile'))
    
    return render_template('candidate/upload_resume.html')

@candidate_bp.route('/skills')
@login_required
def skills():
    """View and edit parsed skills"""
    return render_template('candidate/skills.html')

@candidate_bp.route('/connections')
@login_required
def connections():
    """Manage GitHub and LinkedIn connections"""
    return render_template('candidate/connections.html') 