"""
Data analysis and processing service
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import logging

from ..models.file_models import ProcessedFile

logger = logging.getLogger(__name__)


class DataService:
    """Service for data analysis and insights"""
    
    def __init__(self):
        pass
    
    def get_data_preview(self, processed_file: ProcessedFile, n_rows: int = 10) -> pd.DataFrame:
        """Get data preview from processed file"""
        try:
            # Convert data_json back to DataFrame for preview
            df = pd.DataFrame(processed_file.data_json)
            return df.head(n_rows)
        except Exception as e:
            logger.error(f"Error getting data preview: {str(e)}")
            return pd.DataFrame()
    
    def generate_visualizations(self, processed_files: Dict[str, ProcessedFile], 
                              user_question: str) -> List[Dict[str, Any]]:
        """Generate visualization suggestions based on data and question"""
        visualizations = []
        
        if not processed_files:
            return visualizations
        
        question_lower = user_question.lower()
        
        for file_name, processed_file in processed_files.items():
            numeric_cols = processed_file.get_numeric_columns()
            categorical_cols = processed_file.get_categorical_columns()
            
            # Correlation visualization
            if 'correlation' in question_lower and len(numeric_cols) >= 2:
                visualizations.append({
                    "type": "heatmap",
                    "title": f"Correlation Matrix - {file_name}",
                    "description": "Heatmap showing correlations between numeric variables",
                    "columns": numeric_cols[:5],
                    "code": self._generate_correlation_code(numeric_cols[:5])
                })
            
            # Distribution visualization
            if 'distribution' in question_lower or 'pattern' in question_lower:
                if numeric_cols:
                    visualizations.append({
                        "type": "histogram",
                        "title": f"Distribution Analysis - {file_name}",
                        "description": "Histograms showing distributions of numeric variables",
                        "columns": numeric_cols[:3],
                        "code": self._generate_distribution_code(numeric_cols[:3])
                    })
            
            # Categorical analysis
            if categorical_cols and ('category' in question_lower or 'count' in question_lower):
                visualizations.append({
                    "type": "bar_chart",
                    "title": f"Categorical Analysis - {file_name}",
                    "description": "Bar chart showing value counts for categorical variables",
                    "columns": categorical_cols[:2],
                    "code": self._generate_categorical_code(categorical_cols[:2])
                })
        
        return visualizations[:3]  # Limit to 3 visualizations
    
    def generate_code_suggestions(self, processed_files: Dict[str, ProcessedFile]) -> List[Dict[str, str]]:
        """Generate Python code suggestions for further analysis"""
        suggestions = []
        
        # Basic analysis code
        suggestions.append({
            "title": "Basic Data Overview",
            "code": """
# Basic data overview
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load your data
df = pd.read_csv('your_file.csv')  # or pd.read_excel('your_file.xlsx')

# Basic info
print("Dataset shape:", df.shape)
print("\\nColumn types:")
print(df.dtypes)
print("\\nMissing values:")
print(df.isnull().sum())
print("\\nBasic statistics:")
print(df.describe())
""",
            "description": "Get a comprehensive overview of your dataset"
        })
        
        # Generate specific suggestions based on data
        for file_name, processed_file in processed_files.items():
            numeric_cols = processed_file.get_numeric_columns()
            categorical_cols = processed_file.get_categorical_columns()
            
            if len(numeric_cols) >= 2:
                suggestions.append({
                    "title": f"Correlation Analysis - {file_name}",
                    "code": self._generate_correlation_code(numeric_cols[:5]),
                    "description": f"Analyze correlations between numeric variables in {file_name}"
                })
                break
        
        for file_name, processed_file in processed_files.items():
            numeric_cols = processed_file.get_numeric_columns()
            if numeric_cols:
                suggestions.append({
                    "title": f"Distribution Analysis - {file_name}",
                    "code": self._generate_distribution_code(numeric_cols[:3]),
                    "description": f"Analyze distributions and detect outliers in {file_name}"
                })
                break
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _generate_correlation_code(self, numeric_cols: List[str]) -> str:
        """Generate correlation analysis code"""
        return f"""
# Correlation analysis
numeric_cols = {numeric_cols}
correlation_matrix = df[numeric_cols].corr()

# Visualize correlations
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Matrix')
plt.show()

# Find strong correlations
strong_correlations = correlation_matrix[abs(correlation_matrix) > 0.7]
print("Strong correlations (>0.7):")
print(strong_correlations)
"""
    
    def _generate_distribution_code(self, numeric_cols: List[str]) -> str:
        """Generate distribution analysis code"""
        return f"""
# Distribution analysis
numeric_cols = {numeric_cols}

# Create distribution plots
fig, axes = plt.subplots(1, {min(3, len(numeric_cols))}, figsize=(15, 5))
for i, col in enumerate(numeric_cols):
    axes[i].hist(df[col].dropna(), bins=30, alpha=0.7)
    axes[i].set_title(f'Distribution of {{col}}')
    axes[i].set_xlabel(col)
    axes[i].set_ylabel('Frequency')

plt.tight_layout()
plt.show()

# Box plots for outlier detection
df[numeric_cols].boxplot(figsize=(12, 6))
plt.title('Box Plots for Outlier Detection')
plt.xticks(rotation=45)
plt.show()
"""
    
    def _generate_categorical_code(self, categorical_cols: List[str]) -> str:
        """Generate categorical analysis code"""
        return f"""
# Categorical analysis
fig, axes = plt.subplots(1, {min(2, len(categorical_cols))}, figsize=(12, 5))
for i, col in enumerate(categorical_cols):
    value_counts = df[col].value_counts().head(10)
    axes[i].bar(range(len(value_counts)), value_counts.values)
    axes[i].set_title(f'Top 10 values in {{col}}')
    axes[i].set_xlabel(col)
    axes[i].set_ylabel('Count')
    axes[i].set_xticks(range(len(value_counts)))
    axes[i].set_xticklabels(value_counts.index, rotation=45)
plt.tight_layout()
plt.show()
"""
    
    def create_data_summary(self, processed_files: Dict[str, ProcessedFile]) -> Dict[str, Any]:
        """Create a summary of all processed data"""
        summary = {
            "total_files": len(processed_files),
            "total_rows": sum(pf.total_rows for pf in processed_files.values()),
            "total_columns": sum(pf.total_columns for pf in processed_files.values()),
            "file_types": {},
            "data_quality": {
                "average_completeness": 0,
                "files_with_issues": 0
            }
        }
        
        # Analyze file types
        for processed_file in processed_files.values():
            file_type = processed_file.file_info.type
            summary["file_types"][file_type] = summary["file_types"].get(file_type, 0) + 1
        
        # Analyze data quality
        completeness_scores = []
        for processed_file in processed_files.values():
            completeness = processed_file.data_quality.completeness_score
            completeness_scores.append(completeness)
            if completeness < 80:
                summary["data_quality"]["files_with_issues"] += 1
        
        if completeness_scores:
            summary["data_quality"]["average_completeness"] = sum(completeness_scores) / len(completeness_scores)
        
        return summary
