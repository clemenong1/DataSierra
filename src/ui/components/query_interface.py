"""
Query interface component
"""

import streamlit as st
from typing import Dict, Any, Optional

from ...models.file_models import ProcessedFile
from ...models.query_models import QueryRequest, QueryResponse
from ...services.ai_service import AIService
from ...services.data_service import DataService


class QueryInterfaceComponent:
    """Component for handling user queries and AI interactions"""
    
    def __init__(self, ai_service: AIService, data_service: DataService):
        self.ai_service = ai_service
        self.data_service = data_service
    
    def render(self, processed_files: Dict[str, ProcessedFile], session_id: str = "default") -> Optional[QueryResponse]:
        """Render the query interface and return response if query is submitted"""
        if not processed_files:
            st.info("Please upload files first to start asking questions.")
            return None
        
        st.markdown("### 🤖 DataSierra AI")
        st.markdown("Ask questions about your data")
        
        # File selector for queries
        st.markdown("#### Select file to query:")
        query_file = st.selectbox(
            "Choose a file to analyze",
            options=list(processed_files.keys()),
            key="query_file_selector",
            label_visibility="collapsed"
        )
        
        # Query input
        default_query = st.session_state.get('example_query', '') or st.session_state.get('pending_rerun_query', '')
        query = st.text_area(
            "Ask your question:",
            height=100,
            placeholder="Enter your question about the data...",
            value=default_query,
            key="query_input"
        )
        
        # Clear pending rerun after use
        if 'pending_rerun_query' in st.session_state:
            del st.session_state.pending_rerun_query
            del st.session_state.pending_rerun_file
        
        # Clear example query after use
        if 'example_query' in st.session_state:
            del st.session_state.example_query
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            ask_button = st.button("Ask Sierra!", type="primary", width='stretch')
        with col2:
            clear_button = st.button("🗑️ Clear", width='stretch')
        
        if clear_button:
            st.rerun()
        
        # Example questions
        self._render_example_questions()
        
        # Process query if submitted
        if ask_button and query.strip():
            return self._process_query(query, query_file, processed_files, session_id)
        
        return None
    
    def _render_example_questions(self):
        """Render example questions"""
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
                    st.rerun()
    
    def _process_query(self, query: str, query_file: str, processed_files: Dict[str, ProcessedFile], session_id: str) -> QueryResponse:
        """Process the user query"""
        with st.spinner("🤖 AI is analyzing your data..."):
            # Create query request
            request = QueryRequest(
                question=query,
                file_name=query_file,
                session_id=session_id
            )
            
            # Process with AI service
            response = self.ai_service.process_query(request, processed_files)
            
            if response.success:
                self._display_successful_response(response, query, query_file)
            else:
                self._display_error_response(response)
            
            return response
    
    def _display_successful_response(self, response: QueryResponse, query: str, query_file: str):
        """Display successful AI response"""
        st.markdown("### 🤖 DataSierra's Response")
        st.markdown(f"**Query:** {query}")
        st.markdown("**Response:**")
        st.markdown(response.answer)
        
        # Display additional insights
        self._display_data_quality_insights(response.data_quality_insights)
        self._display_statistical_insights(response.statistical_insights)
        self._display_business_insights(response.business_insights)
        self._display_pandasai_results(response.pandasai_results, response.pandasai_insights)
        self._display_visualizations(response.visualizations)
        self._display_code_suggestions(response.code_suggestions)
        self._display_metadata(response.metadata)
        self._display_feedback_section()
    
    def _display_error_response(self, response: QueryResponse):
        """Display error response"""
        st.error(f"❌ Error: {response.error}")
        if response.error_type:
            st.info(f"Error type: {response.error_type}")
    
    def _display_data_quality_insights(self, insights: Optional[Dict[str, Any]]):
        """Display data quality insights"""
        if not insights:
            return
        
        with st.expander("📊 Data Quality Insights"):
            st.metric("Overall Quality Score", f"{insights.get('overall_score', 0):.1f}%")
            
            if insights.get("issues"):
                st.write("**Issues Found:**")
                for issue in insights["issues"]:
                    st.write(f"• {issue}")
            
            if insights.get("recommendations"):
                st.write("**Recommendations:**")
                for rec in insights["recommendations"]:
                    st.write(f"• {rec}")
    
    def _display_statistical_insights(self, insights: Optional[Dict[str, Any]]):
        """Display statistical insights"""
        if not insights:
            return
        
        with st.expander("📈 Statistical Insights"):
            if insights.get("numeric_summaries"):
                st.write("**Numeric Column Summaries:**")
                for file_name, summaries in insights["numeric_summaries"].items():
                    st.write(f"**{file_name}:**")
                    for col_name, col_stats in summaries.items():
                        st.write(f"• {col_name}: Mean={col_stats.get('mean', 'N/A')}, Range={col_stats.get('range', 'N/A')}")
    
    def _display_business_insights(self, insights: Optional[list]):
        """Display business insights"""
        if not insights:
            return
        
        with st.expander("💼 Business Insights"):
            for insight in insights:
                st.write(f"• {insight}")
    
    def _display_pandasai_results(self, results: Optional[Dict[str, Any]], insights: Optional[list]):
        """Display PandasAI results"""
        if results and isinstance(results, dict):
            with st.expander("🤖 PandasAI Direct Analysis"):
                st.write("**PandasAI provided direct data analysis:**")
                for file_name, result in results.items():
                    if isinstance(result, dict) and result.get("success") and result.get("answer"):
                        st.write(f"**{file_name}:**")
                        st.write(result["answer"])
                    elif isinstance(result, dict) and not result.get("success"):
                        st.write(f"**{file_name}:** Analysis failed - {result.get('error', 'Unknown error')}")
                    else:
                        st.write(f"**{file_name}:** No analysis available")
        elif results and isinstance(results, dict) and results.get("success"):
            # Handle single result case
            with st.expander("🤖 PandasAI Direct Analysis"):
                st.write("**PandasAI provided direct data analysis:**")
                if results.get("answer"):
                    st.write(results["answer"])
                else:
                    st.write("Analysis completed but no response available")
        
        if insights:
            with st.expander("💡 PandasAI Insights"):
                for insight in insights:
                    st.write(f"• {insight}")
    
    def _display_visualizations(self, visualizations: Optional[list]):
        """Display visualization suggestions"""
        if not visualizations:
            return
        
        with st.expander("📊 Visualization Suggestions"):
            for viz in visualizations:
                st.write(f"**{viz['title']}:**")
                st.write(viz['description'])
                if viz.get('code'):
                    st.code(viz['code'], language='python')
    
    def _display_code_suggestions(self, suggestions: Optional[list]):
        """Display code suggestions"""
        if not suggestions:
            return
        
        with st.expander("💻 Code Suggestions"):
            for suggestion in suggestions:
                st.write(f"**{suggestion['title']}:**")
                st.write(suggestion['description'])
                st.code(suggestion['code'], language='python')
    
    def _display_metadata(self, metadata: Optional[Dict[str, Any]]):
        """Display analysis metadata"""
        if not metadata:
            return
        
        with st.expander("ℹ️ Analysis Metadata"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tokens Used", metadata.get("tokens_used", "N/A"))
            with col2:
                st.metric("Model", metadata.get("model", "N/A"))
            with col3:
                st.metric("Files Analyzed", metadata.get("datasets_analyzed", 0))
            
            # Show PandasAI usage
            if metadata.get("pandasai_used"):
                st.success("🤖 PandasAI was used for enhanced analysis!")
            else:
                st.info("💡 Try asking data-specific questions to enable PandasAI analysis")
    
    def _display_feedback_section(self):
        """Display feedback section"""
        st.markdown("### 💬 Feedback")
        feedback_col1, feedback_col2, feedback_col3 = st.columns([1, 1, 2])
        
        with feedback_col1:
            if st.button("👍 Helpful", key="thumbs_up"):
                st.success("Thank you for your feedback!")
        
        with feedback_col2:
            if st.button("👎 Not Helpful", key="thumbs_down"):
                st.success("Thank you for your feedback!")
        
        with feedback_col3:
            feedback_comment = st.text_input("Additional comments:", key="feedback_comment")
            if st.button("💬 Submit Comment", key="submit_comment"):
                if feedback_comment:
                    st.success("Comment submitted!")
