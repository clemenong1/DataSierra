import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
import io
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import os

try:
    from lida import Manager, TextGenerationConfig, llm
    LIDA_AVAILABLE = True
except ImportError as e:
    LIDA_AVAILABLE = False
    LIDA_IMPORT_ERROR = str(e)
except Exception as e:
    LIDA_AVAILABLE = False
    LIDA_IMPORT_ERROR = str(e)

# Fallback for Python 3.8 - create a simple visualization service
if not LIDA_AVAILABLE:
    print("LIDA not available, using fallback visualization service")

from ..config import Config


class LidaVisualizationService:
    
    def __init__(self):
        self.lida_manager = None
        self._initialize_lida()
    
    def _initialize_lida(self):
        if not LIDA_AVAILABLE:
            return
        
        try:
            openai_api_key = Config.get_openai_api_key()
            if openai_api_key:
                text_gen_config = TextGenerationConfig(
                    model="gpt-4o",
                    api_key=openai_api_key
                )
                self.lida_manager = Manager(text_gen=llm("openai", api_key=openai_api_key))
        except Exception as e:
            pass
    
    def is_available(self) -> bool:
        if not LIDA_AVAILABLE:
            return False
        if self.lida_manager is None:
            return False
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed status information for debugging"""
        status = {
            'lida_available': LIDA_AVAILABLE,
            'lida_manager_initialized': self.lida_manager is not None,
            'openai_api_key_available': Config.get_openai_api_key() is not None,
            'overall_available': self.is_available()
        }
        
        if not LIDA_AVAILABLE:
            status['lida_import_error'] = LIDA_IMPORT_ERROR if 'LIDA_IMPORT_ERROR' in globals() else "Unknown import error"
        
        return status
    
    def generate_visualization_from_prompt(self, dataframes: Dict[str, pd.DataFrame], user_prompt: str) -> Dict[str, Any]:
        if not self.is_available():
            if dataframes:
                df_name, df = next(iter(dataframes.items()))
                fallback_code = self._generate_fallback_code(df, user_prompt)
                return {
                    "success": True,
                    "charts": [{
                        "title": f"Fallback Visualization for: {user_prompt}",
                        "description": f"Generated based on your request: {user_prompt}",
                        "code": fallback_code,
                        "library": "plotly"
                    }],
                    "method": "fallback"
                }
            return {"success": False, "error": "No dataframes provided"}
        
        try:
            if not dataframes:
                return {"success": False, "error": "No dataframes provided"}
            
            df_name, df = next(iter(dataframes.items()))
            
            summary = self.lida_manager.summarize(df)
            
            goals = self.lida_manager.goals(summary, n=1, textgen_config=TextGenerationConfig(
                n=1,
                temperature=0.1,
                model="gpt-4o",
                use_cache=True
            ))
            
            if not goals:
                return {"success": False, "error": "Could not generate visualization goals"}
            
            goal = goals[0]
            goal.question = user_prompt
            
            charts = self.lida_manager.visualize(
                summary=summary,
                goal=goal,
                textgen_config=TextGenerationConfig(
                    n=1,
                    temperature=0.1,
                    model="gpt-4o",
                    use_cache=True
                ),
                library="plotly"
            )
            
            processed_charts = []
            for chart in charts:
                processed_charts.append({
                    "title": getattr(chart, 'title', 'Generated Chart'),
                    "description": getattr(chart, 'description', user_prompt),
                    "code": getattr(chart, 'code', ''),
                    "library": "plotly"
                })
            
            return {
                "success": True,
                "charts": processed_charts,
                "method": "lida"
            }
            
        except Exception as e:
            if dataframes:
                df_name, df = next(iter(dataframes.items()))
                fallback_code = self._generate_fallback_code(df, user_prompt)
                return {
                    "success": True,
                    "charts": [{
                        "title": f"Fallback Visualization for: {user_prompt}",
                        "description": f"Generated based on your request: {user_prompt}",
                        "code": fallback_code,
                        "library": "plotly"
                    }],
                    "method": "fallback",
                    "error": f"LIDA failed, using fallback: {str(e)}"
                }
            return {
                "success": False,
                "error": f"LIDA visualization failed: {str(e)}"
            }

    def generate_visualizations(self, data: pd.DataFrame, insights_context: str = "", num_visualizations: int = 5) -> List[Dict[str, Any]]:
        if not self.is_available():
            return self._generate_fallback_visualizations(data)
        
        try:
            summary = self.lida_manager.summarize(data)
            goals = self.lida_manager.goals(summary, n=num_visualizations)
            
            visualizations = []
            for i, goal in enumerate(goals):
                try:
                    chart = self.lida_manager.visualize(
                        summary=summary, 
                        goal=goal, 
                        library="plotly"
                    )
                    
                    if chart and hasattr(chart, 'figure'):
                        fig = chart.figure
                        chart_html = fig.to_html(include_plotlyjs=False)
                        
                        visualizations.append({
                            'id': f"lida_chart_{i}",
                            'title': goal.question if hasattr(goal, 'question') else f"Visualization {i+1}",
                            'description': goal.rationale if hasattr(goal, 'rationale') else "",
                            'html': chart_html,
                            'type': 'lida_generated',
                            'goal': goal
                        })
                except Exception as e:
                    continue
            
            return visualizations
            
        except Exception as e:
            return self._generate_fallback_visualizations(data)
    
    def _generate_fallback_visualizations(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        visualizations = []
        
        try:
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
            
            # Generate more comprehensive visualizations
            if len(numeric_cols) >= 2:
                # Scatter plot
                fig = px.scatter(data, x=numeric_cols[0], y=numeric_cols[1], 
                               title=f"Scatter Plot: {numeric_cols[0]} vs {numeric_cols[1]}",
                               labels={numeric_cols[0]: numeric_cols[0], numeric_cols[1]: numeric_cols[1]})
                visualizations.append({
                    'id': 'scatter_plot',
                    'title': f"Scatter Plot: {numeric_cols[0]} vs {numeric_cols[1]}",
                    'description': f"Shows the relationship between {numeric_cols[0]} and {numeric_cols[1]}. Each point represents a data observation.",
                    'html': fig.to_html(include_plotlyjs=False),
                    'type': 'fallback'
                })
            
            if len(numeric_cols) >= 1:
                # Histogram
                fig = px.histogram(data, x=numeric_cols[0], 
                                 title=f"Distribution of {numeric_cols[0]}",
                                 labels={numeric_cols[0]: numeric_cols[0], 'count': 'Frequency'})
                visualizations.append({
                    'id': 'histogram',
                    'title': f"Distribution of {numeric_cols[0]}",
                    'description': f"Shows the frequency distribution of {numeric_cols[0]}. Helps identify patterns, outliers, and data spread.",
                    'html': fig.to_html(include_plotlyjs=False),
                    'type': 'fallback'
                })
            
            if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                # Box plot
                fig = px.box(data, x=categorical_cols[0], y=numeric_cols[0],
                           title=f"Box Plot: {numeric_cols[0]} by {categorical_cols[0]}",
                           labels={categorical_cols[0]: categorical_cols[0], numeric_cols[0]: numeric_cols[0]})
                visualizations.append({
                    'id': 'box_plot',
                    'title': f"Box Plot: {numeric_cols[0]} by {categorical_cols[0]}",
                    'description': f"Shows the distribution of {numeric_cols[0]} across different {categorical_cols[0]} categories. Displays median, quartiles, and outliers.",
                    'html': fig.to_html(include_plotlyjs=False),
                    'type': 'fallback'
                })
            
            if len(numeric_cols) >= 3:
                # Correlation matrix
                fig = px.scatter_matrix(data[numeric_cols[:4]], 
                                      title="Correlation Matrix",
                                      labels={col: col for col in numeric_cols[:4]})
                visualizations.append({
                    'id': 'correlation_matrix',
                    'title': "Correlation Matrix",
                    'description': "Shows relationships between all numeric variables. Helps identify correlations and patterns in the data.",
                    'html': fig.to_html(include_plotlyjs=False),
                    'type': 'fallback'
                })
            
            # Add bar chart for categorical data
            if len(categorical_cols) >= 1:
                value_counts = data[categorical_cols[0]].value_counts().head(10)
                fig = px.bar(x=value_counts.index, y=value_counts.values,
                           title=f"Top 10 {categorical_cols[0]} Categories",
                           labels={'x': categorical_cols[0], 'y': 'Count'})
                visualizations.append({
                    'id': 'bar_chart',
                    'title': f"Top 10 {categorical_cols[0]} Categories",
                    'description': f"Shows the frequency of different {categorical_cols[0]} categories in your dataset.",
                    'html': fig.to_html(include_plotlyjs=False),
                    'type': 'fallback'
                })
            
            # Add line plot if we have a time-like column
            if len(numeric_cols) >= 2:
                fig = px.line(data, x=numeric_cols[0], y=numeric_cols[1],
                            title=f"Line Chart: {numeric_cols[1]} over {numeric_cols[0]}",
                            labels={numeric_cols[0]: numeric_cols[0], numeric_cols[1]: numeric_cols[1]})
                visualizations.append({
                    'id': 'line_chart',
                    'title': f"Line Chart: {numeric_cols[1]} over {numeric_cols[0]}",
                    'description': f"Shows how {numeric_cols[1]} changes with {numeric_cols[0]}. Useful for identifying trends and patterns.",
                    'html': fig.to_html(include_plotlyjs=False),
                    'type': 'fallback'
                })
            
        except Exception as e:
            print(f"Error generating fallback visualizations: {e}")
        
        return visualizations
    
    def _generate_fallback_code(self, data: pd.DataFrame, user_prompt: str) -> str:
        """Generate fallback visualization code based on user prompt and data"""
        try:
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
            
            # Simple keyword-based fallback
            prompt_lower = user_prompt.lower()
            
            if 'bar' in prompt_lower and categorical_cols and numeric_cols:
                col1 = categorical_cols[0]
                col2 = numeric_cols[0] if len(numeric_cols) > 0 else categorical_cols[0]
                return f"""
