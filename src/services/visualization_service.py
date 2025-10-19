from typing import Dict, List, Optional, Any
from datetime import datetime
from firebase_admin import firestore

from .firebase_config import FirebaseConfig

class VisualizationService:
    
    def __init__(self):
        self.db = FirebaseConfig.get_firestore_client()
    
    def save_visualization(self, user_uid: str, viz_data: Dict[str, Any]) -> Optional[str]:
        try:
            if not self.db:
                return None
            
            # Add default fields if not present
            viz_data['created_at'] = viz_data.get('created_at', datetime.utcnow().isoformat())
            viz_data['helpfulness_updated_at'] = None
            viz_data['is_helpful'] = None
            viz_data['user_id'] = user_uid # Ensure user_id is explicitly stored
            
            doc_ref = self.db.collection('users').document(user_uid).collection('visualisations').add(viz_data)
            
            return doc_ref[1].id if doc_ref else None
            
        except Exception as e:
            return None
    
    def get_user_visualizations(self, user_uid: str, limit: int = 10, order_by: str = 'created_at') -> List[Dict[str, Any]]:
        """
        Get user's visualizations from Firestore.
        
        Args:
            user_uid: User's Firebase UID
            limit: Maximum number of visualizations to return
            order_by: Field to order by (default: created_at)
            
        Returns:
            List of visualization dictionaries
        """
        try:
            if not self.db:
                return []
            
            viz_ref = self.db.collection('users').document(user_uid).collection('visualisations')
            query = viz_ref.order_by(order_by, direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            
            visualizations = []
            for doc in docs:
                viz = doc.to_dict()
                viz['id'] = doc.id # Add document ID to the dict
                visualizations.append(viz)
            
            return visualizations
            
        except Exception as e:
            return []

    def update_visualization_helpfulness(self, user_uid: str, viz_id: str, is_helpful: bool) -> bool:
        """
        Update the helpfulness status of a visualization.
        """
        try:
            if not self.db:
                return False
            
            doc_ref = self.db.collection('users').document(user_uid).collection('visualisations').document(viz_id)
            doc_ref.update({
                'is_helpful': is_helpful,
                'helpfulness_updated_at': datetime.utcnow().isoformat()
            })
            return True
        except Exception as e:
            return False

    def delete_visualization(self, user_uid: str, viz_id: str) -> bool:
        """
        Delete a visualization from Firestore.
        """
        try:
            if not self.db:
                return False
            
            doc_ref = self.db.collection('users').document(user_uid).collection('visualisations').document(viz_id)
            doc_ref.delete()
            return True
        except Exception as e:
            return False
