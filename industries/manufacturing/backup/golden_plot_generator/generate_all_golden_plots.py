"""
Generate all golden plots for evaluation.
This script creates reference plots for all 7 queries in eval_set_plots.json.
"""
import sys
import os
import pandas as pd
import json
from pathlib import Path

# Add the parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from golden_plot_generator.database.connector import DatabaseConnector
from golden_plot_generator.generators.line_plot import LinePlotGenerator
from golden_plot_generator.generators.histogram_plot import HistogramPlotGenerator
from golden_plot_generator.generators.multi_line_plot import MultiLinePlotGenerator

class GoldenPlotGenerator:
    def __init__(self):
        self.db = DatabaseConnector()
        self.line_plotter = LinePlotGenerator()
        self.histogram_plotter = HistogramPlotGenerator()
        self.multi_line_plotter = MultiLinePlotGenerator()
        self.results = []
        
    def test_query_1(self):
        """Query 1: In dataset train_FD004, plot sensor_measurement1 vs time_in_cycles for unit_number 107"""
        print("🎯 Testing Query 1: sensor_measurement1 vs time_in_cycles (Unit 107, FD004)")
        print("=" * 70)
        
        sql_query = """
        SELECT time_in_cycles, sensor_measurement_1 
        FROM training_data 
        WHERE dataset = 'FD004' AND unit_number = 107
        ORDER BY time_in_cycles
        """
        
        data = self.db.execute_query(sql_query)
        if data is None or data.empty:
            print("❌ No data retrieved")
            return False
        
        print(f"✅ Retrieved {len(data)} data points")
        print(f"📈 Sensor measurement range: {data['sensor_measurement_1'].min():.2f} - {data['sensor_measurement_1'].max():.2f}")
        
        plot_path = self.line_plotter.create_line_plot(
            data=data,
            x_column="time_in_cycles",
            y_column="sensor_measurement_1",
            title="Query 1: Sensor Measurement 1 vs Time (Unit 107, FD004)",
            output_filename="query_1_golden_plot"
        )
        
        if plot_path:
            self.results.append({
                "query": 1,
                "status": "SUCCESS",
                "plot_path": plot_path,
                "data_points": len(data),
                "value_range": f"{data['sensor_measurement_1'].min():.2f} - {data['sensor_measurement_1'].max():.2f}"
            })
            return True
        return False
    
    def test_query_2(self):
        """Query 2: In dataset train_FD004, plot the variation of sensor_measurement1 over time for unit_number 107"""
        print("🎯 Testing Query 2: sensor_measurement1 variation over time (Unit 107, FD004)")
        print("=" * 70)
        
        # Same as query 1 but with different title
        sql_query = """
        SELECT time_in_cycles, sensor_measurement_1 
        FROM training_data 
        WHERE dataset = 'FD004' AND unit_number = 107
        ORDER BY time_in_cycles
        """
        
        data = self.db.execute_query(sql_query)
        if data is None or data.empty:
            print("❌ No data retrieved")
            return False
        
        print(f"✅ Retrieved {len(data)} data points")
        print(f"📈 Sensor measurement variation: {data['sensor_measurement_1'].min():.2f} - {data['sensor_measurement_1'].max():.2f}")
        
        plot_path = self.line_plotter.create_line_plot(
            data=data,
            x_column="time_in_cycles",
            y_column="sensor_measurement_1",
            title="Query 2: Sensor Measurement 1 Variation Over Time (Unit 107, FD004)",
            output_filename="query_2_golden_plot"
        )
        
        if plot_path:
            self.results.append({
                "query": 2,
                "status": "SUCCESS",
                "plot_path": plot_path,
                "data_points": len(data),
                "value_range": f"{data['sensor_measurement_1'].min():.2f} - {data['sensor_measurement_1'].max():.2f}"
            })
            return True
        return False
    
    def test_query_3(self):
        """Query 3: In dataset train_FD002, plot operational_setting_3 vs time_in_cycles for unit_number 200"""
        print("🎯 Testing Query 3: operational_setting_3 vs time_in_cycles (Unit 200, FD002)")
        print("=" * 70)
        
        sql_query = """
        SELECT time_in_cycles, operational_setting_3 
        FROM training_data 
        WHERE dataset = 'FD002' AND unit_number = 200
        ORDER BY time_in_cycles
        """
        
        data = self.db.execute_query(sql_query)
        if data is None or data.empty:
            print("❌ No data retrieved")
            return False
        
        print(f"✅ Retrieved {len(data)} data points")
        print(f"📊 Unique operational_setting_3 values: {sorted(data['operational_setting_3'].unique())}")
        
        plot_path = self.line_plotter.create_line_plot(
            data=data,
            x_column="time_in_cycles",
            y_column="operational_setting_3",
            title="Query 3: Operational Setting 3 vs Time (Unit 200, FD002)",
            output_filename="query_3_golden_plot"
        )
        
        if plot_path:
            unique_values = sorted(data['operational_setting_3'].unique())
            validation_passed = set(unique_values) == {60.0, 100.0}
            
            self.results.append({
                "query": 3,
                "status": "SUCCESS",
                "plot_path": plot_path,
                "data_points": len(data),
                "unique_values": unique_values,
                "validation": "PASSED" if validation_passed else "FAILED"
            })
            
            if validation_passed:
                print("✅ VALIDATION PASSED: Only two values 100 and 60 in the plot")
            else:
                print(f"❌ VALIDATION FAILED: Expected [60.0, 100.0], got {unique_values}")
                
            return True
        return False
    
    def test_query_4(self):
        """Query 4: Plot a histogram showing distribution of values of operational_setting_3 over time for unit_number 200 in dataset train_FD002"""
        print("🎯 Testing Query 4: Histogram of operational_setting_3 (Unit 200, FD002)")
        print("=" * 70)
        
        sql_query = """
        SELECT operational_setting_3 
        FROM training_data 
        WHERE dataset = 'FD002' AND unit_number = 200
        """
        
        data = self.db.execute_query(sql_query)
        if data is None or data.empty:
            print("❌ No data retrieved")
            return False
        
        print(f"✅ Retrieved {len(data)} data points")
        print(f"📊 Unique values: {sorted(data['operational_setting_3'].unique())}")
        
        plot_path = self.histogram_plotter.create_distribution_plot(
            data=data,
            column="operational_setting_3",
            title="Query 4: Distribution of Operational Setting 3 (Unit 200, FD002)",
            output_filename="query_4_golden_plot"
        )
        
        if plot_path:
            unique_values = sorted(data['operational_setting_3'].unique())
            value_counts = data['operational_setting_3'].value_counts().sort_index()
            
            self.results.append({
                "query": 4,
                "status": "SUCCESS",
                "plot_path": plot_path,
                "data_points": len(data),
                "unique_values": unique_values,
                "value_counts": value_counts.to_dict()
            })
            
            print(f"📊 Value distribution: {value_counts.to_dict()}")
            return True
        return False
    
    def test_query_5(self):
        """Query 5: In dataset test_FD001 plot a histogram showing the distribution of operational_setting_3 across all units"""
        print("🎯 Testing Query 5: Histogram of operational_setting_3 across all units (test_FD001)")
        print("=" * 70)
        
        sql_query = """
        SELECT operational_setting_3 
        FROM test_data 
        WHERE dataset = 'FD001'
        """
        
        data = self.db.execute_query(sql_query)
        if data is None or data.empty:
            print("❌ No data retrieved")
            return False
        
        print(f"✅ Retrieved {len(data)} data points")
        print(f"📊 Unique values: {sorted(data['operational_setting_3'].unique())}")
        
        plot_path = self.histogram_plotter.create_distribution_plot(
            data=data,
            column="operational_setting_3",
            title="Query 5: Distribution of Operational Setting 3 (All Units, test_FD001)",
            output_filename="query_5_golden_plot"
        )
        
        if plot_path:
            unique_values = sorted(data['operational_setting_3'].unique())
            value_counts = data['operational_setting_3'].value_counts().sort_index()
            
            self.results.append({
                "query": 5,
                "status": "SUCCESS",
                "plot_path": plot_path,
                "data_points": len(data),
                "unique_values": unique_values,
                "value_counts": value_counts.to_dict()
            })
            
            print(f"📊 Value distribution: {value_counts.to_dict()}")
            return True
        return False
    
    def test_query_6(self):
        """Query 6: In dataset test_FD001 plot operational_setting_3 as a function of time_in_cycles for units 10, 20, 30, 40"""
        print("🎯 Testing Query 6: Multi-line plot operational_setting_3 vs time (Units 10,20,30,40, test_FD001)")
        print("=" * 70)
        
        sql_query = """
        SELECT time_in_cycles, operational_setting_3, unit_number 
        FROM test_data 
        WHERE dataset = 'FD001' AND unit_number IN (10, 20, 30, 40)
        ORDER BY unit_number, time_in_cycles
        """
        
        data = self.db.execute_query(sql_query)
        if data is None or data.empty:
            print("❌ No data retrieved")
            return False
        
        print(f"✅ Retrieved {len(data)} data points")
        print(f"📊 Units found: {sorted(data['unit_number'].unique())}")
        print(f"📊 Unique operational_setting_3 values: {sorted(data['operational_setting_3'].unique())}")
        
        plot_path = self.multi_line_plotter.create_constant_line_plot(
            data=data,
            x_column="time_in_cycles",
            y_column="operational_setting_3",
            group_column="unit_number",
            title="Query 6: Operational Setting 3 vs Time (Units 10,20,30,40, test_FD001)",
            output_filename="query_6_golden_plot",
            specific_groups=[10, 20, 30, 40]
        )
        
        if plot_path:
            unique_values = sorted(data['operational_setting_3'].unique())
            units = sorted(data['unit_number'].unique())
            
            self.results.append({
                "query": 6,
                "status": "SUCCESS",
                "plot_path": plot_path,
                "data_points": len(data),
                "units": units,
                "unique_values": unique_values
            })
            
            return True
        return False
    
    def test_query_7(self):
        """Query 7: Retrieve RUL of all units from the FD001 and plot their distribution using a histogram"""
        print("🎯 Testing Query 7: Histogram of RUL distribution (All units, FD001)")
        print("=" * 70)
        
        sql_query = """
        SELECT RUL 
        FROM rul_data 
        WHERE dataset = 'FD001'
        """
        
        data = self.db.execute_query(sql_query)
        if data is None or data.empty:
            print("❌ No data retrieved")
            return False
        
        print(f"✅ Retrieved {len(data)} data points")
        print(f"📊 RUL range: {data['RUL'].min()} - {data['RUL'].max()}")
        
        plot_path = self.histogram_plotter.create_distribution_plot(
            data=data,
            column="RUL",
            title="Query 7: Distribution of RUL Values (All Units, FD001)",
            output_filename="query_7_golden_plot"
        )
        
        if plot_path:
            self.results.append({
                "query": 7,
                "status": "SUCCESS",
                "plot_path": plot_path,
                "data_points": len(data),
                "rul_range": f"{data['RUL'].min()} - {data['RUL'].max()}",
                "unique_values_count": data['RUL'].nunique()
            })
            
            return True
        return False
    
    def generate_all_plots(self):
        """Generate all golden plots."""
        print("🎊 GENERATING ALL GOLDEN PLOTS")
        print("=" * 50)
        
        test_methods = [
            self.test_query_1,
            self.test_query_2,
            self.test_query_3,
            self.test_query_4,
            self.test_query_5,
            self.test_query_6,
            self.test_query_7
        ]
        
        success_count = 0
        for i, test_method in enumerate(test_methods, 1):
            try:
                print(f"\n📊 Query {i}/7")
                if test_method():
                    success_count += 1
                    print(f"✅ Query {i}: SUCCESS")
                else:
                    print(f"❌ Query {i}: FAILED")
            except Exception as e:
                print(f"💥 Query {i}: ERROR - {e}")
                self.results.append({
                    "query": i,
                    "status": "ERROR",
                    "error": str(e)
                })
        
        print(f"\n🎉 SUMMARY: {success_count}/7 plots generated successfully")
        return success_count == 7
    
    def save_results(self):
        """Save generation results to JSON file."""
        results_file = "golden_plot_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"📄 Results saved to: {results_file}")

def main():
    """Main execution function."""
    generator = GoldenPlotGenerator()
    
    success = generator.generate_all_plots()
    generator.save_results()
    
    if success:
        print("\n🎊 ALL GOLDEN PLOTS GENERATED SUCCESSFULLY!")
    else:
        print("\n💥 SOME GOLDEN PLOTS FAILED TO GENERATE")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 