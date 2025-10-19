import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.express as px
import io
import base64
from src.services.lida_visualization_service import LidaVisualizationService
from src.services.firebase_storage_service import FirebaseStorageService
from src.services.visualization_service import VisualizationService
from src.models.file_models import ProcessedFile

class LidaVisualizationComponent:
    def __init__(self):
        self.lida_service = LidaVisualizationService()
        self.storage_service = FirebaseStorageService()
        self.viz_service = VisualizationService()
    
    def render(self, processed_files: Dict[str, ProcessedFile]):
        if not processed_files:
            st.warning("⚠️ Please upload and process a data file first to generate visualizations.")
            return
        
        st.markdown("---")
        st.markdown("### 🎨 Smart Data Visualization")
        st.markdown("Generate intelligent visualizations using natural language prompts.")
        
        with st.expander("📊 Available Data Files", expanded=False):
            for file_name, processed_file in processed_files.items():
                rows, cols = processed_file.file_info.shape
                st.write(f"**{file_name}**: {rows} rows, {cols} columns")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_prompt = st.text_input(
                "Describe the visualization you want:",
                placeholder="e.g., 'Show me a bar chart of survival rates by passenger class' or 'Create a scatter plot of age vs fare'",
                help="Describe what kind of chart or visualization you want to see from your data"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            generate_button = st.button("🎨 Generate Visualization", type="primary", use_container_width=True)
        
        if generate_button:
            if not user_prompt.strip():
                st.error("Please enter a description for your visualization.")
                return
            
            with st.spinner("🤖 Generating your visualization..."):
                try:
                    result = self._generate_visualization(processed_files, user_prompt)
                    if result["success"]:
                        self._display_visualization(result, user_prompt, processed_files)
                    else:
                        st.error(f"❌ {result['error']}")
                except Exception as e:
                    st.error(f"❌ Error generating visualization: {str(e)}")
    
    def _generate_visualization(self, processed_files: Dict[str, ProcessedFile], user_prompt: str) -> Dict[str, Any]:
        try:
            if not self.lida_service.is_available():
                return {
                    "success": False,
                    "error": "LIDA is not available. Please ensure you're running with Python 3.9+ and LIDA is installed."
                }
            
            dataframes = {}
            for file_name, processed_file in processed_files.items():
                # Convert the data_json back to a DataFrame
                import pandas as pd
                dataframes[file_name] = pd.DataFrame(processed_file.data_json)
            
            result = self.lida_service.generate_visualization_from_prompt(
                dataframes=dataframes,
                user_prompt=user_prompt
            )
            
            if result["success"]:
                visualization_data = {
                    "prompt": user_prompt,
                    "charts": result["charts"],
                    "timestamp": pd.Timestamp.now(),
                    "file_used": list(processed_files.keys())[0] if processed_files else "Unknown"
                }
                
                if "generated_visualizations" not in st.session_state:
                    st.session_state.generated_visualizations = []
                
                st.session_state.generated_visualizations.append(visualization_data)
                st.session_state.generated_visualizations = st.session_state.generated_visualizations[-10:]
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate visualization: {str(e)}"
            }
    
    def _display_visualization(self, result: Dict[str, Any], user_prompt: str, processed_files: Dict[str, Any]):
        st.success("✅ Visualization generated successfully!")
        
        charts = result.get("charts", [])
        if not charts:
            st.warning("No charts were generated. Try a different prompt.")
            return
        
        for i, chart in enumerate(charts):
            with st.expander(f"📊 Visualization {i+1}: {chart.get('title', 'Generated Chart')}", expanded=True):
                st.markdown(f"**Description:** {chart.get('description', 'No description available')}")
                
                try:
                    if chart.get('code'):
                        # Get the data from the first processed file
                        if not processed_files:
                            st.error("No data available for visualization.")
                            return
                        
                        # Convert the first file's data to DataFrame
                        file_name, processed_file = next(iter(processed_files.items()))
                        data = pd.DataFrame(processed_file.data_json)
                        
                        # Set up execution context with all necessary imports and data
                        exec_globals = {
                            "pd": pd, 
                            "px": px, 
                            "go": go,
                            "data": data,
                            "plt": None
                        }
                        exec_locals = {}
                        
                        # Execute the chart code
                        exec(chart['code'], exec_globals, exec_locals)
                        
                        # Try to find the figure in different possible variable names
                        fig = None
                        for var_name in ['fig', 'chart', 'figure']:
                            if var_name in exec_locals:
                                fig = exec_locals[var_name]
                                break
                        
                        if fig is not None:
                            # Display the chart
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Generate chart image and save to Firebase
                            self._save_chart_to_firebase(fig, chart, user_prompt, i)
                        else:
                            st.code(chart['code'], language='python')
                            st.info("Chart code generated but couldn't find the figure. Check the code above.")
                    else:
                        st.warning("No chart code available.")
                        
                except Exception as e:
                    st.error(f"Error executing chart code: {str(e)}")
                    st.code(chart.get('code', 'No code available'), language='python')
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📋 Copy Code {i+1}", key=f"copy_{i}"):
                        st.code(chart.get('code', ''), language='python')
                
                with col2:
                    if st.button(f"💾 Save to History {i+1}", key=f"save_{i}"):
                        # Re-save this specific chart to Firebase
                        self._save_chart_to_firebase(None, chart, user_prompt, i)
    
    def _save_chart_to_firebase(self, fig, chart: Dict[str, Any], user_prompt: str, chart_index: int):
        """Save a chart image to Firebase Storage and metadata to Firestore"""
        try:
            # Get current user
            user_id = st.session_state.get('user', {}).get('uid')
            if not user_id:
                st.warning("Please log in to save visualizations")
                return
            
            # Generate filename
            filename = f"{chart.get('title', 'chart').replace(' ', '_')}_{chart_index + 1}.png"
            
            if fig is not None:
                # Convert Plotly figure to PNG image
                img_bytes = fig.to_image(format="png", width=800, height=600)
                
                # Upload image to Firebase Storage
                upload_result = self.storage_service.upload_chart_image(
                    image_data=img_bytes,
                    filename=filename,
                    user_id=user_id,
                    query=user_prompt
                )
            else:
                # If no figure available, create a simple HTML representation
                html_content = f"""
                <html>
                <head><title>{chart.get('title', 'Generated Chart')}</title></head>
                <body>
                    <h2>{chart.get('title', 'Generated Chart')}</h2>
                    <p><strong>Description:</strong> {chart.get('description', 'No description available')}</p>
                    <p><strong>Prompt:</strong> {user_prompt}</p>
                    <h3>Code:</h3>
                    <pre><code>{chart.get('code', 'No code available')}</code></pre>
                    <p><em>Generated by DataSierra LIDA</em></p>
                </body>
                </html>
                """
                
                # Upload HTML to Firebase Storage
                upload_result = self.storage_service.upload_visualization(
                    file_data=html_content.encode('utf-8'),
                    filename=filename.replace('.png', '.html'),
                    user_id=user_id,
                    query=user_prompt,
                    content_type='text/html'
                )
            
            if upload_result:
                # Save to Firestore
                viz_id = self.viz_service.save_visualization(user_id, upload_result)
                if viz_id:
                    st.success(f"✅ Chart saved: {chart.get('title', 'Generated Chart')}")
                else:
                    st.error("❌ Failed to save chart to database")
            else:
                st.error("❌ Failed to upload chart to storage")
                
        except Exception as e:
            st.error(f"❌ Error saving chart: {str(e)}")
    
    # Previous visualizations are now handled by the history component
    # which pulls data from Firebase instead of local storage
