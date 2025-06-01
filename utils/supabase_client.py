import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Dict, Optional, Tuple

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def get_candidate_by_email(email: str) -> Optional[Dict]:
    """
    Check if a candidate with the given email exists.
    
    Args:
        email (str): Email address to check
        
    Returns:
        Optional[Dict]: Candidate data if found, None if not found
    """
    try:
        response = supabase.table('candidates').select('*').eq('email', email).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error checking candidate email: {str(e)}")
        return None

def save_candidate(parsed_data: Dict) -> Tuple[Optional[str], bool]:
    """
    Save or update candidate data in Supabase candidates table.
    
    Args:
        parsed_data (dict): Dictionary containing candidate data from Gemini parser
            and user input. Expected fields:
            - name (required)
            - email (required)
            - phone (optional)
            - skills (required, list)
            - experience_years (required, int)
            - education (required)
            - current_location (optional)
            - linkedin (optional)
            - github (optional)
    
    Returns:
        Tuple[Optional[str], bool]: (candidate_id, is_update)
            - candidate_id: The UUID of the inserted/updated record if successful, None if failed
            - is_update: True if this was an update, False if it was a new insertion
    """
    try:
        # Prepare data for insertion/update
        candidate_data = {
            'name': parsed_data.get('name'),
            'email': parsed_data.get('email'),
            'phone': parsed_data.get('phone'),
            'skills': parsed_data.get('skills', []),  # Default to empty list if not provided
            'experience_years': parsed_data.get('experience_years'),
            'education': parsed_data.get('education'),
            'current_location': parsed_data.get('current_location'),
            'linkedin': parsed_data.get('linkedin'),
            'github': parsed_data.get('github')
        }
        
        # Remove None values to avoid inserting nulls for optional fields
        candidate_data = {k: v for k, v in candidate_data.items() if v is not None}
        
        # Check if email exists
        existing_candidate = get_candidate_by_email(candidate_data['email'])
        
        if existing_candidate:
            # Update existing record
            response = supabase.table('candidates').update(candidate_data).eq('email', candidate_data['email']).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]['id'], True
        else:
            # Insert new record
            response = supabase.table('candidates').insert(candidate_data).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]['id'], False
                
        return None, False
        
    except Exception as e:
        print(f"Error saving candidate to Supabase: {str(e)}")
        return None, False

def test_save_candidate():
    """
    Test function to verify the save_candidate function is working.
    """
    test_data = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+1-234-567-8901',
        'skills': ['Python', 'Flask', 'SQL', 'Git'],
        'experience_years': 5,
        'education': 'M.Sc. in Computer Science',
        'current_location': 'New York, NY',
        'linkedin': 'https://linkedin.com/in/johndoe',
        'github': 'https://github.com/johndoe'
    }
    
    result, is_update = save_candidate(test_data)
    if result:
        print(f"Successfully {'updated' if is_update else 'saved'} candidate with ID: {result}")
    else:
        print("Failed to save candidate")

if __name__ == "__main__":
    test_save_candidate() 