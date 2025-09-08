"""
Configuration settings for the AI Data Analysis Assistant
"""

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

# Session settings
SESSION_TIMEOUT = 3600  # 1 hour in seconds
AUTO_SAVE_INTERVAL = 300  # 5 minutes in seconds
