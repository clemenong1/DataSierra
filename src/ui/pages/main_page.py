"""
Main page component
"""

import streamlit as st
from typing import Dict, Any

from ...models.file_models import ProcessedFile
from ...models.query_models import QueryResponse
from ...services.file_service import FileService
from ...services.ai_service import AIService
from ...services.data_service import DataService
from ...services.session_service import SessionService
from ...services.auth_service import AuthService
from ..components.file_upload import FileUploadComponent
from ..components.data_preview import DataPreviewComponent
from ..components.query_interface import QueryInterfaceComponent
from ..components.history import HistoryComponent
from ..components.auth_modal import AuthModalComponent
from ..components.lida_visualization import LidaVisualizationComponent


class MainPage:
    """Main page component that orchestrates all UI components"""
    
    def __init__(self):
        # Initialize services
        self.file_service = FileService()
        self.ai_service = AIService()
        self.data_service = DataService()
        self.session_service = SessionService()
        self.auth_service = AuthService()
        
        # Initialize UI components
        self.auth_modal_component = AuthModalComponent(self.auth_service)
        self.file_upload_component = FileUploadComponent(self.file_service, self.auth_modal_component)
        self.data_preview_component = DataPreviewComponent(self.data_service)
        self.query_interface_component = QueryInterfaceComponent(self.ai_service, self.data_service)
        self.history_component = HistoryComponent(self.session_service)
        self.lida_visualization_component = LidaVisualizationComponent()
    
    def render(self):
        """Render the main page"""
        # Initialize session state
        self._initialize_session_state()
        
        # Render header with authentication
        self._render_header()
        
        # Handle authentication modal
        self._handle_authentication()
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # File upload section
            processed_files = self.file_upload_component.render()
            
            # Store processed files in session state
            if processed_files:
                st.session_state.processed_files = processed_files
            
            # Data preview section
            if st.session_state.get('processed_files'):
                self.data_preview_component.render(st.session_state.processed_files)
            
            # Query interface section
            if st.session_state.get('processed_files'):
                query_result = self.query_interface_component.render(
                    st.session_state.processed_files,
                    st.session_state.get('session_id', 'default')
                )
                
                # Save successful queries to history
                if query_result and query_result['response'].success:
                    self.session_service.save_query_history(
                        query=query_result['original_query'],
                        response=query_result['response'].answer or '',
                        file_name=query_result['file_name']
                    )
            
            # LIDA Visualization section
            processed_files = st.session_state.get('processed_files', {})
            if processed_files:
                self.lida_visualization_component.render(processed_files)
        
        with col2:
            # Sidebar content
            self._render_sidebar()
        
        # Handle rerun queries
        self._handle_rerun_queries()
        
        # Render footer
        self._render_footer()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        if 'processed_files' not in st.session_state:
            st.session_state.processed_files = {}
        if 'session_id' not in st.session_state:
            st.session_state.session_id = "default"
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
    
    def _render_header(self):
        """Render the main header with authentication"""
        # Create header with authentication button
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("""
            <div class="main-header">
                <h1>DataSierra</h1>
                <p>Upload your data files and get insights from our AI assistant</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Render authentication button
            show_auth_modal = self.auth_modal_component.render_auth_button()
            if show_auth_modal:
                st.session_state.show_auth_modal = True
                st.rerun()
    
    def _handle_authentication(self):
        """Handle authentication modal display"""
        # Clear modal state if user is already authenticated
        if self.auth_service.is_authenticated() and st.session_state.get('show_auth_modal', False):
            st.session_state.show_auth_modal = False
            st.rerun()
        
        if st.session_state.get('show_auth_modal', False):
            success = self.auth_modal_component.render_auth_modal(show_modal=True)
            if success:
                st.session_state.show_auth_modal = False
                st.rerun()
    
    def _render_sidebar(self):
        """Render sidebar content"""
        # History component
        self.history_component.render_sidebar()
        
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
    
    def _handle_rerun_queries(self):
        """Handle rerun queries from history"""
        if 'rerun_query' in st.session_state:
            # Use a different approach to avoid session state conflicts
            st.session_state.pending_rerun_query = st.session_state.rerun_query
            st.session_state.pending_rerun_file = st.session_state.rerun_file
            del st.session_state.rerun_query
            del st.session_state.rerun_file
            st.rerun()
    
    def _render_footer(self):
        """Render the footer"""
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            <p>🤖 AI Data Analysis Assistant | Built with Streamlit</p>
            <p>Upload your data and get intelligent insights!</p>
        </div>
        """, unsafe_allow_html=True)
