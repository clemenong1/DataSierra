import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional
from pathlib import Path


class FirebaseConfig:
    _app: Optional[firebase_admin.App] = None
    _db: Optional[firestore.Client] = None
    _last_error: Optional[str] = None
    
    @classmethod
    def initialize(cls, service_account_path: Optional[str] = None) -> bool:
        try:
            if cls._app is not None:
                return True
            
            if cls._initialize_with_env():
                return True
            
            if not service_account_path:
                service_account_path = cls._find_service_account_file()
            
            if not service_account_path or not Path(service_account_path).exists():
                cls._last_error = (
                    f"Service account file not found. Searched paths: {service_account_path}"
                )
                return False
            
            cred = credentials.Certificate(service_account_path)
            cls._app = firebase_admin.initialize_app(cred)
            cls._db = firestore.client()
            
            cls._last_error = None
            return True
            
        except Exception as e:
            cls._last_error = str(e)
            return False
    
    @classmethod
    def _find_service_account_file(cls) -> Optional[str]:
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
        try:
            if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                cls._app = firebase_admin.initialize_app()
                cls._db = firestore.client()
                return True
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
            
            required_fields = ["project_id", "private_key", "client_email"]
            if all(firebase_config.get(field) for field in required_fields):
                try:
                    cred = credentials.Certificate(firebase_config)
                    cls._app = firebase_admin.initialize_app(cred)
                    cls._db = firestore.client()
                    cls._last_error = None
                    return True
                except Exception as e:
                    cls._last_error = str(e)
                    return False

            cls._last_error = (
                "Firebase environment variables not fully configured (need FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY, FIREBASE_CLIENT_EMAIL)"
            )
            return False
            
        except Exception as e:
            return False
    
    @classmethod
    def get_firestore_client(cls) -> Optional[firestore.Client]:
        return cls._db
    
    @classmethod
    def get_app(cls) -> Optional[firebase_admin.App]:
        return cls._app
    
    @classmethod
    def is_initialized(cls) -> bool:
        return cls._app is not None and cls._db is not None

    @classmethod
    def get_initialization_error(cls) -> Optional[str]:
        """Return a human-readable initialization error if initialization failed."""
        return cls._last_error
