"""
Authentication service for Firebase integration
"""

import streamlit as st
from typing import Dict, Any, Optional, Tuple

from .firebase_auth import FirebaseAuthService


class AuthService:
    """Service for handling Firebase authentication"""
    
    def __init__(self):
        """Initialize Firebase authentication service"""
        self.firebase_auth = FirebaseAuthService()
        self.initialization_error = None
        
        # Check if initialization was successful
        if not self.firebase_auth.is_initialized():
            self.initialization_error = "Firebase authentication not properly initialized"
    
    
    def sign_up(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Sign up a new user
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success, message)
        """
        return self.firebase_auth.sign_up(email, password)
    
    def sign_in(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Sign in an existing user
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success, message)
        """
        return self.firebase_auth.sign_in(email, password)
    
    def sign_out(self) -> bool:
        """
        Sign out the current user
        
        Returns:
            True if successful
        """
        return self.firebase_auth.sign_out()
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated
        
        Returns:
            True if user is authenticated
        """
        return self.firebase_auth.is_authenticated()
    
    def is_initialized(self) -> bool:
        """
        Check if Firebase is properly initialized
        
        Returns:
            True if Firebase is initialized
        """
        return self.firebase_auth.is_initialized()
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current user information
        
        Returns:
            User dictionary or None if not authenticated
        """
        return self.firebase_auth.get_current_user()
    
    def get_user_email(self) -> Optional[str]:
        """
        Get current user's email
        
        Returns:
            User email or None if not authenticated
        """
        return self.firebase_auth.get_user_email()
    
    def get_user_uid(self) -> Optional[str]:
        """
        Get current user's UID
        
        Returns:
            User UID or None if not authenticated
        """
        return self.firebase_auth.get_user_uid()
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email to validate
            
        Returns:
            True if valid email format
        """
        if not email:
            return False
        
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        if len(password) > 128:
            return False, "Password must be less than 128 characters"
        
        return True, ""
