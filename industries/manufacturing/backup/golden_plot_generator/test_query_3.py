"""
Test script for Query 3: Generate golden plot for evaluation.

Query 3: "In dataset train_FD002, plot operational_setting_3 vs time_in_cycles for unit_number 200"
Expected: "Only two values 100 and 60 in the plot"
"""
import sys
import os
import pandas as pd

# Add the parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from golden_plot_generator.database.connector import DatabaseConnector
from golden_plot_generator.generators.line_plot import LinePlotGenerator

def test_query_3():
    """Test golden plot generation for Query 3."""
    
    print("🎯 Testing Query 3: Golden Plot Generation")
    print("=" * 50)
    
    # Initialize components
    db = DatabaseConnector()
    plotter = LinePlotGenerator()
    
    # SQL query for Query 3
    sql_query = """
    SELECT time_in_cycles, operational_setting_3 
    FROM training_data 
    WHERE dataset = 'FD002' AND unit_number = 200
    ORDER BY time_in_cycles
    """
    
    print("📊 Executing SQL query...")
    print(f"SQL: {sql_query}")
    
    # Execute query
    data = db.execute_query(sql_query)
    
    if data is None:
        print("❌ Failed to retrieve data")
        return False
    
    print(f"✅ Retrieved {len(data)} data points")
    print(f"📈 Data preview:")
    print(data.head())
    print(f"📊 Unique operational_setting_3 values: {sorted(data['operational_setting_3'].unique())}")
    
    # Generate plot
    plot_path = plotter.create_line_plot(
        data=data,
        x_column="time_in_cycles",
        y_column="operational_setting_3", 
        title="Query 3: Operational Setting 3 vs Time (Unit 200, FD002)",
        output_filename="query_3_golden_plot"
    )
    
    if plot_path:
        print(f"🎉 Golden plot generated successfully!")
        print(f"📁 Location: {plot_path}")
        
        # Validate against expected result
        unique_values = sorted(data['operational_setting_3'].unique())
        print(f"\n🔍 Validation:")
        print(f"   Expected: Only two values 100 and 60 in the plot")
        print(f"   Actual: {unique_values}")
        
        if set(unique_values) == {60, 100}:
            print("✅ VALIDATION PASSED: Matches expected result!")
            return True
        else:
            print("❌ VALIDATION FAILED: Does not match expected result")
            return False
    else:
        print("❌ Failed to generate plot")
        return False

if __name__ == "__main__":
    success = test_query_3()
    if success:
        print("\n🎊 Query 3 golden plot generation: SUCCESS")
    else:
        print("\n💥 Query 3 golden plot generation: FAILED")
    
    sys.exit(0 if success else 1) 