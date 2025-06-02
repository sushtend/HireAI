from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import login_required
from models.candidate import Candidate
from utils.gemini import parse_resume_with_gemini
from utils.supabase_client import supabase
from utils.ranker import rank_candidates
from utils.background_quality import score_github_background_api, score_linkedin_background, score_public_presence
import json
import os # Import os to get GITHUB_TOKEN

recruiter_bp = Blueprint('recruiter', __name__, url_prefix='/recruiter')

def interpret_search_query(query: str) -> dict:
    """
    Use Gemini to interpret the recruiter's search query into structured filters.
    """
    prompt = f"""You are an expert recruiter AI. Interpret the following query and return a structured filter in this format. If a field is not mentioned, set it to null, empty string, or empty array as appropriate. Always include all fields:

{{
  "skills": ["Python", "Node.js"],
  "min_experience_years": 4,
  "location": "San Francisco",
  "job_title": "Software Engineer",
  "industry": "Tech"
}}

Query: {query}

Return ONLY the JSON object, no explanation or additional text. If a field is not mentioned, set it to null, empty string, or empty array as appropriate. Always include all fields."""

    try:
        parsed_data, raw_response = parse_resume_with_gemini(prompt)
        if parsed_data:
            return parsed_data
        return None
    except Exception as e:
        return None

def calculate_background_score(candidate_data: dict) -> int:
    """
    Calculate a combined background score for a candidate.
    This is a simple combination of individual scores for now.
    """
    github_url = candidate_data.get('github')
    linkedin_url = candidate_data.get('linkedin')
    name = candidate_data.get('name')
    candidate_id = candidate_data.get('id', 'Unknown ID') # Get candidate ID for logging
    
    github_score = 0
    linkedin_score = 0
    public_presence_score = 0

    # Calculate GitHub score
    if github_url:
        try:
            github_token = os.getenv("GITHUB_TOKEN")
            github_score = score_github_background_api(github_url, github_token)
        except Exception as e:
            print(f"Error calculating GitHub score for candidate {candidate_id} ({github_url}): {e}")

    # Calculate LinkedIn score
    if linkedin_url:
        try:
            linkedin_score = score_linkedin_background(linkedin_url)
        except Exception as e:
            print(f"Error calculating LinkedIn score for candidate {candidate_id} ({linkedin_url}): {e}")

    # Calculate Public Presence score
    if name:
         try:
            public_presence_score = score_public_presence(name, github_url, linkedin_url)
         except Exception as e:
             print(f"Error calculating Public Presence score for candidate {candidate_id} ({name}): {e}")

    # Simple weighted combination (adjust weights as needed)
    # Max possible combined score with current mock logic: ~100 (GH API) + 80 (LI placeholder) + 80 (PP placeholder) = ~260
    # We'll scale it to 100, but actual scores will likely be lower.
    
    combined_score = (github_score * 0.4) + (linkedin_score * 0.3) + (public_presence_score * 0.3)
    
    # Ensure score is between 0 and 100
    return min(max(int(combined_score), 0), 100)

@recruiter_bp.route('/', methods=['GET', 'POST'])
# @login_required  # Temporarily disabled for testing
def index():
    """
    Recruiter dashboard route that handles both GET and POST requests.
    GET: Shows the search interface
    POST: Processes search query and returns matching candidates with background scores
    """
    search_query = ""
    candidates = []
    structured_query = {}
    filters = {}
    
    if request.method == 'POST':
        # Get the search query from the form
        search_query = request.form.get('search_query', '').strip()
        
        if not search_query:
            flash('Please enter a search query', 'error')
            return render_template('recruiter/dashboard.html')
        
        # Step 1: Interpret the query using Gemini
        structured_query = interpret_search_query(search_query)
        
        if not structured_query:
            flash('Error interpreting search query', 'error')
            return render_template('recruiter/dashboard.html')
        
        # Prepare filters for UI
        filters = {
            'location': bool(structured_query.get('location')),
            'job_title': bool(structured_query.get('job_title')),
            'years_of_experience': bool(structured_query.get('min_experience_years')),
            'industry': bool(structured_query.get('industry')),
            'skills': bool(structured_query.get('skills')) and len(structured_query.get('skills', [])) > 0
        }
        
        # Step 2: Query Supabase for matching candidates
        try:
            # Build the query based on structured filters
            query = supabase.table('candidates').select('*')
            
            # Add filters if they exist in structured_query
            if structured_query.get('skills'):
                skills_json = json.dumps(structured_query['skills'])
                query = query.filter('skills', 'cs', skills_json)
            
            if structured_query.get('min_experience_years'):
                query = query.gte('experience_years', structured_query['min_experience_years'])
            
            if structured_query.get('location'):
                query = query.ilike('current_location', f"%{structured_query['location']}%")
            
            # Execute the query
            response = query.execute()
            candidates = response.data
            
            # Calculate background scores and add to candidates
            for candidate in candidates:
                candidate['background_score'] = calculate_background_score(candidate)
            
            # Step 3: Rank the candidates (can use background score here later)
            # For now, rank_candidates uses a dummy score, but we can update it.
            # ranked_candidates = rank_candidates(search_query, candidates)
            ranked_candidates = sorted(candidates, key=lambda x: x.get('background_score', 0), reverse=True)
            
            return render_template('recruiter/dashboard.html',
                                 search_query=search_query,
                                 candidates=ranked_candidates,
                                 structured_query=structured_query,
                                 filters=filters)
            
        except Exception as e:
            print(f"Error searching for candidates: {e}") # Keep error logging for backend issues
            flash('Error searching for candidates', 'error')
            return render_template('recruiter/dashboard.html')
    
    # GET request - show the search interface
    return render_template('recruiter/dashboard.html', search_query=search_query, candidates=candidates, structured_query=structured_query, filters=filters)

@recruiter_bp.route('/search')
@login_required
def search_page():
    """Search for candidates using natural language"""
    query = request.args.get('q', '')
    # TODO: Implement AI-powered search
    return render_template('recruiter/search.html')

@recruiter_bp.route('/candidates')
@login_required
def candidates():
    """View search results and candidate profiles"""
    return render_template('recruiter/candidates.html')

@recruiter_bp.route('/outreach/<candidate_id>', methods=['GET', 'POST'])
@login_required
def outreach(candidate_id):
    """Generate and send personalized outreach"""
    if request.method == 'POST':
        # TODO: Implement AI-generated outreach
        pass
    return render_template('recruiter/outreach.html')

@recruiter_bp.route('/api/search', methods=['POST'])
@login_required
def api_search():
    """API endpoint for candidate search"""
    data = request.get_json()
    # TODO: Implement search API
    return jsonify({'results': []}) 