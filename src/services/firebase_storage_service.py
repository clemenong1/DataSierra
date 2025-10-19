import os
from firebase_admin import storage
from firebase_admin import credentials, initialize_app
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class FirebaseStorageService:
    """Service for handling Firebase Storage operations"""
    
    def __init__(self):
        self.bucket_name = f"{os.getenv('FIREBASE_PROJECT_ID', 'datasierra-5c806')}.firebasestorage.app"
        self._bucket = None
    
    def _get_bucket(self):
        """Get Firebase Storage bucket"""
        if self._bucket is None:
            try:
                self._bucket = storage.bucket(name=self.bucket_name)
            except Exception as e:
                logger.error(f"Error getting Firebase Storage bucket: {e}")
                return None
        return self._bucket

    def upload_file(self, file_data: bytes, filename: str, user_id: str, content_type: str) -> Optional[Dict[str, Any]]:
        """Uploads a file to Firebase Storage."""
        bucket = self._get_bucket()
        if not bucket:
            return None
        
        try:
            # Create a unique path for the file
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            blob_path = f"users/{user_id}/uploads/{timestamp}_{filename}"
            blob = bucket.blob(blob_path)
            
            blob.upload_from_string(file_data, content_type=content_type)
            blob.make_public() # Make the file publicly accessible for easy display
            
            logger.info(f"File {filename} uploaded to {blob_path}")
            
            return {
                "file_url": blob.public_url,
                "storage_path": blob_path,
                "original_filename": filename,
                "file_size": len(file_data),
                "content_type": content_type,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to upload file {filename} to Firebase Storage: {e}")
            return None

    def upload_visualization(self, file_data: bytes, filename: str, user_id: str, query: str, content_type: str) -> Optional[Dict[str, Any]]:
        """Uploads a visualization file to Firebase Storage."""
        bucket = self._get_bucket()
        if not bucket:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            blob_path = f"users/{user_id}/visualizations/{timestamp}_{filename}"
            blob = bucket.blob(blob_path)
            
            blob.upload_from_string(file_data, content_type=content_type)
            blob.make_public()
            
            logger.info(f"Visualization {filename} uploaded to {blob_path}")
            
            return {
                "file_url": blob.public_url,
                "storage_path": blob_path,
                "original_filename": filename,
                "file_size": len(file_data),
                "content_type": content_type,
                "created_at": datetime.utcnow().isoformat(),
                "query": query,
                "user_id": user_id
            }
        except Exception as e:
            logger.error(f"Failed to upload visualization {filename} to Firebase Storage: {e}")
            return None

    def upload_chart_image(self, image_data: bytes, filename: str, user_id: str, query: str) -> Optional[Dict[str, Any]]:
        """Uploads a chart image to Firebase Storage."""
        bucket = self._get_bucket()
        if not bucket:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            blob_path = f"users/{user_id}/chart_images/{timestamp}_{filename}"
            blob = bucket.blob(blob_path)
            
            blob.upload_from_string(image_data, content_type='image/png')
            blob.make_public()
            
            logger.info(f"Chart image {filename} uploaded to {blob_path}")
            
            return {
                "file_url": blob.public_url,
                "storage_path": blob_path,
                "original_filename": filename,
                "file_size": len(image_data),
                "content_type": 'image/png',
                "created_at": datetime.utcnow().isoformat(),
                "query": query,
                "user_id": user_id
            }
        except Exception as e:
            logger.error(f"Failed to upload chart image {filename} to Firebase Storage: {e}")
            return None

    def delete_file(self, storage_path: str) -> bool:
        """Deletes a file from Firebase Storage."""
        bucket = self._get_bucket()
        if not bucket:
            return False
        
        try:
            blob = bucket.blob(storage_path)
            blob.delete()
            logger.info(f"File {storage_path} deleted from Firebase Storage.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {storage_path} from Firebase Storage: {e}")
            return False

    def list_user_files(self, user_id: str, prefix: str = "uploads/", limit: int = 10) -> List[Dict[str, Any]]:
        """Lists files for a specific user in a given prefix."""
        bucket = self._get_bucket()
        if not bucket:
            return []
        
        try:
            blobs = bucket.list_blobs(prefix=f"users/{user_id}/{prefix}", max_results=limit)
            files = []
            for blob in blobs:
                files.append({
                    "name": blob.name.split('/')[-1],
                    "path": blob.name,
                    "size": blob.size,
                    "updated": blob.updated.isoformat(),
                    "url": blob.public_url
                })
            return files
        except Exception as e:
            logger.error(f"Failed to list files for user {user_id}: {e}")
            return []
