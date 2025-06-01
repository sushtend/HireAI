# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

def parse_resume_with_gemini(resume_text):
    """
    Parse resume text using Gemini API and return structured data.
    
    Args:
        resume_text (str): The text content of the resume
        
    Returns:
        tuple: (parsed_data, raw_response)
            - parsed_data: dict containing structured resume data
            - raw_response: str containing the raw response from Gemini
    """
    try:
        client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY"),
        )

        model = "gemini-1.5-flash-8b"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="""You are an expert resume parser. I will give you the raw text of a resume.  
Your task is to extract the following fields **accurately** and return ONLY a valid JSON object (no explanation, no formatting, no markdown, no code blocks, just the raw JSON):

- name
- email
- phone
- skills (as an array)
- experience_years (numeric only)
- education (highest qualification)
- current_location (if available)
- linkedin (if mentioned)
- github (if mentioned)

Example of expected response (just the JSON, nothing else):
{"name": "Jane Doe", "email": "jane.doe@gmail.com", "phone": "+1-234-567-8901", "skills": ["Python", "LangChain", "NLP", "RAG", "LLMs"], "experience_years": 5, "education": "M.Sc. in Computer Science", "current_location": "Berlin, Germany", "linkedin": "https://linkedin.com/in/janedoe", "github": "https://github.com/janedoe"}

Now here is the resume: """ + resume_text),
                ],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
        )

        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        # Get the raw response
        raw_response = response.text.strip()
        
        # Clean the response - remove any markdown or code block indicators
        json_str = raw_response
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()
            
        # Parse JSON
        parsed_data = json.loads(json_str)
        return parsed_data, raw_response
        
    except Exception as e:
        print(f"Error parsing resume: {str(e)}")
        return None, None

def test_parser():
    """
    Test function to verify the resume parser is working.
    """
    test_resume = """
    JOHN DOE
    Software Engineer
    john.doe@email.com | (555) 123-4567 | New York, NY
    
    SKILLS
    Python, JavaScript, React, Node.js, SQL, Git
    
    EXPERIENCE
    Senior Software Engineer
    Tech Corp
    2020 - Present
    • Led development of microservices architecture
    • Mentored junior developers
    
    Software Engineer
    Startup Inc
    2018 - 2020
    • Developed full-stack web applications
    
    EDUCATION
    M.Sc. in Computer Science
    University of Technology
    2018
    
    LINKS
    LinkedIn: https://linkedin.com/in/johndoe
    GitHub: https://github.com/johndoe
    """
    
    result, raw_response = parse_resume_with_gemini(test_resume)
    print("\nRaw Gemini Response:")
    print(raw_response)
    print("\nParsed Resume Data:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_parser()