import plotly.express as px
fig = px.bar(data, x='{col1}', y='{col2}', title='Bar Chart: {col2} by {col1}')
fig.show()
"""
            
            elif 'scatter' in prompt_lower and len(numeric_cols) >= 2:
                col1, col2 = numeric_cols[0], numeric_cols[1]
                return f"""
import plotly.express as px
fig = px.scatter(data, x='{col1}', y='{col2}', title='Scatter Plot: {col1} vs {col2}')
fig.show()
"""
            
            elif 'histogram' in prompt_lower and numeric_cols:
                col = numeric_cols[0]
                return f"""
import plotly.express as px
fig = px.histogram(data, x='{col}', title='Distribution of {col}')
fig.show()
"""
            
            elif 'box' in prompt_lower and categorical_cols and numeric_cols:
                cat_col = categorical_cols[0]
                num_col = numeric_cols[0]
                return f"""
import plotly.express as px
fig = px.box(data, x='{cat_col}', y='{num_col}', title='Box Plot: {num_col} by {cat_col}')
fig.show()
"""
            
            else:
                # Default to a simple bar chart
                if categorical_cols and numeric_cols:
                    col1 = categorical_cols[0]
                    col2 = numeric_cols[0]
                    return f"""
import plotly.express as px
fig = px.bar(data, x='{col1}', y='{col2}', title='Bar Chart: {col2} by {col1}')
fig.show()
"""
                elif numeric_cols:
                    col = numeric_cols[0]
                    return f"""
