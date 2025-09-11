from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class QueryRequest:
    question: str
    file_name: str
    session_id: str = "default"
    include_visualizations: bool = True
    include_code_suggestions: bool = True


@dataclass
class QueryResponse:
    success: bool
    answer: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    visualizations: Optional[List[Dict[str, Any]]] = None
    code_suggestions: Optional[List[Dict[str, str]]] = None
    data_quality_insights: Optional[Dict[str, Any]] = None
    statistical_insights: Optional[Dict[str, Any]] = None
    business_insights: Optional[List[str]] = None
    pandasai_results: Optional[Dict[str, Any]] = None
    pandasai_insights: Optional[List[str]] = None


@dataclass
class QueryHistory:
    id: int
    query: str
    response: str
    file_name: str
    timestamp: datetime
    feedback: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'query': self.query,
            'response': self.response,
            'file_name': self.file_name,
            'timestamp': self.timestamp,
            'feedback': self.feedback
        }
