from turtle import color
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import os
from typing import Dict, List, Tuple, Optional
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stateful_button import button
from streamlit_extras.app_logo import add_logo

# Page configuration
st.set_page_config(
    page_title="AI Data Analysis Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
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
    }
    
    .history-item:hover {
        transform: translateX(5px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {} #file name : file
if 'query_history' not in st.session_state:
    st.session_state.query_history = [] #query idx : query, response, file name, timestamp, feedback
if 'current_query_id' not in st.session_state:
    st.session_state.current_query_id = 0 #query idx
if 'feedback_data' not in st.session_state:
    st.session_state.feedback_data = {} #query idx : feedback type, comment, timestamp

# Placeholder backend functions
def upload_and_process_files(files: List) -> Dict:
    """Placeholder function for file processing"""
    processed_files = {}
    for file in files:
        try:
            if file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            elif file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                continue
                
            processed_files[file.name] = {
                'data': df,
                'size': file.size,
                'type': file.type,
                'upload_time': datetime.now(),
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict()
            }
        except Exception as e:
            st.error(f"Error processing {file.name}: {str(e)}")
    return processed_files

def get_data_preview(file_name: str, sheet: str = None, n_rows: int = 10) -> pd.DataFrame:
    """Placeholder function for data preview"""
    if file_name in st.session_state.uploaded_files:
        df = st.session_state.uploaded_files[file_name]['data']
        return df.head(n_rows)
    return pd.DataFrame()

def query_ai(question: str, selected_file: str) -> str:
    """Placeholder function for AI query processing"""
    # Simulate AI processing time
    import time
    time.sleep(1)
    
    # Mock AI response based on question type
    if "summary" in question.lower() or "describe" in question.lower():
        return f"Based on the data in {selected_file}, here's a summary of the dataset..."
    elif "correlation" in question.lower():
        return "I found several interesting correlations in your data..."
    elif "trend" in question.lower():
        return "The trend analysis shows..."
    else:
        return f"Here's my analysis of your question about {selected_file}: [AI Response Placeholder]"

def save_query_history(query: str, response: str, file_name: str):
    """Save query to history"""
    query_id = st.session_state.current_query_id
    st.session_state.query_history.append({
        'id': query_id,
        'query': query,
        'response': response,
        'file_name': file_name,
        'timestamp': datetime.now(),
        'feedback': None
    })
    st.session_state.current_query_id += 1

def submit_feedback(query_id: int, feedback_type: str, comment: str = ""):
    """Submit feedback for a query"""
    st.session_state.feedback_data[query_id] = {
        'type': feedback_type,
        'comment': comment,
        'timestamp': datetime.now()
    }

# Main app header
st.markdown("""
<div class="main-header">
    <h1>DataSierra</h1>
    <p>Upload your data files and get insights from our AI assistant</p>
</div>
""", unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # File Upload Section
    colored_header(
        label="📁 File Upload",
        description="Upload your Excel or CSV files for analysis",
        color_name="blue-70"
    )
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=True,
        help="Upload Excel (.xlsx, .xls) or CSV files. Maximum file size: 200MB"
    )
    
    if uploaded_files:
        with st.spinner("Processing uploaded files..."):
            processed_files = upload_and_process_files(uploaded_files)
            st.session_state.uploaded_files.update(processed_files)
        
        st.success(f"Successfully uploaded {len(processed_files)} files!")
        
        # Display uploaded files info
        st.markdown("### 📋 Uploaded Files")
        for file_name, file_info in st.session_state.uploaded_files.items():
            with st.expander(f"📄 {file_name}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Rows", file_info['shape'][0])
                with col2:
                    st.metric("Columns", file_info['shape'][1])
                with col3:
                    st.metric("Size", f"{file_info['size'] / 1024:.1f} KB")
                
                st.write("**Columns:**", ", ".join(file_info['columns'][:5]) + 
                        ("..." if len(file_info['columns']) > 5 else ""))

    # Data Preview Section
    if st.session_state.uploaded_files:
        colored_header(
            label="👁️ Data Preview",
            description="Preview your uploaded data",
            color_name="green-70"
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_file = st.selectbox(
                "Select file to preview:",
                options=list(st.session_state.uploaded_files.keys()),
                key="preview_file_selector"
            )
        
        with col2:
            n_rows = st.number_input(
                "Number of rows to display:",
                min_value=1,
                max_value=100,
                value=10,
                key="preview_rows"
            )
        
        if selected_file:
            preview_data = get_data_preview(selected_file, n_rows=n_rows)
            if not preview_data.empty:
                st.dataframe(preview_data, use_container_width=True)
                
                # Download button for preview
                csv = preview_data.to_csv(index=False)
                st.download_button(
                    label="📥 Download Preview",
                    data=csv,
                    file_name=f"{selected_file}_preview.csv",
                    mime="text/csv"
                )

    # AI Query Interface
    colored_header(
        label="🤖 DataSierra AI",
        description="Ask questions about your data",
        color_name="blue-70"
    )
    
    # File selector for queries
    st.markdown("# Select file to query:")
    if st.session_state.uploaded_files:
        query_file = st.selectbox(
            "",
            options=list(st.session_state.uploaded_files.keys()),
            key="query_file_selector"
        )

        # Query input
        query = st.text_area(
            "Ask your question:",
            height=100,
            placeholder="Enter your question about the data...",
            value=st.session_state.get('example_query', ''),
            key="query_input"
        )
        
        # Clear example query after use
        if 'example_query' in st.session_state:
            del st.session_state.example_query
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            ask_button = st.button("Ask Sierra!", type="primary", use_container_width=True)
        with col2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)
        
        if clear_button:
            st.rerun()
        
        # Example questions
        st.markdown("**💡 Example Questions:**")
        example_cols = st.columns(3)
        examples = [
            "What are the main trends in this data?",
            "Show me correlations between variables",
            "Summarize the key insights",
            "What patterns do you see?",
            "Are there any outliers?",
            "Describe the data distribution"
        ]

        
        for i, example in enumerate(examples):
            with example_cols[i % 3]:
                if st.button(f"💭 {example[:30]}...", key=f"example_{i}"):
                    st.session_state.example_query = example
        
        if ask_button and query.strip():
            with st.spinner("🤖 AI is analyzing your data..."):
                response = query_ai(query, query_file)
                save_query_history(query, response, query_file)
                
                # Display response
                st.markdown("### 🤖 AI Response")
                st.markdown(f"**Query:** {query}")
                st.markdown(f"**Response:** {response}")
                
                # Feedback section
                st.markdown("### 💬 Feedback")
                feedback_col1, feedback_col2, feedback_col3 = st.columns([1, 1, 2])
                
                with feedback_col1:
                    if st.button("👍 Helpful", key="thumbs_up"):
                        submit_feedback(st.session_state.current_query_id - 1, "positive")
                        st.success("Thank you for your feedback!")
                
                with feedback_col2:
                    if st.button("👎 Not Helpful", key="thumbs_down"):
                        submit_feedback(st.session_state.current_query_id - 1, "negative")
                        st.success("Thank you for your feedback!")
                
                with feedback_col3:
                    feedback_comment = st.text_input("Additional comments:", key="feedback_comment")
                    if st.button("💬 Submit Comment", key="submit_comment"):
                        if feedback_comment:
                            submit_feedback(st.session_state.current_query_id - 1, "comment", feedback_comment)
                            st.success("Comment submitted!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    
    # Query History
    with st.expander("📚 Query History", expanded=True):
        if st.session_state.query_history:
            # Search functionality
            search_term = st.text_input("🔍 Search history:", key="history_search")
            
            # Filter history based on search
            filtered_history = st.session_state.query_history
            if search_term:
                filtered_history = [
                    item for item in st.session_state.query_history
                    if search_term.lower() in item['query'].lower() or 
                       search_term.lower() in item['response'].lower()
                ]
            
            # Display history items
            for item in reversed(filtered_history[-10:]):  # Show last 10 items
                with st.container():
                    st.markdown(f"""
                    <div class="history-item" onclick="rerunQuery({item['id']})">
                        <strong>📅 {item['timestamp'].strftime('%H:%M')}</strong><br>
                        <strong>File:</strong> {item['file_name']}<br>
                        <strong>Query:</strong> {item['query'][:50]}...
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Rerun button
                    if st.button(f"🔄 Rerun", key=f"rerun_{item['id']}"):
                        st.session_state.rerun_query = item['query']
                        st.session_state.rerun_file = item['file_name']
                        st.rerun()
            
            # Clear history button
            if st.button("🗑️ Clear History", type="secondary"):
                st.session_state.query_history = []
                st.session_state.feedback_data = {}
                st.rerun()
        else:
            st.info("No queries yet. Start by asking a question!")
    
    # App Settings
    with st.expander("⚙️ Settings"):
        st.markdown("**Display Options:**")
        show_metadata = st.checkbox("Show file metadata", value=True)
        auto_refresh = st.checkbox("Auto-refresh preview", value=False)
        
        st.markdown("**AI Settings:**")
        response_length = st.selectbox("Response length", ["Short", "Medium", "Long"])
        include_visualizations = st.checkbox("Include visualizations", value=True)
    
    # Help Section
    with st.expander("❓ Help"):
        st.markdown("""
        **How to use:**
        1. Upload your Excel or CSV files
        2. Preview the data to understand its structure
        3. Ask questions about your data
        4. Get AI-powered insights
        
        **Supported formats:**
        - Excel (.xlsx, .xls)
        - CSV (.csv)
        
        **Tips:**
        - Be specific in your questions
        - Use the example questions as starting points
        - Check the query history for previous insights
        """)

# Handle rerun queries
if 'rerun_query' in st.session_state:
    st.session_state.query_input = st.session_state.rerun_query
    st.session_state.query_file_selector = st.session_state.rerun_file
    del st.session_state.rerun_query
    del st.session_state.rerun_file
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>�� AI Data Analysis Assistant | Built with Streamlit</p>
    <p>Upload your data and get intelligent insights!</p>
</div>
""", unsafe_allow_html=True)
