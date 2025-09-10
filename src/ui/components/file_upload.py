"""
File upload component
"""

import streamlit as st
from typing import Dict, List, Any
from datetime import datetime

from ...models.file_models import ProcessedFile
from ...services.file_service import FileService


class FileUploadComponent:
    """Component for handling file uploads"""
    
    def __init__(self, file_service: FileService):
        self.file_service = file_service
    
    def render(self) -> Dict[str, ProcessedFile]:
        """Render the file upload interface and return processed files"""
        st.markdown("### 📁 File Upload")
        st.markdown("Upload your Excel or CSV files for analysis")
        
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
