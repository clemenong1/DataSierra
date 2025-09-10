"""
File processing service
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..models.file_models import FileInfo, ProcessedFile, DataQuality

logger = logging.getLogger(__name__)


class FileService:
    """Service for handling file operations"""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls']
        self.max_file_size = 200 * 1024 * 1024  # 200MB
        
    def validate_file(self, file: Any) -> bool:
        """Validate uploaded file"""
        if file.size > self.max_file_size:
            logger.warning(f"File {file.name} exceeds maximum size limit")
            return False
            
        if not any(file.name.endswith(ext) for ext in self.supported_formats):
            logger.warning(f"Unsupported file format: {file.name}")
            return False
            
        return True
    
    def process_file(self, file: Any) -> Optional[ProcessedFile]:
        """Process a single file and return ProcessedFile object"""
        try:
            if not self.validate_file(file):
                return None
                
            # Read file based on type
            if file.name.endswith('.csv'):
                df = self._read_csv(file)
            elif file.name.endswith(('.xlsx', '.xls')):
                df = self._read_excel(file)
            else:
                return None
                
            if df is None or df.empty:
                return None
                
            # Create file info
            file_info = FileInfo(
                name=file.name,
                size=file.size,
                type=self._get_file_type(file.name),
                upload_time=datetime.now(),
                shape=df.shape,
                columns=list(df.columns),
                dtypes=df.dtypes.to_dict()
            )
            
            # Calculate data quality
            data_quality = self._calculate_data_quality(df)
            
            # Get sample rows
            sample_rows = df.head(5).to_dict('records')
            
            # Calculate column statistics
            column_statistics = self._calculate_column_statistics(df)
            
            # Convert to JSON
            data_json = df.to_dict('records')
            
            return ProcessedFile(
                file_info=file_info,
                data_quality=data_quality,
                sample_rows=sample_rows,
                column_statistics=column_statistics,
                data_json=data_json
            )
            
        except Exception as e:
            logger.error(f"Error processing file {file.name}: {str(e)}")
            return None
    
    def process_files(self, files: List[Any]) -> Dict[str, ProcessedFile]:
        """Process multiple files"""
        processed_files = {}
        
        for file in files:
            processed_file = self.process_file(file)
            if processed_file:
                processed_files[file.name] = processed_file
                logger.info(f"Successfully processed: {file.name}")
                
        return processed_files
    
    def _read_csv(self, file: Any) -> Optional[pd.DataFrame]:
        """Read CSV file with encoding detection"""
        try:
            # Try UTF-8 first
            df = pd.read_csv(file, encoding='utf-8', on_bad_lines='skip')
            
            # If empty, try other encodings
            if df.empty:
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        file.seek(0)
                        df = pd.read_csv(file, encoding=encoding, on_bad_lines='skip')
                        if not df.empty:
                            break
                    except:
                        continue
                        
            return df
            
        except Exception as e:
            logger.error(f"Error reading CSV {file.name}: {str(e)}")
            return None
    
    def _read_excel(self, file: Any) -> Optional[pd.DataFrame]:
        """Read Excel file"""
        try:
            excel_file = pd.ExcelFile(file)
            # Use the first sheet
            sheet_name = excel_file.sheet_names[0]
            df = pd.read_excel(file, sheet_name=sheet_name)
            return df
            
        except Exception as e:
            logger.error(f"Error reading Excel {file.name}: {str(e)}")
            return None
    
    def _get_file_type(self, filename: str) -> str:
        """Get file type from filename"""
        if filename.endswith('.csv'):
            return 'csv'
        elif filename.endswith(('.xlsx', '.xls')):
            return 'excel'
        else:
            return 'unknown'
    
    def _calculate_data_quality(self, df: pd.DataFrame) -> DataQuality:
        """Calculate data quality metrics"""
        total_nulls = int(df.isnull().sum().sum())
        duplicate_rows = int(df.duplicated().sum())
        total_cells = len(df) * len(df.columns)
        
        completeness_score = float((1 - total_nulls / total_cells) * 100) if total_cells > 0 else 0
        uniqueness_score = float(df.nunique().sum() / total_cells * 100) if total_cells > 0 else 0
        
        return DataQuality(
            total_nulls=total_nulls,
            duplicate_rows=duplicate_rows,
            completeness_score=completeness_score,
            uniqueness_score=uniqueness_score
        )
    
    def _calculate_column_statistics(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics for each column"""
        column_stats = {}
        
        for col in df.columns:
            col_data = df[col]
            stats = {
                'type': str(col_data.dtype),
                'null_count': int(col_data.isnull().sum()),
                'null_percentage': float(col_data.isnull().sum() / len(df) * 100),
                'unique_count': int(col_data.nunique()),
                'unique_percentage': float(col_data.nunique() / len(df) * 100),
                'sample_values': self._get_sample_values(col_data),
                'statistics': self._get_column_statistics_detailed(col_data)
            }
            column_stats[col] = stats
            
        return column_stats
    
    def _get_sample_values(self, series: pd.Series) -> List[Any]:
        """Get sample values from a series"""
        non_null_values = series.dropna()
        if len(non_null_values) == 0:
            return []
        unique_values = non_null_values.unique()
        sample_size = min(5, len(unique_values))
        return unique_values[:sample_size].tolist()
    
    def _get_column_statistics_detailed(self, series: pd.Series) -> Dict[str, Any]:
        """Get detailed statistics for a column"""
        stats = {}
        
        try:
            if pd.api.types.is_numeric_dtype(series):
                stats.update({
                    'mean': float(series.mean()) if not series.empty else None,
                    'median': float(series.median()) if not series.empty else None,
                    'std': float(series.std()) if not series.empty else None,
                    'min': float(series.min()) if not series.empty else None,
                    'max': float(series.max()) if not series.empty else None,
                    'quartiles': {
                        'q1': float(series.quantile(0.25)) if not series.empty else None,
                        'q2': float(series.quantile(0.5)) if not series.empty else None,
                        'q3': float(series.quantile(0.75)) if not series.empty else None
                    }
                })
            elif pd.api.types.is_categorical_dtype(series) or series.dtype == 'object':
                value_counts = series.value_counts()
                stats.update({
                    'most_common': value_counts.head(3).to_dict() if not value_counts.empty else {},
                    'value_distribution': value_counts.head(10).to_dict() if not value_counts.empty else {}
                })
            elif pd.api.types.is_datetime64_any_dtype(series):
                stats.update({
                    'earliest': str(series.min()) if not series.empty else None,
                    'latest': str(series.max()) if not series.empty else None,
                    'date_range_days': int((series.max() - series.min()).days) if not series.empty else None
                })
        except Exception as e:
            logger.warning(f"Error calculating statistics: {str(e)}")
            stats['error'] = str(e)
        
        return stats
