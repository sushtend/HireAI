from flask_login import UserMixin
from datetime import datetime

class User(UserMixin):
    def __init__(self, id, email, role, created_at=None):
        self.id = id
        self.email = email
        self.role = role
        self.created_at = created_at or datetime.utcnow()
        self.is_admin = role == 'admin'
        self.is_recruiter = role == 'recruiter'
        self.is_candidate = role == 'candidate'

    @staticmethod
    def get(user_id):
        """Retrieve user from Supabase"""
        # TODO: Implement Supabase user retrieval
        pass

    @staticmethod
    def create(email, password, role):
        """Create new user in Supabase"""
        # TODO: Implement Supabase user creation
        pass 