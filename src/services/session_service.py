"""
Session management service with Firestore integration
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models.query_models import QueryHistory
from ..models.session_models import SessionInfo
from .firestore_query_service import FirestoreQueryService
from .auth_service import AuthService


class SessionService:
    """Service for managing user sessions and query history with Firestore integration"""
    
    def __init__(self):
        self.query_history: List[QueryHistory] = []
        self.current_query_id = 0
        self.feedback_data: Dict[int, Dict[str, Any]] = {}
        self.firestore_service = FirestoreQueryService()
        self.auth_service = AuthService()
    
    def save_query_history(self, query: str, response: str, file_name: str) -> int:
        """Save query to history and Firestore, return query ID"""
        # Save to local memory (for backward compatibility)
        query_id = self.current_query_id
        query_history_entry = QueryHistory(
            id=query_id,
            query=query,
            response=response,
            file_name=file_name,
            timestamp=datetime.now()
        )
        
        self.query_history.append(query_history_entry)
        self.current_query_id += 1
        
        # Save to Firestore if user is authenticated
        if self.auth_service.is_authenticated():
            user_uid = self.auth_service.get_user_uid()
            if user_uid:
                self.firestore_service.save_query(user_uid, query, response, file_name)
        
        return query_id
    
    def get_query_history(self, limit: int = 10, search_term: Optional[str] = None) -> List[QueryHistory]:
        """Get query history from Firestore with optional filtering"""
        # If user is authenticated, get from Firestore
        if self.auth_service.is_authenticated():
            user_uid = self.auth_service.get_user_uid()
            if user_uid:
                if search_term:
                    return self.firestore_service.search_user_queries(user_uid, search_term, limit)
                else:
                    return self.firestore_service.get_user_queries(user_uid, limit)
        
        # Fallback to local memory for non-authenticated users
        filtered_history = self.query_history
        
        if search_term:
            search_lower = search_term.lower()
            filtered_history = [
                item for item in self.query_history
                if search_lower in item.query.lower() or 
                   search_lower in item.response.lower()
            ]
        
        # Return last N items, reversed (most recent first)
        return list(reversed(filtered_history[-limit:]))
    
    def get_query_by_id(self, query_id: int) -> Optional[QueryHistory]:
        """Get a specific query by ID"""
        # If user is authenticated, try to get from Firestore first
        if self.auth_service.is_authenticated():
            user_uid = self.auth_service.get_user_uid()
            if user_uid:
                firestore_query = self.firestore_service.get_query_by_id(user_uid, str(query_id))
                if firestore_query:
                    return firestore_query
        
        # Fallback to local memory
        for query in self.query_history:
            if query.id == query_id:
                return query
        return None
    
    def submit_feedback(self, query_id: int, feedback_type: str, comment: str = "") -> bool:
        """Submit feedback for a query"""
        try:
            self.feedback_data[query_id] = {
                'type': feedback_type,
                'comment': comment,
                'timestamp': datetime.now()
            }
            
            # Update the query history entry
            query = self.get_query_by_id(query_id)
            if query:
                query.feedback = feedback_type
            
            # Update in Firestore if user is authenticated
            if self.auth_service.is_authenticated():
                user_uid = self.auth_service.get_user_uid()
                if user_uid:
                    self.firestore_service.update_query_feedback(user_uid, str(query_id), feedback_type)
            
            return True
            
        except Exception as e:
            return False
    
    def get_feedback_data(self, query_id: int) -> Optional[Dict[str, Any]]:
        """Get feedback data for a query"""
        return self.feedback_data.get(query_id)
    
    def clear_history(self) -> bool:
        """Clear all query history"""
        try:
            # Clear local memory
            self.query_history = []
            self.feedback_data = {}
            self.current_query_id = 0
            
            # Clear from Firestore if user is authenticated
            if self.auth_service.is_authenticated():
                user_uid = self.auth_service.get_user_uid()
                if user_uid:
                    self.firestore_service.clear_user_queries(user_uid)
            
            return True
        except Exception as e:
            return False
    
    def get_history_statistics(self) -> Dict[str, Any]:
        """Get statistics about query history"""
        # If user is authenticated, get stats from Firestore
        if self.auth_service.is_authenticated():
            user_uid = self.auth_service.get_user_uid()
            if user_uid:
                firestore_stats = self.firestore_service.get_user_query_stats(user_uid)
                if firestore_stats:
                    return firestore_stats
        
        # Fallback to local memory stats
        total_queries = len(self.query_history)
        total_feedback = len(self.feedback_data)
        
        # Count feedback types
        feedback_types = {}
        for feedback in self.feedback_data.values():
            feedback_type = feedback.get('type', 'unknown')
            feedback_types[feedback_type] = feedback_types.get(feedback_type, 0) + 1
        
        # Get most recent query time
        last_query_time = None
        if self.query_history:
            last_query_time = max(query.timestamp for query in self.query_history)
        
        return {
            "total_queries": total_queries,
            "total_feedback": total_feedback,
            "feedback_types": feedback_types,
            "last_query_time": last_query_time.isoformat() if last_query_time else None,
            "current_query_id": self.current_query_id
        }
    
    def export_history(self, format: str = "json") -> Dict[str, Any]:
        """Export query history in specified format"""
        if format.lower() == "json":
            return {
                "query_history": [query.to_dict() for query in self.query_history],
                "feedback_data": self.feedback_data,
                "statistics": self.get_history_statistics(),
                "export_timestamp": datetime.now().isoformat()
            }
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_history(self, data: Dict[str, Any]) -> bool:
        """Import query history from exported data"""
        try:
            if "query_history" in data:
                self.query_history = []
                for query_data in data["query_history"]:
                    query = QueryHistory(
                        id=query_data["id"],
                        query=query_data["query"],
                        response=query_data["response"],
                        file_name=query_data["file_name"],
                        timestamp=datetime.fromisoformat(query_data["timestamp"]),
                        feedback=query_data.get("feedback")
                    )
                    self.query_history.append(query)
                
                # Update current query ID
                if self.query_history:
                    self.current_query_id = max(query.id for query in self.query_history) + 1
                else:
                    self.current_query_id = 0
            
            if "feedback_data" in data:
                self.feedback_data = data["feedback_data"]
            
            return True
            
        except Exception as e:
            return False
