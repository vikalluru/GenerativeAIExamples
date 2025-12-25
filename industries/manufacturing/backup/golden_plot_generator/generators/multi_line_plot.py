"""
Multi-line plot generator for golden plots.
Uses plotly for HTML output to match agentic framework format.
Specialized for plotting multiple units on the same chart.
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Optional
import os

class MultiLinePlotGenerator:
    def __init__(self, output_dir: str = "golden_plot_generator/plots"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_multi_line_plot(self, 
                              data: pd.DataFrame,
                              x_column: str,
                              y_column: str,
                              group_column: str,
                              title: str,
                              output_filename: str,
                              specific_groups: Optional[List] = None) -> str:
        """
        Create a multi-line plot with each group as a separate line.
        
        Args:
            data (pd.DataFrame): Data to plot
            x_column (str): Column name for x-axis
            y_column (str): Column name for y-axis
            group_column (str): Column name for grouping (e.g., unit_number)
            title (str): Plot title
            output_filename (str): Output file name (without extension)
            specific_groups (List, optional): Specific groups to include
            
        Returns:
            str: Path to saved HTML file
        """
        try:
            if data.empty:
                print(f"Warning: No data to plot for {title}")
                return None
                
            # Check required columns
            required_columns = [x_column, y_column, group_column]
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                print(f"Error: Missing columns: {missing_columns}")
                return None
            
            # Filter for specific groups if provided
            if specific_groups:
                data = data[data[group_column].isin(specific_groups)]
                if data.empty:
                    print(f"Warning: No data found for groups: {specific_groups}")
                    return None
            
            # Sort data by group and x-axis for proper line plotting
            data = data.sort_values([group_column, x_column])
            
            # Create multi-line plot using plotly express
            fig = px.line(
                data, 
                x=x_column, 
                y=y_column, 
                color=group_column,
                title=title,
                markers=True,
                line_shape='linear'
            )
            
            # Customize layout
            fig.update_layout(
                xaxis_title=x_column,
                yaxis_title=y_column,
                width=800,
                height=500,
                showlegend=True,
                template="plotly_white",
                legend=dict(
                    title=group_column,
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02
                )
            )
            
            # Add hover information
            fig.update_traces(
                hovertemplate=f"<b>{group_column}:</b> %{{legendgroup}}<br>"
                             f"<b>{x_column}:</b> %{{x}}<br>"
                             f"<b>{y_column}:</b> %{{y}}<br>"
                             "<extra></extra>"
            )
            
            # Save to HTML
            output_path = os.path.join(self.output_dir, f"{output_filename}.html")
            fig.write_html(output_path)
            
            # Print summary
            groups = data[group_column].unique()
            print(f"✅ Multi-line plot saved: {output_path}")
            print(f"   Data points: {len(data)}")
            print(f"   Groups ({group_column}): {sorted(groups)}")
            print(f"   X range: {data[x_column].min()} - {data[x_column].max()}")
            print(f"   Y range: {data[y_column].min()} - {data[y_column].max()}")
            print(f"   Unique Y values: {sorted(data[y_column].unique())}")
            
            return output_path
            
        except Exception as e:
            print(f"Error creating multi-line plot: {e}")
            return None

    def create_constant_line_plot(self, 
                                 data: pd.DataFrame,
                                 x_column: str,
                                 y_column: str,
                                 group_column: str,
                                 title: str,
                                 output_filename: str,
                                 specific_groups: Optional[List] = None) -> str:
        """
        Create a multi-line plot optimized for constant values.
        
        Args:
            data (pd.DataFrame): Data to plot
            x_column (str): Column name for x-axis
            y_column (str): Column name for y-axis (constant values)
            group_column (str): Column name for grouping
            title (str): Plot title
            output_filename (str): Output file name (without extension)
            specific_groups (List, optional): Specific groups to include
            
        Returns:
            str: Path to saved HTML file
        """
        try:
            result = self.create_multi_line_plot(
                data=data,
                x_column=x_column,
                y_column=y_column,
                group_column=group_column,
                title=title,
                output_filename=output_filename,
                specific_groups=specific_groups
            )
            
            if result:
                # Check if all lines are constant
                if specific_groups:
                    check_data = data[data[group_column].isin(specific_groups)]
                else:
                    check_data = data
                
                unique_y_values = check_data[y_column].unique()
                if len(unique_y_values) == 1:
                    print(f"   📊 All lines are constant at value: {unique_y_values[0]}")
                else:
                    print(f"   📊 Lines have different values: {sorted(unique_y_values)}")
            
            return result
            
        except Exception as e:
            print(f"Error creating constant line plot: {e}")
            return None 