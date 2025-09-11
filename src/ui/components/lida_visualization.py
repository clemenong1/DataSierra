import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
import streamlit.components.v1 as components
from src.services.lida_visualization_service import LidaVisualizationService
from src.models.file_models import ProcessedFile

class LidaVisualizationComponent:
    def __init__(self):
        self.lida_service = LidaVisualizationService()
    
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
                        self._display_visualization(result)
                    else:
                        st.error(f"❌ {result['error']}")
                except Exception as e:
                    st.error(f"❌ Error generating visualization: {str(e)}")
        
        self._display_previous_visualizations()
    
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
    
    def _display_visualization(self, result: Dict[str, Any]):
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
                        processed_files = st.session_state.get('processed_files', {})
                        if not processed_files:
                            st.error("No data available for visualization.")
                            return
                        
                        # Convert the first file's data to DataFrame
                        file_name, processed_file = next(iter(processed_files.items()))
                        data = pd.DataFrame(processed_file.data_json)
                        
                        # Set up execution context with all necessary imports and data
                        exec_globals = {
                            "pd": pd, 
                            "px": None, 
                            "go": None,
                            "data": data,
                            "plt": None
                        }
                        exec_locals = {}
                        
                        # Import plotly modules
                        import plotly.express as px
                        import plotly.graph_objects as go
                        exec_globals["px"] = px
                        exec_globals["go"] = go
                        
                        # Execute the chart code
                        exec(chart['code'], exec_globals, exec_locals)
                        
                        # Try to find the figure in different possible variable names
                        fig = None
                        for var_name in ['fig', 'chart', 'figure']:
                            if var_name in exec_locals:
                                fig = exec_locals[var_name]
                                break
                        
                        if fig is not None:
                            st.plotly_chart(fig, use_container_width=True)
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
                    if st.button(f"🗑️ Remove {i+1}", key=f"remove_{i}"):
                        if "generated_visualizations" in st.session_state:
                            st.session_state.generated_visualizations = [
                                v for v in st.session_state.generated_visualizations 
                                if v != st.session_state.generated_visualizations[-1]
                            ]
                        st.rerun()
    
    def _display_previous_visualizations(self):
        if "generated_visualizations" in st.session_state and st.session_state.generated_visualizations:
            st.markdown("---")
            st.markdown("### 📚 Previous Visualizations")
            
            for i, viz in enumerate(reversed(st.session_state.generated_visualizations)):
                with st.expander(f"🕒 {viz['timestamp'].strftime('%H:%M:%S')} - {viz['prompt'][:50]}...", expanded=False):
                    st.write(f"**Prompt:** {viz['prompt']}")
                    st.write(f"**File:** {viz['file_used']}")
                    
                    charts = viz.get("charts", [])
                    for j, chart in enumerate(charts):
                        st.markdown(f"**Chart {j+1}:** {chart.get('title', 'Untitled')}")
                        if st.button(f"🔄 Regenerate Chart {j+1}", key=f"regen_{i}_{j}"):
                            st.session_state.regenerate_prompt = viz['prompt']
                            st.rerun()
