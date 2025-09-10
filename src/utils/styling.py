"""
Custom styling utilities for DataSierra
"""

import streamlit as st


def apply_custom_styling():
    """Apply custom CSS styling to the Streamlit app"""
    st.markdown("""
    <style>
        /* Main app styling */
        .main-header {
            background: linear-gradient(90deg, #1f4e79 0%, #2e6da4 100%);
            padding: 2rem 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .main-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .main-header p {
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        /* File upload area styling */
        .upload-area {
            border: 2px dashed #2e6da4;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            background-color: #f8f9fa;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }
        
        .upload-area:hover {
            border-color: #1f4e79;
            background-color: #e3f2fd;
        }
        
        /* Card styling */
        .card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border: 1px solid #e0e0e0;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(90deg, #2e6da4 0%, #1f4e79 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Query interface styling */
        .query-box {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1.5rem;
            border: 1px solid #e0e0e0;
        }
        
        /* History item styling */
        .history-item {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #2e6da4;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            cursor: pointer;
            transition: all 0.3s ease;
            color: #333333 !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .history-item:hover {
            transform: translateX(5px);
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
            background-color: #f8f9fa;
        }
        
        .history-item strong {
            color: #1f4e79 !important;
            font-weight: 600;
        }
        
        /* Feedback buttons */
        .feedback-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .feedback-btn {
            background: #f8f9fa;
            border: 2px solid #e0e0e0;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .feedback-btn:hover {
            transform: scale(1.1);
        }
        
        .feedback-btn.thumbs-up:hover {
            background: #d4edda;
            border-color: #28a745;
        }
        
        .feedback-btn.thumbs-down:hover {
            background: #f8d7da;
            border-color: #dc3545;
        }
        
        /* Progress bar styling */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #2e6da4 0%, #1f4e79 100%);
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #f8f9fa;
        }
        
        /* Ensure sidebar text is visible */
        .sidebar .stTextInput > div > div > input,
        .sidebar .stSelectbox > div > div > div,
        .sidebar .stButton > button,
        .sidebar .stMarkdown,
        .sidebar .stInfo,
        .sidebar .stSuccess,
        .sidebar .stWarning,
        .sidebar .stError {
            color: #333333 !important;
        }
        
        /* Sidebar expander content */
        .sidebar .streamlit-expanderContent {
            color: #333333 !important;
        }
        
        /* Sidebar headings */
        .sidebar h1, .sidebar h2, .sidebar h3, .sidebar h4, .sidebar h5, .sidebar h6 {
            color: #1f4e79 !important;
        }
        
        /* Data table styling */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        /* Success/Error message styling */
        .stSuccess {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 1rem;
        }
        
        .stError {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            padding: 1rem;
        }
        
        .stInfo {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 8px;
            padding: 1rem;
        }
        
        /* Metric styling */
        .metric-container {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border: 1px solid #e0e0e0;
        }
        
        /* Code block styling */
        .stCode {
            background: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        
        .streamlit-expanderContent {
            background: white;
            border-radius: 0 0 8px 8px;
            border: 1px solid #e0e0e0;
            border-top: none;
        }
    </style>
    """, unsafe_allow_html=True)
