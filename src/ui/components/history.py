"""
Query history component
"""

import streamlit as st
from typing import Dict, List, Any, Optional

from ...models.query_models import QueryHistory
from ...services.session_service import SessionService
from ...services.visualization_service import VisualizationService
from ...services.firestore_query_service import FirestoreQueryService


class HistoryComponent:
    """Component for displaying and managing query history"""
    
    def __init__(self, session_service: SessionService):
        self.session_service = session_service
        self.viz_service = VisualizationService()
        self.firestore_query_service = FirestoreQueryService()
    
    def render_sidebar(self):
        """Render the history component in the sidebar"""
        st.markdown("# Navigation")
        
        # Query History
        with st.expander("📚 Query History", expanded=True):
            # Get current user
            user_id = st.session_state.get('user', {}).get('uid')
            if not user_id:
                st.info("Please log in to view query history")
            else:
                # Get queries from Firestore
                queries = self.firestore_query_service.get_user_queries(user_id, limit=10)
                
                if queries:
                    # Search functionality
                    search_term = st.text_input("🔍 Search history:", key="history_search")
                    
                    # Filter queries based on search
                    filtered_queries = queries
                    if search_term:
                        filtered_queries = [
                            query for query in queries
                            if search_term.lower() in query.get('query', '').lower() or 
                               search_term.lower() in query.get('response', '').lower()
                        ]
                    
                    # Display queries
                    for query in filtered_queries:
                        self._render_firestore_query_item(query)
                else:
                    st.info("No queries yet. Start by asking a question!")
        
        # Visualization History
        with st.expander("📊 Visualizations History", expanded=True):
            self._render_visualization_history()
    
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
            
            # Action buttons (matching visualization history format)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                # Dynamic button text based on current state
                button_text = "🙈 Hide" if is_viewing else "👁️ View"
                if st.button(button_text, key=f"view_{item.id}"):
                    # Toggle view state
                    st.session_state[view_key] = not is_viewing
                    st.rerun()
            
            with col2:
                if st.button("👍", key=f"thumbs_up_{item.id}"):
                    # TODO: Implement query helpfulness feedback
                    st.success("Marked as helpful!")
                    st.rerun()
            
            with col3:
                if st.button("👎", key=f"thumbs_down_{item.id}"):
                    # TODO: Implement query helpfulness feedback
                    st.success("Marked as not helpful!")
                    st.rerun()
            
            with col4:
                if st.button("🗑️", key=f"delete_{item.id}"):
                    # Delete query from database
                    user_id = st.session_state.get('user', {}).get('uid')
                    if user_id and self.firestore_query_service.delete_query(user_id, str(item.id)):
                        st.success("Query deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete query")
            
            # Show response if view is active
            if is_viewing:
                st.markdown("**🤖 Response:**")
                # Escape HTML characters in the response to prevent rendering issues
                escaped_response = self._escape_html(item.response)
                st.markdown(escaped_response)
                st.markdown("---")
    
    def render_main_page(self):
        """Render history component on main page"""
        st.markdown("### 📚 Query History")
        
        # Get current user
        user_id = st.session_state.get('user', {}).get('uid')
        if not user_id:
            st.info("Please log in to view query history")
            return
        
        # Get queries from Firestore
        queries = self.firestore_query_service.get_user_queries(user_id, limit=50)
        
        if not queries:
            st.info("No query history available.")
            return
        
        # Search and filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("🔍 Search history:", key="main_history_search")
        with col2:
            limit = st.selectbox("Show last:", [10, 25, 50, 100], index=1)
        
        # Filter queries based on search
        filtered_queries = queries
        if search_term:
            filtered_queries = [
                query for query in queries
                if search_term.lower() in query.get('query', '').lower() or 
                   search_term.lower() in query.get('response', '').lower()
            ]
        
        # Display queries
        for query in filtered_queries[:limit]:
            # Format timestamp
            created_at = query.get('created_at', 'Unknown date')
            if hasattr(created_at, 'strftime'):
                formatted_date = created_at.strftime('%Y-%m-%d %H:%M')
            elif isinstance(created_at, str):
                formatted_date = created_at[:16] if len(created_at) > 16 else created_at
            else:
                formatted_date = 'Unknown date'
            
            with st.expander(f"📅 {formatted_date} - {query.get('file_name', 'Unknown file')}", expanded=False):
                # Query details
                st.markdown(f"**📁 File:** {query.get('file_name', 'Unknown file')}")
                st.markdown(f"**❓ Query:** {query.get('query', 'No query')}")
                
                # Full response
                st.markdown("**🤖 Response:**")
                escaped_response = self._escape_html(query.get('response', ''))
                st.markdown(escaped_response)
                
                # Action buttons (matching visualization history format)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("👁️ View", key=f"main_view_{query.get('id', 'unknown')}"):
                        st.info("Use the sidebar to view full response")
                with col2:
                    if st.button("👍", key=f"main_thumbs_up_{query.get('id', 'unknown')}"):
                        # Update query helpfulness in database
                        user_id = st.session_state.get('user', {}).get('uid')
                        if user_id and self.firestore_query_service.update_query_helpfulness(user_id, query.get('id'), True):
                            st.success("Marked as helpful!")
                            st.rerun()
                        else:
                            st.error("Failed to update feedback")
                with col3:
                    if st.button("👎", key=f"main_thumbs_down_{query.get('id', 'unknown')}"):
                        # Update query helpfulness in database
                        user_id = st.session_state.get('user', {}).get('uid')
                        if user_id and self.firestore_query_service.update_query_helpfulness(user_id, query.get('id'), False):
                            st.success("Marked as not helpful!")
                            st.rerun()
                        else:
                            st.error("Failed to update feedback")
                with col4:
                    if st.button("🗑️", key=f"main_delete_{query.get('id', 'unknown')}"):
                        # Delete query from database
                        user_id = st.session_state.get('user', {}).get('uid')
                        if user_id and self.firestore_query_service.delete_query(user_id, query.get('id')):
                            st.success("Query deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete query")
    
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
    
    def _render_visualization_history(self):
        """Render visualization history from Firebase"""
        # Get current user
        user_id = st.session_state.get('user', {}).get('uid')
        if not user_id:
            st.info("Please log in to view visualization history")
            return
        
        # Search functionality
        search_term = st.text_input("🔍 Search visualizations:", key="viz_search")
        
        # Get visualizations from Firebase
        visualizations = self.viz_service.get_user_visualizations(user_id, limit=20)
        
        if not visualizations:
            st.info("No visualizations yet. Generate some charts to see them here!")
            return
        
        # Filter visualizations based on search
        filtered_viz = visualizations
        if search_term:
            filtered_viz = [
                viz for viz in visualizations
                if search_term.lower() in viz.get('query', '').lower()
            ]
        
        # Display visualizations
        for viz in filtered_viz:
            self._render_visualization_item(viz)
    
    def _render_visualization_item(self, viz: Dict[str, Any]):
        """Render a single visualization item"""
        with st.container():
            # Header with timestamp and query
            # Format the created_at timestamp properly
            created_at = viz.get('created_at', 'Unknown date')
            if hasattr(created_at, 'strftime'):
                # It's a datetime object, format it
                formatted_date = created_at.strftime('%b %d %H:%M')
            elif isinstance(created_at, str):
                # It's already a string, use it as is
                formatted_date = created_at[:10] + ' ' + created_at[11:16] if len(created_at) > 16 else created_at
            else:
                # Fallback
                formatted_date = 'Unknown date'
            
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin: 5px 0; background-color: #f9f9f9;">
                <div style="color: #1f4e79; font-weight: 600; margin-bottom: 0.5rem;">
                    📅 {formatted_date}
                </div>
                <div style="color: #333; line-height: 1.4;">
                    <strong>❓ Query:</strong> {viz.get('query', 'No query')[:60]}{'...' if len(viz.get('query', '')) > 60 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Check current view state
            view_key = f"view_viz_{viz.get('id', 'unknown')}"
            is_viewing = st.session_state.get(view_key, False)
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                button_text = "🙈 Hide" if is_viewing else "👁️ View"
                if st.button(button_text, key=f"view_viz_{viz.get('id', 'unknown')}"):
                    st.session_state[view_key] = not is_viewing
                    st.rerun()
            
            with col2:
                if st.button("👍", key=f"thumbs_up_{viz.get('id', 'unknown')}"):
                    self.viz_service.update_visualization_helpfulness(
                        st.session_state.get('user', {}).get('uid'), 
                        viz.get('id'), 
                        True
                    )
                    st.success("Marked as helpful!")
                    st.rerun()
            
            with col3:
                if st.button("👎", key=f"thumbs_down_{viz.get('id', 'unknown')}"):
                    self.viz_service.update_visualization_helpfulness(
                        st.session_state.get('user', {}).get('uid'), 
                        viz.get('id'), 
                        False
                    )
                    st.success("Marked as not helpful!")
                    st.rerun()
            
            with col4:
                if st.button("🗑️", key=f"delete_{viz.get('id', 'unknown')}"):
                    if self.viz_service.delete_visualization(
                        st.session_state.get('user', {}).get('uid'), 
                        viz.get('id')
                    ):
                        st.success("Visualization deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete visualization")
            
            # Show visualization if view is active
            if is_viewing:
                st.markdown("**📊 Visualization:**")
                
                # Check if it's an image URL or HTML content
                file_url = viz.get('file_url', '')
                if file_url:
                    if file_url.endswith('.png') or file_url.endswith('.jpg') or file_url.endswith('.jpeg'):
                        # Display image
                        st.image(file_url, caption=viz.get('query', 'Generated visualization'))
                    else:
                        # Display HTML content
                        import streamlit.components.v1 as components
                        try:
                            import requests
                            response = requests.get(file_url)
                            if response.status_code == 200:
                                components.html(response.text, height=500, scrolling=True)
                            else:
                                st.error("Could not load visualization")
                        except Exception as e:
                            st.error(f"Error loading visualization: {str(e)}")
                else:
                    st.warning("No visualization file found")
                
                st.markdown("---")
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML characters in text to prevent rendering issues"""
        if not text:
            return ""
        
        # Replace common HTML characters with their escaped equivalents
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#x27;",
            ">": "&gt;",
            "<": "&lt;",
        }
        
        escaped_text = text
        for char, escaped in html_escape_table.items():
            escaped_text = escaped_text.replace(char, escaped)
        
        return escaped_text
    
    def _render_firestore_query_item(self, query: Dict[str, Any]):
        """Render a single Firestore query item (works exactly like visualizations)"""
        with st.container():
            # Header with timestamp and query
            # Format the created_at timestamp properly
            created_at = query.get('created_at', 'Unknown date')
            if hasattr(created_at, 'strftime'):
                # It's a datetime object, format it
                formatted_date = created_at.strftime('%b %d %H:%M')
            elif isinstance(created_at, str):
                # It's already a string, use it as is
                formatted_date = created_at[:10] + ' ' + created_at[11:16] if len(created_at) > 16 else created_at
            else:
                # Fallback
                formatted_date = 'Unknown date'
            
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin: 5px 0; background-color: #f9f9f9;">
                <div style="color: #1f4e79; font-weight: 600; margin-bottom: 0.5rem;">
                    📅 {formatted_date}
                </div>
                <div style="color: #333; margin-bottom: 0.3rem;">
                    <strong>📁 File:</strong> {query.get('file_name', 'Unknown file')}
                </div>
                <div style="color: #333; line-height: 1.4;">
                    <strong>❓ Query:</strong> {query.get('query', 'No query')[:60]}{'...' if len(query.get('query', '')) > 60 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Check current view state
            view_key = f"view_response_{query.get('id', 'unknown')}"
            is_viewing = st.session_state.get(view_key, False)
            
            # Action buttons (matching visualization history format)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                # Dynamic button text based on current state
                button_text = "🙈 Hide" if is_viewing else "👁️ View"
                if st.button(button_text, key=f"view_{query.get('id', 'unknown')}"):
                    # Toggle view state
                    st.session_state[view_key] = not is_viewing
                    st.rerun()
            
            with col2:
                if st.button("👍", key=f"thumbs_up_{query.get('id', 'unknown')}"):
                    # Update query helpfulness in database
                    user_id = st.session_state.get('user', {}).get('uid')
                    if user_id and self.firestore_query_service.update_query_helpfulness(user_id, query.get('id'), True):
                        st.success("Marked as helpful!")
                        st.rerun()
                    else:
                        st.error("Failed to update feedback")
            
            with col3:
                if st.button("👎", key=f"thumbs_down_{query.get('id', 'unknown')}"):
                    # Update query helpfulness in database
                    user_id = st.session_state.get('user', {}).get('uid')
                    if user_id and self.firestore_query_service.update_query_helpfulness(user_id, query.get('id'), False):
                        st.success("Marked as not helpful!")
                        st.rerun()
                    else:
                        st.error("Failed to update feedback")
            
            with col4:
                if st.button("🗑️", key=f"delete_{query.get('id', 'unknown')}"):
                    # Delete query from database
                    user_id = st.session_state.get('user', {}).get('uid')
                    if user_id and self.firestore_query_service.delete_query(user_id, query.get('id')):
                        st.success("Query deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete query")
            
            # Show response if view is active
            if is_viewing:
                st.markdown("**🤖 Response:**")
                # Escape HTML characters in the response to prevent rendering issues
                escaped_response = self._escape_html(query.get('response', ''))
                st.markdown(escaped_response)
                st.markdown("---")
