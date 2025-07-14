#!/usr/bin/env python3
"""
Monitor Vanna State Utility

This script provides monitoring capabilities for VannaManager instances
to detect potential contamination issues and track performance metrics.

Usage:
    python monitor_vanna_state.py [--watch] [--threshold 40]
    
Options:
    --watch             Continuously monitor (check every 30 seconds)
    --threshold N       Set contamination warning threshold (default: 40)
    --export-stats      Export statistics to JSON file
"""

import argparse
import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from predictive_maintenance_agent.vanna_manager import VannaManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_vanna_state(contamination_threshold: int = 40):
    """Check the current state of all VannaManager instances"""
    if not VannaManager._instances:
        logger.info("No VannaManager instances found")
        return []
    
    all_stats = []
    contamination_warnings = []
    
    logger.info(f"Checking {len(VannaManager._instances)} VannaManager instances...")
    
    for config_key, manager in VannaManager._instances.items():
        stats = manager.get_stats()
        all_stats.append(stats)
        
        # Check for contamination warnings
        query_count = stats.get('query_count', 0)
        threshold = stats.get('contamination_threshold', 50)
        
        logger.info(f"Manager: {config_key}")
        logger.info(f"  Query count: {query_count}/{threshold}")
        logger.info(f"  Instance ID: {stats.get('instance_id', 'None')}")
        logger.info(f"  Last reset: {datetime.fromtimestamp(stats.get('last_reset_time', 0))}")
        
        # Warning conditions
        if query_count >= contamination_threshold:
            warning = {
                'config_key': config_key,
                'query_count': query_count,
                'threshold': threshold,
                'warning_type': 'contamination_risk'
            }
            contamination_warnings.append(warning)
            logger.warning(f"  ⚠️  CONTAMINATION RISK: {query_count} queries (threshold: {contamination_threshold})")
        
        if query_count >= threshold:
            warning = {
                'config_key': config_key,
                'query_count': query_count,
                'threshold': threshold,
                'warning_type': 'auto_reset_imminent'
            }
            contamination_warnings.append(warning)
            logger.warning(f"  🔄 AUTO-RESET IMMINENT: {query_count} queries (limit: {threshold})")
    
    return all_stats, contamination_warnings

def export_stats(stats_data: list, filename: str = None):
    """Export statistics to JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vanna_stats_{timestamp}.json"
    
    export_data = {
        'timestamp': datetime.now().isoformat(),
        'total_instances': len(stats_data),
        'instances': stats_data
    }
    
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    logger.info(f"Statistics exported to: {filename}")

def watch_mode(contamination_threshold: int = 40, check_interval: int = 30):
    """Continuously monitor VannaManager instances"""
    logger.info(f"Starting watch mode (checking every {check_interval} seconds)")
    logger.info(f"Contamination threshold: {contamination_threshold}")
    logger.info("Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            print("\n" + "="*60)
            print(f"Monitoring Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
            stats, warnings = check_vanna_state(contamination_threshold)
            
            if warnings:
                print(f"\n🚨 WARNINGS DETECTED: {len(warnings)}")
                for warning in warnings:
                    print(f"  - {warning['config_key']}: {warning['warning_type']}")
            else:
                print("\n✅ No contamination warnings detected")
            
            print(f"\nNext check in {check_interval} seconds...")
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")

def main():
    parser = argparse.ArgumentParser(description='Monitor Vanna State Utility')
    parser.add_argument('--watch', action='store_true',
                       help='Continuously monitor (check every 30 seconds)')
    parser.add_argument('--threshold', type=int, default=40,
                       help='Set contamination warning threshold (default: 40)')
    parser.add_argument('--export-stats', action='store_true',
                       help='Export statistics to JSON file')
    parser.add_argument('--check-interval', type=int, default=30,
                       help='Check interval in seconds for watch mode (default: 30)')
    
    args = parser.parse_args()
    
    if args.watch:
        watch_mode(args.threshold, args.check_interval)
    else:
        logger.info("Checking VannaManager state...")
        stats, warnings = check_vanna_state(args.threshold)
        
        if warnings:
            logger.warning(f"Found {len(warnings)} contamination warnings!")
            for warning in warnings:
                logger.warning(f"  {warning['config_key']}: {warning['warning_type']}")
            
            print("\n🚨 RECOMMENDATIONS:")
            print("1. Consider running: python reset_vanna_state.py")
            print("2. For aggressive cleanup: python reset_vanna_state.py --force-clean-db")
            print("3. Monitor with: python monitor_vanna_state.py --watch")
        else:
            logger.info("✅ No contamination warnings detected")
        
        if args.export_stats:
            export_stats(stats)

if __name__ == '__main__':
    main() 