import plotly.express as px
fig = px.histogram(data, x='{col}', title='Distribution of {col}')
fig.show()
"""
                else:
                    return """
import plotly.express as px
fig = px.bar(data, x=data.columns[0], title='Data Overview')
fig.show()
"""
                    
        except Exception as e:
            return f"""
import plotly.express as px
fig = px.bar(data, x=data.columns[0], title='Data Overview')
fig.show()
"""
    
    def generate_custom_visualization(self, data: pd.DataFrame, chart_type: str, 
                                    x_col: str = None, y_col: str = None, 
                                    color_col: str = None) -> Optional[Dict[str, Any]]:
        try:
            if chart_type == "scatter" and x_col and y_col:
                fig = px.scatter(data, x=x_col, y=y_col, color=color_col,
                               title=f"Scatter Plot: {x_col} vs {y_col}")
            elif chart_type == "line" and x_col and y_col:
                fig = px.line(data, x=x_col, y=y_col, color=color_col,
                            title=f"Line Chart: {y_col} over {x_col}")
            elif chart_type == "bar" and x_col and y_col:
                fig = px.bar(data, x=x_col, y=y_col, color=color_col,
                           title=f"Bar Chart: {y_col} by {x_col}")
            elif chart_type == "histogram" and x_col:
                fig = px.histogram(data, x=x_col, color=color_col,
                                 title=f"Distribution of {x_col}")
            elif chart_type == "box" and x_col and y_col:
                fig = px.box(data, x=x_col, y=y_col, color=color_col,
                           title=f"Box Plot: {y_col} by {x_col}")
            else:
                return None
            
            return {
                'id': f'custom_{chart_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'title': fig.layout.title.text,
                'description': f"Custom {chart_type} visualization",
                'html': fig.to_html(include_plotlyjs=False),
                'type': 'custom'
            }
            
        except Exception as e:
            return None
    
    def get_data_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        try:
            summary = {
                'shape': data.shape,
                'columns': list(data.columns),
                'dtypes': data.dtypes.to_dict(),
                'numeric_columns': data.select_dtypes(include=['number']).columns.tolist(),
                'categorical_columns': data.select_dtypes(include=['object', 'category']).columns.tolist(),
                'missing_values': data.isnull().sum().to_dict(),
                'basic_stats': data.describe().to_dict() if len(data.select_dtypes(include=['number']).columns) > 0 else {}
            }
            return summary
        except Exception as e:
            return {}
    
    def export_visualization(self, visualization: Dict[str, Any], format: str = "html") -> str:
        if format == "html":
            return visualization.get('html', '')
        elif format == "json":
            return str(visualization)
        else:
            return ""
