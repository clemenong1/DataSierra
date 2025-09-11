from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class DataQuality:
    total_nulls: int
    duplicate_rows: int
    completeness_score: float
    uniqueness_score: float
    
    @property
    def overall_score(self) -> float:
        return (self.completeness_score + self.uniqueness_score) / 2


@dataclass
class FileInfo:
    name: str
    size: int
    type: str
    upload_time: datetime
    shape: tuple
    columns: List[str]
    dtypes: Dict[str, str]


@dataclass
class ProcessedFile:
    file_info: FileInfo
    data_quality: DataQuality
    sample_rows: List[Dict[str, Any]]
    column_statistics: Dict[str, Dict[str, Any]]
    data_json: List[Dict[str, Any]]
    
    @property
    def total_rows(self) -> int:
        return self.file_info.shape[0]
    
    @property
    def total_columns(self) -> int:
        return self.file_info.shape[1]
    
    def get_numeric_columns(self) -> List[str]:
        numeric_cols = []
        for col, stats in self.column_statistics.items():
            col_type = stats.get('type', '')
            if 'int' in col_type or 'float' in col_type:
                numeric_cols.append(col)
        return numeric_cols
    
    def get_categorical_columns(self) -> List[str]:
        categorical_cols = []
        for col, stats in self.column_statistics.items():
            col_type = stats.get('type', '')
            if col_type == 'object':
                categorical_cols.append(col)
        return categorical_cols
