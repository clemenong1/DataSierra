"""
PandasAI processor for natural language data queries
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

try:
    from pandasai import PandasAI
    from pandasai.llm.openai import OpenAI
    PANDASAI_AVAILABLE = True
except ImportError:
    PANDASAI_AVAILABLE = False


class PandasAIEnhancedProcessor:
    """Enhanced processor for PandasAI natural language queries"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.pandasai = None
        self.available = PANDASAI_AVAILABLE
        
        if self.available and self.openai_api_key:
            try:
                llm = OpenAI(api_token=self.openai_api_key)
                self.pandasai = PandasAI(llm, verbose=True)
            except Exception as e:
                logger.error(f"Failed to initialize PandasAI: {str(e)}")
                self.available = False
    
    def process_natural_language_query(
        self, 
        query: str, 
        dataframes: Dict[str, pd.DataFrame],
        session_id: str = "default"
    ) -> Dict[str, Any]:
        """Process natural language query using PandasAI"""
        
        if not self.available or not self.pandasai:
            return {
                "success": False,
                "error": "PandasAI not available",
                "answer": "PandasAI is not available. Please install it with: pip install pandasai"
            }
        
        try:
            # Convert dataframes to a list for PandasAI
            df_list = list(dataframes.values())
            
            if not df_list:
                return {
                    "success": False,
                    "error": "No dataframes provided",
                    "answer": "No data available for analysis."
                }
            
            # Process query with PandasAI
            result = self.pandasai.run(df_list, prompt=query)
            
            return {
                "success": True,
                "answer": str(result),
                "method": "pandasai",
                "dataframes_used": len(dataframes)
            }
            
        except Exception as e:
            logger.error(f"PandasAI processing error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "answer": f"Error processing query with PandasAI: {str(e)}"
            }
    
    def get_data_summary(self, dataframes: Dict[str, pd.DataFrame]) -> str:
        """Get a summary of the dataframes"""
        if not dataframes:
            return "No data available."
        
        summary_parts = []
        for name, df in dataframes.items():
            summary_parts.append(f"Dataset '{name}':")
            summary_parts.append(f"  - Shape: {df.shape}")
            summary_parts.append(f"  - Columns: {list(df.columns)}")
            summary_parts.append(f"  - Data types: {dict(df.dtypes)}")
            summary_parts.append(f"  - Missing values: {df.isnull().sum().sum()}")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def suggest_queries(self, dataframes: Dict[str, pd.DataFrame]) -> List[str]:
        """Suggest example queries based on the data"""
        if not dataframes:
            return []
        
        suggestions = []
        
        for name, df in dataframes.items():
            # Basic statistics queries
            if len(df.select_dtypes(include=['number']).columns) > 0:
                suggestions.append(f"What are the basic statistics for {name}?")
                suggestions.append(f"What is the average of numeric columns in {name}?")
            
            # Column-specific queries
            for col in df.columns:
                if df[col].dtype in ['object', 'string']:
                    suggestions.append(f"What are the unique values in {col} column?")
                elif df[col].dtype in ['int64', 'float64']:
                    suggestions.append(f"What is the distribution of {col}?")
            
            # Relationship queries for multiple datasets
            if len(dataframes) > 1:
                suggestions.append(f"How do the datasets relate to each other?")
                suggestions.append(f"Compare the datasets and find patterns")
        
        return suggestions[:10]  # Limit to 10 suggestions
