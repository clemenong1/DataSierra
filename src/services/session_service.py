"""
Session management service
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..models.query_models import QueryHistory
from ..models.session_models import SessionInfo

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing user sessions and query history"""
    
    def __init__(self):
        self.query_history: List[QueryHistory] = []
        self.current_query_id = 0
        self.feedback_data: Dict[int, Dict[str, Any]] = {}
    
    def save_query_history(self, query: str, response: str, file_name: str) -> int:
        """Save query to history and return query ID"""
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
        
        logger.info(f"Saved query {query_id} to history")
        return query_id
    
    def get_query_history(self, limit: int = 10, search_term: Optional[str] = None) -> List[QueryHistory]:
        """Get query history with optional filtering"""
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
            
            logger.info(f"Feedback submitted for query {query_id}: {feedback_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {str(e)}")
            return False
    
    def get_feedback_data(self, query_id: int) -> Optional[Dict[str, Any]]:
        """Get feedback data for a query"""
        return self.feedback_data.get(query_id)
    
    def clear_history(self) -> bool:
        """Clear all query history"""
        try:
            self.query_history = []
            self.feedback_data = {}
            self.current_query_id = 0
            logger.info("Query history cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing history: {str(e)}")
            return False
    
    def get_history_statistics(self) -> Dict[str, Any]:
        """Get statistics about query history"""
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
            
            logger.info("Query history imported successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error importing history: {str(e)}")
            return False
