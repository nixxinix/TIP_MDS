"""
Custom authentication backend for email-based login.
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Authenticate using email address instead of username.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user with email and password.
        
        Args:
            username: Email address (we use username field for email)
            password: User password
        
        Returns:
            User object if authentication succeeds, None otherwise
        """
        try:
            # Try to fetch user by email
            user = User.objects.get(email=username.lower())
            
            # Check password
            if user.check_password(password):
                return user
            
        except User.DoesNotExist:
            # Run the default password hasher once to reduce timing
            # difference between existing and non-existing users
            User().set_password(password)
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        Get user by primary key.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None