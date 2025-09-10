"""
Authentication service for Firebase integration
"""

import streamlit as st
import pyrebase
import os
from typing import Dict, Any, Optional, Tuple
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling Firebase authentication"""
    
    def __init__(self):
        """Initialize Firebase configuration"""
        # Load environment variables from .env file
        self._load_env_variables()
        
        self.firebase_config = self._get_firebase_config()
        self.firebase = self._initialize_firebase()
        self.auth = self.firebase.auth() if self.firebase else None
        self.initialization_error = None
        
        # Check if initialization was successful
        if not self.firebase or not self.auth:
            self.initialization_error = "Firebase authentication not properly initialized"
    
    def _load_env_variables(self):
        """Load environment variables from .env file"""
        try:
            from dotenv import load_dotenv
            # Load .env file from project root
            env_path = Path(__file__).parent.parent.parent / ".env"
            if env_path.exists():
                load_dotenv(env_path)
                logger.info("Environment variables loaded from .env file")
            else:
                logger.warning(".env file not found, using system environment variables")
        except ImportError:
            logger.warning("python-dotenv not installed, using system environment variables")
        except Exception as e:
            logger.error(f"Error loading .env file: {e}")
    
    def _get_firebase_config(self) -> Dict[str, str]:
        """Get Firebase configuration from environment variables"""
        try:
            config = {
                "apiKey": os.getenv("FIREBASE_API_KEY"),
                "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
                "projectId": os.getenv("FIREBASE_PROJECT_ID"),
                "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
                "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
                "appId": os.getenv("FIREBASE_APP_ID")
            }
            
            # Add databaseURL if available
            database_url = os.getenv("FIREBASE_DATABASE_URL")
            if database_url:
                config["databaseURL"] = database_url
            
            # Check if all required config values are present
            missing_keys = [key for key, value in config.items() if not value]
            if missing_keys:
                logger.error(f"Missing Firebase configuration: {missing_keys}")
                st.error(f"Firebase configuration incomplete. Missing: {', '.join(missing_keys)}")
                return {}
            
            logger.info("Firebase configuration loaded from environment variables")
            return config
        except Exception as e:
            logger.error(f"Error loading Firebase config: {e}")
            st.error("Firebase configuration not found. Please check your .env file.")
            return {}
    
    def _initialize_firebase(self) -> Optional[Any]:
        """Initialize Firebase connection"""
        try:
            if not self.firebase_config:
                return None
            return pyrebase.initialize_app(self.firebase_config)
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
            st.error("Failed to initialize Firebase connection.")
            return None
    
    def sign_up(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Sign up a new user
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.auth:
                return False, "Firebase authentication not initialized"
            
            # Create user account
            user = self.auth.create_user_with_email_and_password(email, password)
            
            # Store user info in session state
            st.session_state.user = {
                'uid': user['localId'],
                'email': user['email'],
                'idToken': user['idToken'],
                'refreshToken': user['refreshToken']
            }
            st.session_state.authenticated = True
            
            logger.info(f"User signed up successfully: {email}")
            return True, "Account created successfully!"
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Sign up error: {error_msg}")
            
            # Handle specific Firebase errors
            if "EMAIL_EXISTS" in error_msg:
                return False, "An account with this email already exists"
            elif "WEAK_PASSWORD" in error_msg:
                return False, "Password should be at least 6 characters"
            elif "INVALID_EMAIL" in error_msg:
                return False, "Please enter a valid email address"
            else:
                return False, f"Sign up failed: {error_msg}"
    
    def sign_in(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Sign in an existing user
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.auth:
                return False, "Firebase authentication not initialized"
            
            # Sign in user
            user = self.auth.sign_in_with_email_and_password(email, password)
            
            # Store user info in session state
            st.session_state.user = {
                'uid': user['localId'],
                'email': user['email'],
                'idToken': user['idToken'],
                'refreshToken': user['refreshToken']
            }
            st.session_state.authenticated = True
            
            logger.info(f"User signed in successfully: {email}")
            return True, "Signed in successfully!"
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Sign in error: {error_msg}")
            
            # Handle specific Firebase errors
            if "INVALID_PASSWORD" in error_msg:
                return False, "Invalid password"
            elif "EMAIL_NOT_FOUND" in error_msg:
                return False, "No account found with this email"
            elif "INVALID_EMAIL" in error_msg:
                return False, "Please enter a valid email address"
            elif "USER_DISABLED" in error_msg:
                return False, "This account has been disabled"
            else:
                return False, f"Sign in failed: {error_msg}"
    
    def sign_out(self) -> bool:
        """
        Sign out the current user
        
        Returns:
            True if successful
        """
        try:
            # Clear session state
            if 'user' in st.session_state:
                del st.session_state.user
            if 'authenticated' in st.session_state:
                del st.session_state.authenticated
            
            logger.info("User signed out successfully")
            return True
            
        except Exception as e:
            logger.error(f"Sign out error: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated
        
        Returns:
            True if user is authenticated
        """
        return st.session_state.get('authenticated', False)
    
    def is_initialized(self) -> bool:
        """
        Check if Firebase is properly initialized
        
        Returns:
            True if Firebase is initialized
        """
        return self.firebase is not None and self.auth is not None and self.initialization_error is None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current user information
        
        Returns:
            User dictionary or None if not authenticated
        """
        if self.is_authenticated():
            return st.session_state.get('user')
        return None
    
    def get_user_email(self) -> Optional[str]:
        """
        Get current user's email
        
        Returns:
            User email or None if not authenticated
        """
        user = self.get_current_user()
        return user.get('email') if user else None
    
    def refresh_token(self) -> bool:
        """
        Refresh the user's authentication token
        
        Returns:
            True if successful
        """
        try:
            if not self.is_authenticated() or not self.auth:
                return False
            
            user = self.get_current_user()
            if not user or 'refreshToken' not in user:
                return False
            
            # Refresh the token
            refreshed_user = self.auth.refresh(user['refreshToken'])
            
            # Update session state with new token
            st.session_state.user['idToken'] = refreshed_user['idToken']
            st.session_state.user['refreshToken'] = refreshed_user['refreshToken']
            
            logger.info("Token refreshed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            # If refresh fails, sign out the user
            self.sign_out()
            return False
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email to validate
            
        Returns:
            True if valid email format
        """
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
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        if len(password) > 128:
            return False, "Password must be less than 128 characters"
        
        return True, ""
