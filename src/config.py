import os
from typing import Dict, Any
from pathlib import Path


class Config:
    MAX_FILE_SIZE = 200 * 1024 * 1024
    SUPPORTED_FORMATS = ['.xlsx', '.xls', '.csv']
    MAX_FILES_PER_UPLOAD = 10
    DEFAULT_PREVIEW_ROWS = 10
    MAX_PREVIEW_ROWS = 1000
    MIN_PREVIEW_ROWS = 1
    MAX_QUERY_LENGTH = 1000
    MAX_RESPONSE_LENGTH = 5000
    QUERY_HISTORY_LIMIT = 100
    THEME_COLORS = {
        'primary': '#2e6da4',
        'secondary': '#1f4e79',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#17a2b8'
    }
    AI_RESPONSE_DELAY = 1
    ENABLE_VISUALIZATIONS = True
    ENABLE_FEEDBACK = True
    DEFAULT_AI_MODEL = "gpt-4o"
    SESSION_TIMEOUT = 3600
    AUTO_SAVE_INTERVAL = 300
    
    @classmethod
    def _load_env_variables(cls):
        try:
            from dotenv import load_dotenv
            env_path = Path(__file__).parent.parent / ".env"
            if env_path.exists():
                load_dotenv(env_path)
        except ImportError:
            pass
        except Exception:
            pass
    
    @classmethod
    def get_openai_api_key(cls) -> str:
        cls._load_env_variables()
        return os.getenv("OPENAI_API_KEY")
    
    @classmethod
    def is_ai_available(cls) -> bool:
        return cls.get_openai_api_key() is not None
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
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