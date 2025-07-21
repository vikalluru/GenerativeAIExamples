"""
Line plot generator for golden plots.
Uses plotly for HTML output to match agentic framework format.
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Optional
import os

class LinePlotGenerator:
    def __init__(self, output_dir: str = "golden_plot_generator/plots"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_line_plot(self, 
                        data: pd.DataFrame,
                        x_column: str,
                        y_column: str,
                        title: str,
                        output_filename: str,
                        unit_column: Optional[str] = None) -> str:
        """
        Create a line plot and save as HTML.
        
        Args:
            data (pd.DataFrame): Data to plot
            x_column (str): Column name for x-axis
            y_column (str): Column name for y-axis  
            title (str): Plot title
            output_filename (str): Output file name (without extension)
            unit_column (str, optional): Column to group by units for multi-line plots
            
        Returns:
            str: Path to saved HTML file
        """
        try:
            if data.empty:
                print(f"Warning: No data to plot for {title}")
                return None
                
            # Create the plot
            if unit_column and unit_column in data.columns:
                # Multi-line plot (one line per unit)
                fig = px.line(data, x=x_column, y=y_column, color=unit_column, 
                             title=title, markers=True)
            else:
                # Single line plot
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data[x_column],
                    y=data[y_column],
                    mode='lines+markers',
                    name=y_column,
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
                fig.update_layout(title=title)
            
            # Customize layout
            fig.update_layout(
                xaxis_title=x_column,
                yaxis_title=y_column,
                width=800,
                height=500,
                showlegend=True if unit_column else False,
                template="plotly_white"
            )
            
            # Save to HTML
            output_path = os.path.join(self.output_dir, f"{output_filename}.html")
            fig.write_html(output_path)
            
            print(f"✅ Line plot saved: {output_path}")
            print(f"   Data points: {len(data)}")
            print(f"   X range: {data[x_column].min()} - {data[x_column].max()}")
            print(f"   Y range: {data[y_column].min()} - {data[y_column].max()}")
            print(f"   Unique Y values: {sorted(data[y_column].unique())}")
            
            return output_path
            
        except Exception as e:
            print(f"Error creating line plot: {e}")
            return None 