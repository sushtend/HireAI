from flask import Blueprint, render_template, request, flash, redirect, url_for, json
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from utils.pdf_extractor import extract_text_from_pdf
from utils.gemini import parse_resume_with_gemini
from utils.supabase_client import save_candidate, get_candidate_by_email, supabase

candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')

# Temporary storage for candidate profiles (replace with database later)
candidate_profiles = {}

@candidate_bp.route('/', methods=['GET', 'POST'])
# @login_required  # Temporarily disabled
def index():
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
        
        # Store profile data temporarily
        profile = {
            'full_name': full_name,
            'email': email,
            'github': github,
            'linkedin': linkedin,
            'resume_filename': secure_filename(resume_file.filename),
            'raw_gemini_response': raw_response,
            'parsed_data': resume_data
        }
        candidate_profiles['default'] = profile
        
        # Show preview page
        return render_template('candidate/preview.html', 
                             profile=profile,
                             resume_data=resume_data)
    
    # GET request - show the form
    return render_template('candidate/dashboard.html')

@candidate_bp.route('/save_profile', methods=['POST'])
# @login_required  # Temporarily disabled
def save_profile():
    """Save the previewed profile to the database"""
    try:
        # Get form data
        candidate_data = {
            'name': request.form.get('full_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),  # Add phone number
            'github': request.form.get('github'),
            'linkedin': request.form.get('linkedin'),
            'skills': json.loads(request.form.get('skills', '[]')),
            'experience_years': int(request.form.get('experience_years', 0)),
            'education': request.form.get('education'),
            'current_location': request.form.get('current_location')
        }
        
        # Remove None values
        candidate_data = {k: v for k, v in candidate_data.items() if v is not None}
        
        # Save to Supabase
        candidate_id, is_update = save_candidate(candidate_data)
        if not candidate_id:
            flash('Error saving candidate data', 'error')
            return redirect(url_for('candidate.index'))
        
        # Show appropriate message based on whether it was an update or new entry
        if is_update:
            flash('Profile updated successfully!', 'success')
        else:
            flash('Profile saved successfully!', 'success')
            
        # Redirect to profile page with the candidate ID
        return redirect(url_for('candidate.profile', candidate_id=candidate_id))
        
    except Exception as e:
        print(f"Error saving profile: {str(e)}")  # Add logging
        flash(f'Error saving profile: {str(e)}', 'error')
        return redirect(url_for('candidate.index'))

@candidate_bp.route('/profile')
@candidate_bp.route('/profile/')
@candidate_bp.route('/profile/<candidate_id>')
@candidate_bp.route('/profile/<candidate_id>/')
def profile(candidate_id=None):
    """Display candidate profile"""
    try:
        # If no candidate_id provided, try to get the most recent one
        if not candidate_id and 'default' in candidate_profiles:
            # Get the email from the most recent profile
            email = candidate_profiles['default']['email']
            # Fetch the candidate from Supabase
            candidate = get_candidate_by_email(email)
            if candidate:
                candidate_id = candidate['id']
        
        if not candidate_id:
            flash('No candidate profile found', 'error')
            return redirect(url_for('candidate.index'))
            
        # Fetch candidate data from Supabase
        response = supabase.table('candidates').select('*').eq('id', candidate_id).execute()
        
        if not response.data or len(response.data) == 0:
            flash('Candidate profile not found', 'error')
            return redirect(url_for('candidate.index'))
            
        candidate = response.data[0]
        
        return render_template('candidate/profile.html', candidate=candidate)
        
    except Exception as e:
        print(f"Error fetching candidate profile: {str(e)}")
        flash('Error loading candidate profile', 'error')
        return redirect(url_for('candidate.index'))

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