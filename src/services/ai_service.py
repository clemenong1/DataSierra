"""
AI service for handling OpenAI and PandasAI interactions
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from ..models.query_models import QueryRequest, QueryResponse
from ..models.file_models import ProcessedFile

# Import AI modules
from .ai.openai_client import OpenAIClient, ConversationMemory
from .ai.pandasai_processor import PandasAIEnhancedProcessor

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered data analysis"""
    
    def __init__(self, openai_api_key: Optional[str] = None, model: str = "gpt-4"):
        # Load environment variables from .env file
        self._load_env_variables()
        
        # Try to get API key from multiple sources
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # Log final status
        if self.openai_api_key:
            logger.info("OpenAI API key is available")
        else:
            logger.warning("OpenAI API key not found in environment variables")
        
        self.model = model
        self.conversation_sessions = {}
        
        # Initialize AI components
        self._initialize_ai_components()
    
    def _load_env_variables(self):
        """Load environment variables from .env file"""
        try:
            from dotenv import load_dotenv
            # Load .env file from project root
            env_path = Path(__file__).parent.parent.parent / ".env"
            if env_path.exists():
                load_dotenv(env_path)
                logger.info("Environment variables loaded from .env file")
            else:
                logger.warning(".env file not found, using system environment variables")
        except ImportError:
            logger.warning("python-dotenv not installed, using system environment variables")
        except Exception as e:
            logger.error(f"Error loading .env file: {e}")
    
    def _initialize_ai_components(self):
        """Initialize AI components"""
        try:
            if self.openai_api_key:
                self.openai_client = OpenAIClient(api_key=self.openai_api_key, model=self.model)
                self.pandasai_processor = PandasAIEnhancedProcessor(
                    openai_api_key=self.openai_api_key
                )
                logger.info("AI components initialized successfully")
            else:
                logger.warning("OpenAI API key not provided. AI features will be limited.")
                self.openai_client = None
                self.pandasai_processor = None
        except Exception as e:
            logger.error(f"Failed to initialize AI components: {str(e)}")
            self.openai_client = None
            self.pandasai_processor = None
    
    def process_query(self, request: QueryRequest, processed_files: Dict[str, ProcessedFile]) -> QueryResponse:
        """Process a user query with AI analysis"""
        try:
            if not self.openai_client:
                return QueryResponse(
                    success=False,
                    error="AI service not available. Please check your OpenAI API key.",
                    error_type="ai_unavailable"
                )
            
            # Convert ProcessedFile objects to the format expected by existing processors
            files_for_processing = self._convert_processed_files_for_ai(processed_files)
            
            # Get or create conversation session
            if request.session_id not in self.conversation_sessions:
                self.conversation_sessions[request.session_id] = ConversationMemory()
            
            conversation_memory = self.conversation_sessions[request.session_id]
            
            # Process with PandasAI if available
            pandasai_response = None
            if self.pandasai_processor and self._is_data_query(request.question):
                pandasai_response = self._process_with_pandasai(request, files_for_processing)
            
            # Build data context
            data_context = self._build_data_context(processed_files, request.question)
            
            # Process with OpenAI
            openai_response = self.openai_client.query_openai_with_data_context(
                question=request.question,
                data_context=data_context,
                session_id=request.session_id,
                include_conversation=True
            )
            
            if not openai_response.get("success", False):
                return QueryResponse(
                    success=False,
                    error=openai_response.get("error", "Unknown error"),
                    error_type=openai_response.get("error_type", "unknown")
                )
            
            # Enhance response with additional insights
            enhanced_response = self._enhance_response(
                openai_response, processed_files, pandasai_response
            )
            
            return QueryResponse(
                success=True,
                answer=enhanced_response.get("answer"),
                metadata=enhanced_response.get("metadata", {}),
                suggestions=enhanced_response.get("suggestions", []),
                visualizations=enhanced_response.get("visualizations", []),
                code_suggestions=enhanced_response.get("code_suggestions", []),
                data_quality_insights=enhanced_response.get("data_quality_insights", {}),
                statistical_insights=enhanced_response.get("statistical_insights", {}),
                business_insights=enhanced_response.get("business_insights", []),
                pandasai_results=enhanced_response.get("pandasai_results"),
                pandasai_insights=enhanced_response.get("pandasai_insights", [])
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return QueryResponse(
                success=False,
                error=f"An unexpected error occurred: {str(e)}",
                error_type="processing_error"
            )
    
    def _convert_processed_files_for_ai(self, processed_files: Dict[str, ProcessedFile]) -> Dict[str, Any]:
        """Convert ProcessedFile objects to DataFrames for AI processors"""
        import pandas as pd
        
        dataframes = {}
        
        for file_name, processed_file in processed_files.items():
            try:
                # Convert data_json back to DataFrame
                df = pd.DataFrame(processed_file.data_json)
                dataframes[file_name] = df
            except Exception as e:
                logger.warning(f"Failed to convert {file_name} to DataFrame: {str(e)}")
                # Create empty DataFrame as fallback
                dataframes[file_name] = pd.DataFrame()
        
        return dataframes
    
    def _is_data_query(self, question: str) -> bool:
        """Determine if the question is suitable for PandasAI processing"""
        data_keywords = [
            'average', 'mean', 'sum', 'count', 'max', 'min', 'median',
            'correlation', 'group by', 'filter', 'sort', 'top', 'bottom',
            'trend', 'pattern', 'distribution', 'outlier', 'missing',
            'compare', 'difference', 'percentage', 'ratio', 'statistics'
        ]
        
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in data_keywords)
    
    def _process_with_pandasai(self, request: QueryRequest, files_for_processing: List[Any]) -> Optional[Dict[str, Any]]:
        """Process query using PandasAI"""
        try:
            if not self.pandasai_processor:
                return None
            
            response = self.pandasai_processor.process_natural_language_query(
                query=request.question,
                dataframes=files_for_processing,
                session_id=request.session_id
            )
            
            return response
            
        except Exception as e:
            logger.warning(f"PandasAI processing failed: {str(e)}")
            return None
    
    def _build_data_context(self, processed_files: Dict[str, ProcessedFile], question: str) -> Dict[str, Any]:
        """Build data context for AI processing"""
        context = {
            "datasets": [],
            "analysis_context": {},
            "query_guidance": {}
        }
        
        # Process each dataset
        for file_name, processed_file in processed_files.items():
            dataset_context = {
                "name": file_name,
                "type": processed_file.file_info.type,
                "shape": processed_file.file_info.shape,
                "total_rows": processed_file.total_rows,
                "total_columns": processed_file.total_columns,
                "columns": {},
                "sample_rows": processed_file.sample_rows,
                "data_quality": {
                    "total_nulls": processed_file.data_quality.total_nulls,
                    "duplicate_rows": processed_file.data_quality.duplicate_rows,
                    "completeness_score": processed_file.data_quality.completeness_score,
                    "uniqueness_score": processed_file.data_quality.uniqueness_score
                },
                "summary_statistics": {
                    "numeric_columns": processed_file.get_numeric_columns(),
                    "categorical_columns": processed_file.get_categorical_columns(),
                    "column_distribution": {
                        "numeric": len(processed_file.get_numeric_columns()),
                        "categorical": len(processed_file.get_categorical_columns())
                    }
                }
            }
            
            # Add column information
            for col_name, col_info in processed_file.column_statistics.items():
                dataset_context["columns"][col_name] = {
                    "type": col_info.get('type', 'unknown'),
                    "sample_values": col_info.get('sample_values', []),
                    "null_count": col_info.get('null_count', 0),
                    "null_percentage": col_info.get('null_percentage', 0),
                    "unique_count": col_info.get('unique_count', 0),
                    "unique_percentage": col_info.get('unique_percentage', 0),
                    "statistics": col_info.get('statistics', {})
                }
            
            context["datasets"].append(dataset_context)
        
        # Add analysis context
        total_rows = sum(pf.total_rows for pf in processed_files.values())
        total_columns = sum(pf.total_columns for pf in processed_files.values())
        
        context["analysis_context"] = {
            "total_datasets": len(processed_files),
            "total_rows": total_rows,
            "total_columns": total_columns,
            "question_type": self._analyze_question_type(question),
            "analysis_scope": "single_dataset" if len(processed_files) == 1 else "multi_dataset"
        }
        
        return context
    
    def _analyze_question_type(self, question: str) -> str:
        """Analyze the type of question being asked"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['correlation', 'relationship', 'related']):
            return 'correlation_analysis'
        elif any(word in question_lower for word in ['trend', 'pattern', 'change over time']):
            return 'trend_analysis'
        elif any(word in question_lower for word in ['compare', 'comparison', 'difference']):
            return 'comparative_analysis'
        elif any(word in question_lower for word in ['summary', 'describe', 'overview']):
            return 'descriptive_analysis'
        elif any(word in question_lower for word in ['outlier', 'anomaly', 'unusual']):
            return 'anomaly_detection'
        elif any(word in question_lower for word in ['predict', 'forecast', 'future']):
            return 'predictive_analysis'
        else:
            return 'general_analysis'
    
    def _enhance_response(self, openai_response: Dict[str, Any], 
                         processed_files: Dict[str, ProcessedFile],
                         pandasai_response: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance OpenAI response with additional insights"""
        enhanced_response = openai_response.copy()
        
        # Add PandasAI results if available
        if pandasai_response:
            # Wrap single PandasAI response in a dictionary format expected by UI
            enhanced_response["pandasai_results"] = {"analysis": pandasai_response}
        
        # Add data quality insights
        enhanced_response["data_quality_insights"] = self._analyze_data_quality(processed_files)
        
        # Add statistical insights
        enhanced_response["statistical_insights"] = self._generate_statistical_insights(processed_files)
        
        # Add business insights
        enhanced_response["business_insights"] = self._generate_business_insights(processed_files)
        
        return enhanced_response
    
    def _analyze_data_quality(self, processed_files: Dict[str, ProcessedFile]) -> Dict[str, Any]:
        """Analyze data quality across all files"""
        quality_insights = {
            "overall_score": 0,
            "issues": [],
            "recommendations": []
        }
        
        total_files = len(processed_files)
        total_score = 0
        
        for file_name, processed_file in processed_files.items():
            data_quality = processed_file.data_quality
            file_score = data_quality.overall_score
            total_score += file_score
            
            # Identify issues
            if data_quality.completeness_score < 80:
                quality_insights["issues"].append(
                    f"{file_name}: Low data completeness ({data_quality.completeness_score:.1f}%)"
                )
            
            if data_quality.uniqueness_score < 50:
                quality_insights["issues"].append(
                    f"{file_name}: Low data uniqueness ({data_quality.uniqueness_score:.1f}%)"
                )
            
            if data_quality.total_nulls > 0:
                quality_insights["issues"].append(
                    f"{file_name}: {data_quality.total_nulls} missing values"
                )
        
        quality_insights["overall_score"] = total_score / total_files if total_files > 0 else 0
        
        return quality_insights
    
    def _generate_statistical_insights(self, processed_files: Dict[str, ProcessedFile]) -> Dict[str, Any]:
        """Generate statistical insights from the data"""
        insights = {
            "numeric_summaries": {},
            "categorical_summaries": {},
            "correlations": {},
            "outliers": {}
        }
        
        for file_name, processed_file in processed_files.items():
            # Numeric column summaries
            numeric_cols = processed_file.get_numeric_columns()
            if numeric_cols:
                insights["numeric_summaries"][file_name] = {}
                for col_name in numeric_cols:
                    col_info = processed_file.column_statistics[col_name]
                    stats = col_info.get("statistics", {})
                    insights["numeric_summaries"][file_name][col_name] = {
                        "mean": stats.get("mean"),
                        "median": stats.get("median"),
                        "std": stats.get("std"),
                        "range": f"{stats.get('min')} - {stats.get('max')}" if stats.get('min') is not None else None
                    }
        
        return insights
    
    def _generate_business_insights(self, processed_files: Dict[str, ProcessedFile]) -> List[str]:
        """Generate business-focused insights"""
        insights = []
        
        total_rows = sum(pf.total_rows for pf in processed_files.values())
        
        if total_rows > 10000:
            insights.append(f"Large dataset with {total_rows:,} records - suitable for robust statistical analysis")
        elif total_rows > 1000:
            insights.append(f"Medium-sized dataset with {total_rows:,} records - good for trend analysis")
        else:
            insights.append(f"Small dataset with {total_rows:,} records - focus on descriptive analysis")
        
        # Data quality insights
        for file_name, processed_file in processed_files.items():
            completeness = processed_file.data_quality.completeness_score
            if completeness > 95:
                insights.append(f"{file_name}: Excellent data quality ({completeness:.1f}% complete)")
            elif completeness > 80:
                insights.append(f"{file_name}: Good data quality ({completeness:.1f}% complete)")
            else:
                insights.append(f"{file_name}: Data quality needs attention ({completeness:.1f}% complete)")
        
        return insights[:5]  # Limit to 5 insights
    
    def get_session_conversation(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a session"""
        if session_id in self.conversation_sessions:
            return self.conversation_sessions[session_id].get_conversation(session_id)
        return []
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversation_sessions:
            self.conversation_sessions[session_id].clear_history()
    
    def get_all_sessions(self) -> Dict[str, Any]:
        """Get information about all active sessions"""
        sessions_info = {}
        for session_id, memory in self.conversation_sessions.items():
            sessions_info[session_id] = memory.get_summary()
        return sessions_info
