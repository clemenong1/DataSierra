"""
Data preview component
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

from ...models.file_models import ProcessedFile
from ...services.data_service import DataService


class DataPreviewComponent:
    """Component for displaying data previews"""
    
    def __init__(self, data_service: DataService):
        self.data_service = data_service
    
    def render(self, processed_files: Dict[str, ProcessedFile]):
        """Render the data preview interface"""
        if not processed_files:
            return
        
        st.markdown("### 👁️ Data Preview")
        st.markdown("Preview your uploaded data")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_file = st.selectbox(
                "Select file to preview:",
                options=list(processed_files.keys()),
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
        
        if selected_file and selected_file in processed_files:
            self._display_data_preview(processed_files[selected_file], n_rows)
    
    def _display_data_preview(self, processed_file: ProcessedFile, n_rows: int):
        """Display data preview for a specific file"""
        preview_data = self.data_service.get_data_preview(processed_file, n_rows)
        
        if not preview_data.empty:
            st.dataframe(preview_data, width='stretch')
            
            # Download button for preview
            csv = preview_data.to_csv(index=False)
            st.download_button(
                label="📥 Download Preview",
                data=csv,
                file_name=f"{processed_file.file_info.name}_preview.csv",
                mime="text/csv"
            )
        else:
            st.error("No data available for preview")
    
    def render_file_statistics(self, processed_files: Dict[str, ProcessedFile]):
        """Render file statistics"""
        if not processed_files:
            return
        
        st.markdown("### 📊 File Statistics")
        
        # Create summary statistics
        total_rows = sum(pf.total_rows for pf in processed_files.values())
        total_columns = sum(pf.total_columns for pf in processed_files.values())
        avg_quality = sum(pf.data_quality.overall_score for pf in processed_files.values()) / len(processed_files)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Files", len(processed_files))
        with col2:
            st.metric("Total Rows", f"{total_rows:,}")
        with col3:
            st.metric("Total Columns", total_columns)
        with col4:
            st.metric("Avg Quality", f"{avg_quality:.1f}%")
        
        # Data quality overview
        st.markdown("#### Data Quality Overview")
        for file_name, processed_file in processed_files.items():
            quality_score = processed_file.data_quality.overall_score
            
            # Color coding based on quality score
            if quality_score >= 90:
                color = "🟢"
            elif quality_score >= 70:
                color = "🟡"
            else:
                color = "🔴"
            
            st.write(f"{color} **{file_name}**: {quality_score:.1f}% quality")
            
            # Show specific issues
            issues = []
            if processed_file.data_quality.completeness_score < 80:
                issues.append(f"Low completeness ({processed_file.data_quality.completeness_score:.1f}%)")
            if processed_file.data_quality.uniqueness_score < 50:
                issues.append(f"Low uniqueness ({processed_file.data_quality.uniqueness_score:.1f}%)")
            if processed_file.data_quality.total_nulls > 0:
                issues.append(f"{processed_file.data_quality.total_nulls} missing values")
            
            if issues:
                st.write(f"   Issues: {', '.join(issues)}")
