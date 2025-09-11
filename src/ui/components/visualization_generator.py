import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ...services.lida_visualization_service import LidaVisualizationService
from ...models.file_models import ProcessedFile


class VisualizationGenerator:
    
    def __init__(self):
        self.lida_service = LidaVisualizationService()
    
    def render(self, processed_files: Dict[str, ProcessedFile], insights_context: str = "") -> bool:
        if not processed_files:
            st.warning("⚠️ No processed files available. Please upload and process a file first.")
            return False
        
        st.markdown("### 📊 Generate Visualizations")
        
        if not self.lida_service.is_available():
            status = self.lida_service.get_status()
            
            # Show a more user-friendly message
            st.info("🎨 **Smart Visualizations Available!** We'll generate relevant charts based on your data structure.")
            
            with st.expander("🔍 Technical Details", expanded=False):
                st.json(status)
                
                if not status['lida_available']:
                    st.info("💡 **Note:** LIDA requires Python 3.9+. Using enhanced fallback visualizations instead.")
                    if 'lida_import_error' in status:
                        st.code(status['lida_import_error'])
                elif not status['openai_api_key_available']:
                    st.error("❌ OpenAI API key is not configured. Check your .env file.")
                elif not status['lida_manager_initialized']:
                    st.error("❌ LIDA manager failed to initialize. Check your API key and model configuration.")
            
            # Don't return False - let the fallback visualizations work
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            button_text = "🎨 Generate Smart Visualizations" if self.lida_service.is_available() else "📊 Generate Data Visualizations"
            if st.button(button_text, type="primary", use_container_width=True):
                st.write("🔄 Button clicked! Generating visualizations...")
                self._generate_visualizations(processed_files, insights_context)
        
        with col2:
            if st.button("⚙️ Custom Chart", use_container_width=True):
                st.session_state.show_custom_chart = True
        
        if st.session_state.get('show_custom_chart', False):
            self._render_custom_chart_interface(processed_files)
        
        if st.session_state.get('generated_visualizations'):
            self._display_visualizations()
        
        return True
    
    def _generate_visualizations(self, processed_files: Dict[str, ProcessedFile], insights_context: str):
        with st.spinner("🎨 Generating visualizations..."):
            try:
                file_name = list(processed_files.keys())[0]
                processed_file = processed_files[file_name]
                
                data = pd.DataFrame(processed_file.data_json)
                
                # Debug info
                st.info(f"📊 Processing data with {len(data)} rows and {len(data.columns)} columns")
                
                visualizations = self.lida_service.generate_visualizations(
                    data=data,
                    insights_context=insights_context,
                    num_visualizations=5
                )
                
                if visualizations:
                    st.session_state.generated_visualizations = visualizations
                    st.success(f"✅ Generated {len(visualizations)} visualizations!")
                    st.rerun()
                else:
                    st.error("❌ Failed to generate visualizations. Please try again.")
                    
            except Exception as e:
                st.error(f"❌ Error generating visualizations: {str(e)}")
                st.write(f"Debug info: {str(e)}")
    
    def _render_custom_chart_interface(self, processed_files: Dict[str, ProcessedFile]):
        st.markdown("#### 🎯 Custom Chart Builder")
        
        file_name = list(processed_files.keys())[0]
        processed_file = processed_files[file_name]
        data = pd.DataFrame(processed_file.data_json)
        
        col1, col2 = st.columns(2)
        
        with col1:
            chart_type = st.selectbox(
                "Chart Type",
                ["scatter", "line", "bar", "histogram", "box"],
                key="custom_chart_type"
            )
            
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if chart_type in ["scatter", "line", "bar", "box"]:
                x_col = st.selectbox("X-axis", data.columns.tolist(), key="custom_x_col")
                y_col = st.selectbox("Y-axis", numeric_cols, key="custom_y_col")
                color_col = st.selectbox("Color by (optional)", [None] + categorical_cols, key="custom_color_col")
            else:
                x_col = st.selectbox("Column", data.columns.tolist(), key="custom_x_col")
                y_col = None
                color_col = st.selectbox("Color by (optional)", [None] + categorical_cols, key="custom_color_col")
        
        with col2:
            st.markdown("**Data Preview:**")
            st.dataframe(data.head(), use_container_width=True)
        
        if st.button("📈 Create Custom Chart", type="secondary"):
            with st.spinner("Creating custom chart..."):
                try:
                    visualization = self.lida_service.generate_custom_visualization(
                        data=data,
                        chart_type=chart_type,
                        x_col=x_col,
                        y_col=y_col,
                        color_col=color_col
                    )
                    
                    if visualization:
                        if 'generated_visualizations' not in st.session_state:
                            st.session_state.generated_visualizations = []
                        st.session_state.generated_visualizations.append(visualization)
                        st.success("✅ Custom chart created!")
                        st.session_state.show_custom_chart = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to create custom chart.")
                        
                except Exception as e:
                    st.error(f"❌ Error creating custom chart: {str(e)}")
        
        if st.button("❌ Cancel", type="secondary"):
            st.session_state.show_custom_chart = False
            st.rerun()
    
    def _display_visualizations(self):
        visualizations = st.session_state.get('generated_visualizations', [])
        
        if not visualizations:
            return
        
        st.markdown("#### 📊 Generated Visualizations")
        
        for i, viz in enumerate(visualizations):
            with st.expander(f"📈 {viz['title']}", expanded=True):
                st.markdown(f"**Description:** {viz['description']}")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    components.html(viz['html'], height=500, scrolling=True)
                
                with col2:
                    if st.button(f"💾 Export", key=f"export_{viz['id']}"):
                        self._export_visualization(viz)
                
                with col3:
                    if st.button(f"🗑️ Remove", key=f"remove_{viz['id']}"):
                        visualizations.pop(i)
                        st.session_state.generated_visualizations = visualizations
                        st.rerun()
        
        if st.button("🗑️ Clear All Visualizations", type="secondary"):
            st.session_state.generated_visualizations = []
            st.rerun()
    
    def _export_visualization(self, visualization: Dict[str, Any]):
        try:
            html_content = visualization['html']
            
            st.download_button(
                label="📥 Download as HTML",
                data=html_content,
                file_name=f"{visualization['title'].replace(' ', '_')}.html",
                mime="text/html",
                key=f"download_{visualization['id']}"
            )
        except Exception as e:
            st.error(f"❌ Error exporting visualization: {str(e)}")
    
    def get_data_summary(self, processed_files: Dict[str, ProcessedFile]) -> Dict[str, Any]:
        if not processed_files:
            return {}
        
        file_name = list(processed_files.keys())[0]
        processed_file = processed_files[file_name]
        data = pd.DataFrame(processed_file.data_json)
        
        return self.lida_service.get_data_summary(data)
