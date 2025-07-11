"""
Histogram plot generator for golden plots.
Uses plotly for HTML output to match agentic framework format.
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Optional
import os
import numpy as np

class HistogramPlotGenerator:
    def __init__(self, output_dir: str = "golden_plot_generator/plots"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_histogram_plot(self, 
                             data: pd.DataFrame,
                             column: str,
                             title: str,
                             output_filename: str,
                             bins: int = 30,
                             x_axis_label: Optional[str] = None,
                             y_axis_label: Optional[str] = None) -> str:
        """
        Create a histogram plot and save as HTML.
        
        Args:
            data (pd.DataFrame): Data to plot
            column (str): Column name for histogram
            title (str): Plot title
            output_filename (str): Output file name (without extension)
            bins (int): Number of bins for histogram
            x_axis_label (str, optional): X-axis label
            y_axis_label (str, optional): Y-axis label
            
        Returns:
            str: Path to saved HTML file
        """
        try:
            if data.empty:
                print(f"Warning: No data to plot for {title}")
                return None
                
            if column not in data.columns:
                print(f"Error: Column '{column}' not found in data")
                return None
            
            # Create histogram
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=data[column],
                nbinsx=bins,
                name=column,
                marker_color='#1f77b4',
                opacity=0.7
            ))
            
            # Customize layout
            fig.update_layout(
                title=title,
                xaxis_title=x_axis_label or column,
                yaxis_title=y_axis_label or 'Frequency',
                width=800,
                height=500,
                showlegend=False,
                template="plotly_white"
            )
            
            # Save to HTML
            output_path = os.path.join(self.output_dir, f"{output_filename}.html")
            fig.write_html(output_path)
            
            print(f"✅ Histogram plot saved: {output_path}")
            print(f"   Data points: {len(data)}")
            print(f"   Column: {column}")
            print(f"   Value range: {data[column].min()} - {data[column].max()}")
            print(f"   Unique values: {sorted(data[column].unique())}")
            print(f"   Bins: {bins}")
            
            return output_path
            
        except Exception as e:
            print(f"Error creating histogram plot: {e}")
            return None

    def create_distribution_plot(self, 
                                data: pd.DataFrame,
                                column: str,
                                title: str,
                                output_filename: str,
                                auto_bins: bool = True) -> str:
        """
        Create a distribution plot with automatic bin sizing.
        
        Args:
            data (pd.DataFrame): Data to plot
            column (str): Column name for distribution
            title (str): Plot title
            output_filename (str): Output file name (without extension)
            auto_bins (bool): Whether to automatically determine bin count
            
        Returns:
            str: Path to saved HTML file
        """
        try:
            if data.empty:
                print(f"Warning: No data to plot for {title}")
                return None
                
            if column not in data.columns:
                print(f"Error: Column '{column}' not found in data")
                return None
            
            # Determine optimal bin count
            unique_values = data[column].nunique()
            
            if unique_values <= 20:
                # For small number of unique values, use one bin per value
                bins = unique_values
                print(f"Using {bins} bins for {unique_values} unique values")
            else:
                # For many unique values, use Sturges' rule
                bins = int(np.ceil(np.log2(len(data))) + 1)
                print(f"Using {bins} bins (Sturges' rule) for {unique_values} unique values")
            
            return self.create_histogram_plot(
                data=data,
                column=column,
                title=title,
                output_filename=output_filename,
                bins=bins
            )
            
        except Exception as e:
            print(f"Error creating distribution plot: {e}")
            return None 