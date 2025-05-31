# HireAI - AI-Powered Job Hiring Platform

HireAI is a lightweight AI-powered job hiring tool that helps recruiters find and connect with the right candidates using natural language queries.

## Features

- **For Recruiters:**
  - Natural language candidate search
  - AI-powered candidate matching
  - Personalized outreach generation
  - Candidate profile viewing

- **For Candidates:**
  - Resume upload and parsing
  - Skills extraction
  - GitHub and LinkedIn integration
  - Profile management

- **For Admins:**
  - Usage analytics via PostHog
  - User management
  - Platform monitoring

## Tech Stack

- **Backend & Frontend:** Flask
- **Database & Auth:** Supabase
- **Analytics:** PostHog
- **Hosting:** Hugging Face Spaces

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hireai.git
   cd hireai
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   Then fill in your environment variables in `.env`

5. Run the development server:
   ```bash
   python app.py
   ```

## Project Structure

```
hireai/
├── app.py              # Main application file
├── config.py           # Configuration settings
├── requirements.txt    # Project dependencies
├── .env               # Environment variables (create from .env.example)
├── routes/            # Route handlers
│   ├── admin.py
│   ├── auth.py
│   ├── candidate.py
│   └── recruiter.py
├── models/            # Data models
│   ├── user.py
│   └── candidate.py
├── templates/         # HTML templates
│   ├── admin/
│   ├── auth/
│   ├── candidate/
│   └── recruiter/
├── static/           # Static files (CSS, JS, images)
└── uploads/          # Uploaded files (resumes)
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.