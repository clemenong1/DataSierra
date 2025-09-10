"""
Configuration settings for DataSierra
"""

import os
from typing import Dict, Any


class Config:
    """Configuration class for DataSierra"""
    
    # File upload settings
    MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB in bytes
    SUPPORTED_FORMATS = ['.xlsx', '.xls', '.csv']
    MAX_FILES_PER_UPLOAD = 10
    
    # Data preview settings
    DEFAULT_PREVIEW_ROWS = 10
    MAX_PREVIEW_ROWS = 1000
    MIN_PREVIEW_ROWS = 1
    
    # Query settings
    MAX_QUERY_LENGTH = 1000
    MAX_RESPONSE_LENGTH = 5000
    QUERY_HISTORY_LIMIT = 100
    
    # UI settings
    THEME_COLORS = {
        'primary': '#2e6da4',
        'secondary': '#1f4e79',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#17a2b8'
    }
    
    # AI settings
    AI_RESPONSE_DELAY = 1  # seconds (for simulation)
    ENABLE_VISUALIZATIONS = True
    ENABLE_FEEDBACK = True
    DEFAULT_AI_MODEL = "gpt-4"
    
    # Session settings
    SESSION_TIMEOUT = 3600  # 1 hour in seconds
    AUTO_SAVE_INTERVAL = 300  # 5 minutes in seconds
    
    # API settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    @classmethod
    def get_openai_api_key(cls) -> str:
        """Get OpenAI API key from environment or Streamlit secrets"""
        # Try Streamlit secrets first
        try:
            import streamlit as st
            return st.secrets.get("OPENAI_API_KEY", cls.OPENAI_API_KEY)
        except:
            return cls.OPENAI_API_KEY
    
    @classmethod
    def is_ai_available(cls) -> bool:
        """Check if AI features are available"""
        return cls.get_openai_api_key() is not None
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return {
            "max_file_size": cls.MAX_FILE_SIZE,
            "supported_formats": cls.SUPPORTED_FORMATS,
            "max_files_per_upload": cls.MAX_FILES_PER_UPLOAD,
            "default_preview_rows": cls.DEFAULT_PREVIEW_ROWS,
            "max_query_length": cls.MAX_QUERY_LENGTH,
            "ai_available": cls.is_ai_available(),
            "default_ai_model": cls.DEFAULT_AI_MODEL,
            "theme_colors": cls.THEME_COLORS
        }
