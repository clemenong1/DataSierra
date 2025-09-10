"""
Firebase configuration service
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional
from pathlib import Path


class FirebaseConfig:
    """Clean Firebase configuration and initialization"""
    
    _app: Optional[firebase_admin.App] = None
    _db: Optional[firestore.Client] = None
    
    @classmethod
    def initialize(cls, service_account_path: Optional[str] = None) -> bool:
        """
        Initialize Firebase Admin SDK
        
        Args:
            service_account_path: Path to service account JSON file
            
        Returns:
            True if initialization successful
        """
        try:
            if cls._app is not None:
                return True
            
            # Try to initialize with environment variable first
            if cls._initialize_with_env():
                return True
            
            # Try to find service account file
            if not service_account_path:
                service_account_path = cls._find_service_account_file()
            
            if not service_account_path or not Path(service_account_path).exists():
                return False
            
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(service_account_path)
            cls._app = firebase_admin.initialize_app(cred)
            
            # Initialize Firestore
            cls._db = firestore.client()
            
            return True
            
        except Exception as e:
            return False
    
    @classmethod
    def _find_service_account_file(cls) -> Optional[str]:
        """Find service account file in common locations"""
        possible_paths = [
            "serviceAccountKey.json",
            "firebase-service-account.json",
            "config/serviceAccountKey.json",
            "src/config/serviceAccountKey.json",
            os.path.join(os.path.dirname(__file__), "serviceAccountKey.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "serviceAccountKey.json")
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        return None
    
    @classmethod
    def _initialize_with_env(cls) -> bool:
        """Try to initialize Firebase using environment variables"""
        try:
            # Check if GOOGLE_APPLICATION_CREDENTIALS is set
            if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                cls._app = firebase_admin.initialize_app()
                cls._db = firestore.client()
                return True
            
            # Check for individual Firebase config environment variables
            firebase_config = {
                "type": os.getenv("FIREBASE_TYPE", "service_account"),
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
                "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
            }
            
            # Check if all required fields are present
            required_fields = ["project_id", "private_key", "client_email"]
            if all(firebase_config.get(field) for field in required_fields):
                cred = credentials.Certificate(firebase_config)
                cls._app = firebase_admin.initialize_app(cred)
                cls._db = firestore.client()
                return True
            
            return False
            
        except Exception as e:
            return False
    
    @classmethod
    def get_firestore_client(cls) -> Optional[firestore.Client]:
        """Get Firestore client"""
        return cls._db
    
    @classmethod
    def get_app(cls) -> Optional[firebase_admin.App]:
        """Get Firebase app instance"""
        return cls._app
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Check if Firebase is initialized"""
        return cls._app is not None and cls._db is not None
