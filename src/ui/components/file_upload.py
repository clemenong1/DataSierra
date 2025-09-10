"""
File upload component
"""

import streamlit as st
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...models.file_models import ProcessedFile
from ...services.file_service import FileService
from .auth_modal import AuthModalComponent


class FileUploadComponent:
    """Component for handling file uploads"""
    
    def __init__(self, file_service: FileService, auth_modal: Optional[AuthModalComponent] = None):
        self.file_service = file_service
        self.auth_modal = auth_modal
    
    def render(self) -> Dict[str, ProcessedFile]:
        """Render the file upload interface and return processed files"""
        st.markdown("### 📁 File Upload")
        st.markdown("Upload your Excel or CSV files for analysis")
        
        # Check if user is authenticated
        is_authenticated = self._check_authentication()
        
        if not is_authenticated:
            # Show authentication required message
            st.info("Please sign in to upload files")
            
            # Show a placeholder file uploader that triggers auth
            uploaded_files = st.file_uploader(
                "Choose files (Sign in required)",
                type=['xlsx', 'xls', 'csv'],
                accept_multiple_files=True,
                help="Sign in to upload files",
                disabled=True
            )
            
            # If user tries to upload without being authenticated, show auth modal
            if uploaded_files:
                if self.auth_modal:
                    self.auth_modal.render_protected_action_modal(
                        "File Upload",
                        "Uploading files requires authentication to ensure data security and provide personalized analysis."
                    )
            
            return {}
        
        # User is authenticated, show normal file upload
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['xlsx', 'xls', 'csv'],
            accept_multiple_files=True,
            help="Upload Excel (.xlsx, .xls) or CSV files. Maximum file size: 200MB"
        )
        
        processed_files = {}
        
        if uploaded_files:
            with st.spinner("Processing uploaded files..."):
                processed_files = self.file_service.process_files(uploaded_files)
            
            if processed_files:
                st.success(f"Successfully uploaded {len(processed_files)} files!")
                self._display_uploaded_files(processed_files)
            else:
                st.error("No valid files could be processed. Please check file formats and try again.")
        
        return processed_files
    
    def _check_authentication(self) -> bool:
        """Check if user is authenticated"""
        if self.auth_modal:
            # Check if Firebase is properly initialized first
            if not self.auth_modal.auth_service.is_initialized():
                return True  # Allow file upload if Firebase is not configured
            # Use the auth service from the modal component
            return self.auth_modal.auth_service.is_authenticated()
        return True  # Default to True if no auth modal is provided (backward compatibility)
    
    def _display_uploaded_files(self, processed_files: Dict[str, ProcessedFile]):
        """Display information about uploaded files"""
        st.markdown("### 📋 Uploaded Files")
        
        for file_name, processed_file in processed_files.items():
            with st.expander(f"📄 {file_name}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Rows", processed_file.total_rows)
                with col2:
                    st.metric("Columns", processed_file.total_columns)
                with col3:
                    st.metric("Size", f"{processed_file.file_info.size / 1024:.1f} KB")
                
                # Display columns
                columns_display = ", ".join(processed_file.file_info.columns[:5])
                if len(processed_file.file_info.columns) > 5:
                    columns_display += "..."
                st.write("**Columns:**", columns_display)
                
                # Display data quality
                quality_score = processed_file.data_quality.overall_score
                st.metric("Data Quality Score", f"{quality_score:.1f}%")
                
                if processed_file.data_quality.total_nulls > 0:
                    st.warning(f"⚠️ {processed_file.data_quality.total_nulls} missing values found")
                
                if processed_file.data_quality.duplicate_rows > 0:
                    st.info(f"ℹ️ {processed_file.data_quality.duplicate_rows} duplicate rows found")
