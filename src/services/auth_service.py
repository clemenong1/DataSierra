"""
Authentication service for Firebase integration
"""

import streamlit as st
from typing import Dict, Any, Optional, Tuple

from .firebase_auth import FirebaseAuthService
from .firebase_config import FirebaseConfig
import os
import json
from pathlib import Path


class LocalAuthService:
    """Simple file-backed local auth for development only."""

    def __init__(self, data_path: Optional[str] = None):
        if not data_path:
            data_path = os.path.join(os.path.dirname(__file__), "local_auth.json")
        self.data_path = Path(data_path)
        self._ensure_store()

    def _ensure_store(self):
        if not self.data_path.exists():
            self._write({"users": {}})

    def _read(self):
        with self.data_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data):
        with self.data_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def sign_up(self, email: str, password: str):
        data = self._read()
        users = data.get("users", {})
        if email in users:
            return False, "An account with this email already exists"
        users[email] = {"password": password, "uid": f"local-{len(users)+1}"}
        data["users"] = users
        self._write(data)
        # set session
        st.session_state.user = {"uid": users[email]["uid"], "email": email}
        st.session_state.authenticated = True
        return True, "Local account created"

    def sign_in(self, email: str, password: str):
        data = self._read()
        users = data.get("users", {})
        if email not in users:
            return False, "No account found with this email"
        if users[email]["password"] != password:
            return False, "Incorrect password"
        st.session_state.user = {"uid": users[email]["uid"], "email": email}
        st.session_state.authenticated = True
        return True, "Signed in (local)"

    def sign_out(self) -> bool:
        if "user" in st.session_state:
            del st.session_state.user
        if "authenticated" in st.session_state:
            del st.session_state.authenticated
        return True

    def is_authenticated(self) -> bool:
        return st.session_state.get("authenticated", False)

    def get_current_user(self):
        if self.is_authenticated():
            return st.session_state.get("user")
        return None

    def get_user_email(self):
        user = self.get_current_user()
        return user.get("email") if user else None

    def get_user_uid(self):
        user = self.get_current_user()
        return user.get("uid") if user else None


class AuthService:
    """Service for handling Firebase authentication"""
    
    def __init__(self):
        """Initialize Firebase authentication service"""
        # Try to use FirebaseAuthService by default
        self.initialization_error = None
        self._backend_name = "firebase"
        try:
            firebase_backend = FirebaseAuthService()
        except Exception:
            firebase_backend = None

        use_local = False
        if firebase_backend is None or not firebase_backend.is_initialized():
            # capture firebase init error
            self.initialization_error = FirebaseConfig.get_initialization_error() or (
                "Firebase authentication not properly initialized"
            )
            # allow a local dev fallback if environment variable DEV_AUTH is set
            if os.getenv("DEV_AUTH", "0") in ("1", "true", "True"):
                use_local = True
        
        if use_local:
            self.firebase_auth = LocalAuthService()
            self._backend_name = "local"
            # override initialization_error to indicate fallback
            self.initialization_error = (self.initialization_error or "") + " (using local DEV_AUTH fallback)"
        else:
            # use firebase backend if available, otherwise create a default firebase auth instance
            self.firebase_auth = firebase_backend or FirebaseAuthService()
    
    
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
