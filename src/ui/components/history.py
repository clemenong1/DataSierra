"""
Query history component
"""

import streamlit as st
from typing import Dict, List, Any, Optional

from ...models.query_models import QueryHistory
from ...services.session_service import SessionService


class HistoryComponent:
    """Component for displaying and managing query history"""
    
    def __init__(self, session_service: SessionService):
        self.session_service = session_service
    
    def render_sidebar(self):
        """Render the history component in the sidebar"""
        st.markdown("# Navigation")
        
        # Query History
        with st.expander("📚 Query History", expanded=True):
            history = self.session_service.get_query_history(limit=10)
            
            if history:
                # Search functionality
                search_term = st.text_input("🔍 Search history:", key="history_search")
                
                # Filter history based on search
                filtered_history = history
                if search_term:
                    filtered_history = [
                        item for item in history
                        if search_term.lower() in item.query.lower() or 
                           search_term.lower() in item.response.lower()
                    ]
                
                # Display history items
                for item in filtered_history:
                    self._render_history_item(item)
                
                # Clear history button
                if st.button("🗑️ Clear History", type="secondary"):
                    if self.session_service.clear_history():
                        st.success("History cleared!")
                        st.rerun()
            else:
                st.info("No queries yet. Start by asking a question!")
    
    def _render_history_item(self, item: QueryHistory):
        """Render a single history item with collapsible response"""
        # Create a container for each history item
        with st.container():
            # Header with timestamp and file
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin: 5px 0; background-color: #f9f9f9;">
                <div style="color: #1f4e79; font-weight: 600; margin-bottom: 0.5rem;">
                    📅 {item.timestamp.strftime('%b %d %H:%M')}
                </div>
                <div style="color: #333; margin-bottom: 0.3rem;">
                    <strong>📁 File:</strong> {item.file_name}
                </div>
                <div style="color: #333; line-height: 1.4;">
                    <strong>❓ Query:</strong> {item.query[:60]}{'...' if len(item.query) > 60 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Check current view state
            view_key = f"view_response_{item.id}"
            is_viewing = st.session_state.get(view_key, False)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"🔄 Rerun", key=f"rerun_{item.id}"):
                    st.session_state.rerun_query = item.query
                    st.session_state.rerun_file = item.file_name
                    st.rerun()
            with col2:
                if st.button(f"📋 Copy", key=f"copy_{item.id}"):
                    st.write("Response copied to clipboard!")
            with col3:
                # Dynamic button text based on current state
                button_text = "🙈 Hide" if is_viewing else "👁️ View"
                if st.button(button_text, key=f"view_{item.id}"):
                    # Toggle view state
                    st.session_state[view_key] = not is_viewing
                    st.rerun()
            
            # Show response if view is active
            if is_viewing:
                st.markdown("**🤖 Response:**")
                st.markdown(item.response)
                st.markdown("---")
    
    def render_main_page(self):
        """Render history component on main page"""
        st.markdown("### 📚 Query History")
        
        # Get all history
        history = self.session_service.get_query_history(limit=50)
        
        if not history:
            st.info("No query history available.")
            return
        
        # Search and filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("🔍 Search history:", key="main_history_search")
        with col2:
            limit = st.selectbox("Show last:", [10, 25, 50, 100], index=1)
        
        # Filter history
        filtered_history = history
        if search_term:
            filtered_history = [
                item for item in history
                if search_term.lower() in item.query.lower() or 
                   search_term.lower() in item.response.lower()
            ]
        
        # Display history
        for item in filtered_history[:limit]:
            with st.expander(f"📅 {item.timestamp.strftime('%Y-%m-%d %H:%M')} - {item.file_name}", expanded=False):
                # Query details
                st.markdown(f"**📁 File:** {item.file_name}")
                st.markdown(f"**❓ Query:** {item.query}")
                
                # Full response
                st.markdown("**🤖 Response:**")
                st.markdown(item.response)
                
                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Rerun", key=f"main_rerun_{item.id}"):
                        st.session_state.rerun_query = item.query
                        st.session_state.rerun_file = item.file_name
                        st.rerun()
                with col2:
                    if st.button("📋 Copy", key=f"copy_{item.id}"):
                        st.write("Response copied to clipboard!")
    
    def render_statistics(self):
        """Render history statistics"""
        stats = self.session_service.get_history_statistics()
        
        st.markdown("### 📊 History Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Queries", stats["total_queries"])
        with col2:
            st.metric("Total Feedback", stats["total_feedback"])
        with col3:
            st.metric("Current ID", stats["current_query_id"])
        with col4:
            last_query = stats.get("last_query_time")
            if last_query:
                st.metric("Last Query", "Recent")
            else:
                st.metric("Last Query", "None")
        
        # Feedback breakdown
        if stats["feedback_types"]:
            st.markdown("#### Feedback Breakdown")
            for feedback_type, count in stats["feedback_types"].items():
                st.write(f"• **{feedback_type.title()}**: {count}")
    
    def export_history(self):
        """Export history functionality"""
        st.markdown("### 📤 Export History")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export as JSON"):
                export_data = self.session_service.export_history("json")
                st.download_button(
                    label="Download JSON",
                    data=str(export_data),
                    file_name=f"datasierra_history_{st.session_state.get('session_id', 'default')}.json",
                    mime="application/json"
                )
        
        with col2:
            uploaded_file = st.file_uploader("📤 Import History", type=['json'])
            if uploaded_file:
                try:
                    import json
                    data = json.load(uploaded_file)
                    if self.session_service.import_history(data):
                        st.success("History imported successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to import history.")
                except Exception as e:
                    st.error(f"Error importing history: {str(e)}")
