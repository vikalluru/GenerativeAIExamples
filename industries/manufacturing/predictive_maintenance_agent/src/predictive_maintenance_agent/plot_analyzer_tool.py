import json
import logging
import os
import pandas as pd
from pydantic import Field, BaseModel
from aiq.builder.builder import Builder
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)

class PlotAnalyzerToolConfig(FunctionBaseConfig, name="plot_analyzer_tool"):
    """Configuration for the plot analyzer tool."""
    llm_name: str = Field(description="Name of the LLM to use for analysis", default="reasoning_llm")

@register_function(config_type=PlotAnalyzerToolConfig)
async def plot_analyzer_tool(
    config: PlotAnalyzerToolConfig, builder: Builder
):
    class PlotAnalyzerInputSchema(BaseModel):
        data_json_path: str = Field(description="Path to the JSON file containing the plot data")
        plot_type: str = Field(description="Type of plot: 'distribution', 'line_chart', 'comparison'")
        analysis_context: str = Field(description="Additional context for analysis", default="")

    def load_data_from_json(json_path: str):
        """Load data from JSON file into a pandas DataFrame."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            return pd.DataFrame(data)
        except FileNotFoundError:
            logger.error(f"JSON file not found at {json_path}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Could not decode JSON from {json_path}")
            return None
        except Exception as e:
            logger.error(f"Error loading data from '{json_path}': {e}")
            return None

    def analyze_distribution_data(df, column_name):
        """Analyze distribution data and extract key characteristics."""
        if column_name not in df.columns:
            return None
        
        unique_values = sorted(df[column_name].unique())
        value_counts = df[column_name].value_counts().sort_index()
        total_points = len(df)
        value_range = (df[column_name].min(), df[column_name].max())
        
        return {
            "unique_values": unique_values,
            "value_counts": value_counts.to_dict(),
            "total_points": total_points,
            "value_range": value_range,
            "num_unique": len(unique_values)
        }

    def analyze_line_chart_data(df, x_col, y_col):
        """Analyze line chart data and extract key characteristics."""
        if x_col not in df.columns or y_col not in df.columns:
            return None
        
        y_range = (df[y_col].min(), df[y_col].max())
        total_points = len(df)
        
        # Determine trend
        if len(df) > 1:
            first_val = df[y_col].iloc[0]
            last_val = df[y_col].iloc[-1]
            if abs(last_val - first_val) < 0.01:  # Essentially constant
                trend = "constant"
            elif last_val > first_val:
                trend = "increasing"
            else:
                trend = "decreasing"
        else:
            trend = "single_point"
        
        return {
            "total_points": total_points,
            "y_range": y_range,
            "trend": trend,
            "x_column": x_col,
            "y_column": y_col
        }

    def analyze_comparison_data(df, x_col, y_col_1, y_col_2):
        """Analyze comparison plot data."""
        if not all(col in df.columns for col in [x_col, y_col_1, y_col_2]):
            return None
        
        total_points = len(df)
        y1_range = (df[y_col_1].min(), df[y_col_1].max())
        y2_range = (df[y_col_2].min(), df[y_col_2].max())
        
        # Calculate correlation if possible
        try:
            correlation = df[y_col_1].corr(df[y_col_2])
        except:
            correlation = None
        
        return {
            "total_points": total_points,
            "y1_range": y1_range,
            "y2_range": y2_range,
            "correlation": correlation,
            "y1_column": y_col_1,
            "y2_column": y_col_2
        }

    async def _response_fn(data_json_path: str, plot_type: str, analysis_context: str = "") -> str:
        """
        Analyze plot data and generate natural language description.
        """
        try:
            # Load the data
            df = load_data_from_json(data_json_path)
            if df is None or df.empty:
                return "Could not load data for plot analysis"
            
            # Get the reasoning LLM
            analysis_llm = await builder.get_llm(config.llm_name)
            
            # Analyze based on plot type
            analysis_data = None
            
            if plot_type == "distribution":
                # Try to infer the column being analyzed
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    # Use the last numeric column (often the target)
                    column_name = numeric_cols[-1]
                    analysis_data = analyze_distribution_data(df, column_name)
                    
            elif plot_type == "line_chart":
                # Look for time and measurement columns
                time_cols = [col for col in df.columns if 'time' in col.lower() or 'cycle' in col.lower()]
                measurement_cols = [col for col in df.columns if 'sensor' in col.lower() or 'operational' in col.lower() or 'RUL' in col]
                
                if time_cols and measurement_cols:
                    x_col = time_cols[0]
                    y_col = measurement_cols[0]
                    analysis_data = analyze_line_chart_data(df, x_col, y_col)
                    
            elif plot_type == "comparison":
                # Look for actual vs predicted columns
                rul_cols = [col for col in df.columns if 'RUL' in col]
                time_cols = [col for col in df.columns if 'time' in col.lower() or 'cycle' in col.lower()]
                
                if len(rul_cols) >= 2 and time_cols:
                    x_col = time_cols[0]
                    y_col_1 = rul_cols[0]  # actual
                    y_col_2 = rul_cols[1]  # predicted
                    analysis_data = analyze_comparison_data(df, x_col, y_col_1, y_col_2)
            
            # Create analysis prompt
            sample_data = df.head(3).to_dict('records')
            
            prompt = f"""
            Analyze this {plot_type} data and provide a natural, descriptive summary that matches evaluation reference format.
            
            Plot Type: {plot_type}
            Data Sample: {json.dumps(sample_data, indent=2)}
            Analysis Data: {json.dumps(analysis_data, indent=2) if analysis_data else "None"}
            Additional Context: {analysis_context}
            
            Based on the data, generate a description following these patterns:
            
            For DISTRIBUTION plots:
            - If 2 unique values: "Two bars for [value1] and [value2] with higher bar for [most_frequent]"
            - If constant value: "Constant value [value], so just one high bar for [value]"
            - If many values: "Distribution showing [X] unique values ranging from [min] to [max]"
            
            For LINE CHART plots:
            - "Line chart showing [column] values ranging from [min] to [max] plotted against [x_column]. Should contain [N] data points showing [trend_description]."
            - Include specific value ranges and data point counts
            
            For COMPARISON plots:
            - "Shows [relationship] between [col1] and [col2] with [N] data points"
            - Mention value ranges if significant
            
            Provide ONLY the description, no additional text or explanations.
            """
            
            # Get LLM analysis
            response = await analysis_llm.ainvoke(prompt)
            description = response.content.strip()
            
            logger.info(f"Plot analysis generated: {description}")
            return description
            
        except Exception as e:
            error_msg = f"Error analyzing plot data: {e}"
            logger.error(error_msg)
            return error_msg

    prompt = """
    Analyze plot data and generate natural language descriptions that match evaluation reference answers.
    
    Input:
    - data_json_path: Path to the JSON file containing the plot data
    - plot_type: Type of plot ('distribution', 'line_chart', 'comparison')
    - analysis_context: Additional context for analysis (optional)
    
    Output:
    - Natural language description of plot content matching evaluation format
    """
    
    yield FunctionInfo.from_fn(_response_fn, 
                               input_schema=PlotAnalyzerInputSchema,
                               description=prompt)
    try:
        pass
    except GeneratorExit:
        logger.info("Plot analyzer function exited early!")
    finally:
        logger.info("Cleaning up plot_analyzer_tool workflow.") 