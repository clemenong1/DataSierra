"""
Firestore-based query storage service
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from firebase_admin import firestore

from .firebase_config import FirebaseConfig
from ..models.query_models import QueryHistory


class FirestoreQueryService:
    """Service for storing and retrieving user queries from Firestore"""
    
    def __init__(self):
        self.db = FirebaseConfig.get_firestore_client()
    
    def save_query(self, user_uid: str, query: str, response: str, file_name: str) -> Optional[str]:
        """
        Save a query to the user's queries subcollection
        
        Args:
            user_uid: User's Firebase UID
            query: The user's query
            response: The AI response
            file_name: Name of the file being queried
            
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            if not self.db:
                return None
            
            # Create query document
            query_data = {
                'query': query,
                'response': response,
                'file_name': file_name,
                'timestamp': datetime.utcnow(),
                'created_at': datetime.utcnow()
            }
            
            
            # Add to user's queries subcollection
            doc_ref = self.db.collection('users').document(user_uid).collection('queries').add(query_data)
            
            return doc_ref[1].id if doc_ref else None
            
        except Exception as e:
            return None
    
    def get_user_queries(self, user_uid: str, limit: int = 10, order_by: str = 'timestamp') -> List[QueryHistory]:
        """
        Get user's queries from Firestore
        
        Args:
            user_uid: User's Firebase UID
            limit: Maximum number of queries to return
            order_by: Field to order by (default: timestamp)
            
        Returns:
            List of QueryHistory objects
        """
        try:
            if not self.db:
                return []
            
            # Query user's queries subcollection
            queries_ref = self.db.collection('users').document(user_uid).collection('queries')
            
            # Order by timestamp descending (most recent first) and limit results
            query = queries_ref.order_by(order_by, direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            
            query_history = []
            for doc in docs:
                data = doc.to_dict()
                query_history.append(QueryHistory(
                    id=hash(doc.id) % (2**31),  # Convert string ID to integer
                    query=data.get('query', ''),
                    response=data.get('response', ''),
                    file_name=data.get('file_name', ''),
                    timestamp=data.get('timestamp', datetime.utcnow()),
                    feedback=data.get('feedback')
                ))
            
            return query_history
            
        except Exception as e:
            return []
    
    def search_user_queries(self, user_uid: str, search_term: str, limit: int = 10) -> List[QueryHistory]:
        """
        Search user's queries by query text or response
        
        Args:
            user_uid: User's Firebase UID
            search_term: Term to search for
            limit: Maximum number of results
            
        Returns:
            List of matching QueryHistory objects
        """
        try:
            if not self.db or not search_term:
                return []
            
            # Get all user queries (Firestore doesn't support full-text search easily)
            all_queries = self.get_user_queries(user_uid, limit=100)  # Get more to filter
            
            # Filter by search term
            search_lower = search_term.lower()
            filtered_queries = [
                query for query in all_queries
                if search_lower in query.query.lower() or 
                   search_lower in query.response.lower()
            ]
            
            return filtered_queries[:limit]
            
        except Exception as e:
            return []
    
    def get_query_by_id(self, user_uid: str, query_id: str) -> Optional[QueryHistory]:
        """
        Get a specific query by ID
        
        Args:
            user_uid: User's Firebase UID
            query_id: Query document ID
            
        Returns:
            QueryHistory object or None if not found
        """
        try:
            if not self.db:
                return None
            
            doc_ref = self.db.collection('users').document(user_uid).collection('queries').document(query_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return QueryHistory(
                    id=hash(doc.id) % (2**31),  # Convert string ID to integer
                    query=data.get('query', ''),
                    response=data.get('response', ''),
                    file_name=data.get('file_name', ''),
                    timestamp=data.get('timestamp', datetime.utcnow()),
                    feedback=data.get('feedback')
                )
            
            return None
            
        except Exception as e:
            return None
    
    def update_query_feedback(self, user_uid: str, query_id: str, feedback: str) -> bool:
        """
        Update feedback for a query
        
        Args:
            user_uid: User's Firebase UID
            query_id: Query document ID
            feedback: Feedback to add
            
        Returns:
            True if successful
        """
        try:
            if not self.db:
                return False
            
            doc_ref = self.db.collection('users').document(user_uid).collection('queries').document(query_id)
            doc_ref.update({
                'feedback': feedback,
                'feedback_updated_at': datetime.utcnow()
            })
            
            return True
            
        except Exception as e:
            return False
    
    def delete_query(self, user_uid: str, query_id: str) -> bool:
        """
        Delete a query
        
        Args:
            user_uid: User's Firebase UID
            query_id: Query document ID
            
        Returns:
            True if successful
        """
        try:
            if not self.db:
                return False
            
            doc_ref = self.db.collection('users').document(user_uid).collection('queries').document(query_id)
            doc_ref.delete()
            
            return True
            
        except Exception as e:
            return False
    
    def clear_user_queries(self, user_uid: str) -> bool:
        """
        Clear all queries for a user
        
        Args:
            user_uid: User's Firebase UID
            
        Returns:
            True if successful
        """
        try:
            if not self.db:
                return False
            
            # Get all query documents
            queries_ref = self.db.collection('users').document(user_uid).collection('queries')
            docs = queries_ref.stream()
            
            # Delete each document
            for doc in docs:
                doc.reference.delete()
            
            return True
            
        except Exception as e:
            return False
    
    def get_user_query_stats(self, user_uid: str) -> Dict[str, Any]:
        """
        Get statistics about user's queries
        
        Args:
            user_uid: User's Firebase UID
            
        Returns:
            Dictionary with query statistics
        """
        try:
            if not self.db:
                return {}
            
            queries = self.get_user_queries(user_uid, limit=1000)  # Get all queries for stats
            
            total_queries = len(queries)
            files_queried = set(query.file_name for query in queries)
            feedback_count = sum(1 for query in queries if query.feedback)
            
            # Get most recent query time
            last_query_time = None
            if queries:
                last_query_time = max(query.timestamp for query in queries)
            
            return {
                'total_queries': total_queries,
                'unique_files': len(files_queried),
                'files_queried': list(files_queried),
                'feedback_count': feedback_count,
                'last_query_time': last_query_time.isoformat() if last_query_time else None
            }
            
        except Exception as e:
            return {}