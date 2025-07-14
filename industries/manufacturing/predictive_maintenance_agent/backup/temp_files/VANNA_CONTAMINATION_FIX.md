# Vector Store Contamination Fix

## Problem

The predictive maintenance agent was experiencing vector store contamination issues where:

1. **Simple queries worked fine** (e.g., "Retrieve time in cycles and operational setting 1...")
2. **Complex queries failed** after running evaluation scripts (e.g., "Retrieve time in cycles, all sensor measurements and RUL value for engine unit 24...")
3. **JSON parsing errors** occurred due to malformed responses
4. **Performance degraded** over time due to contaminated training data

## Root Cause

The issue was caused by **vector store contamination** in the Vanna implementation:

- Even with auto-training disabled, there were race conditions where training could occur
- Poor SQL results were being used to contaminate the vector store
- No proper isolation between initialization and production modes
- No mechanism to detect or prevent contamination

## Solution

### 1. VannaManager Class

A new `VannaManager` class has been implemented that provides:

- **Singleton pattern** to ensure only one instance per configuration
- **Thread-safe operations** with proper locking
- **Automatic cleanup** and reset capabilities
- **Strict isolation** between production and initialization modes
- **Contamination detection** and prevention

### 2. ContaminationPreventionVanna Class

An enhanced Vanna class that:

- **Blocks all training attempts** during production use
- **Validates SQL responses** for contamination indicators
- **Provides strict mode** enforcement
- **Logs all training attempts** for monitoring

### 3. Monitoring and Cleanup Utilities

Two utility scripts for managing the system:

- **`reset_vanna_state.py`** - Reset contaminated instances
- **`monitor_vanna_state.py`** - Monitor for contamination issues

## Implementation Details

### Key Features

1. **Automatic Reset**: Instances are automatically reset after 50 queries to prevent contamination
2. **Contamination Detection**: Responses are checked for error indicators
3. **Thread Safety**: All operations are properly synchronized
4. **Monitoring**: Real-time stats and warnings
5. **Cleanup**: Easy reset and database cleaning

### Files Modified

- `src/predictive_maintenance_agent/vanna_manager.py` - New VannaManager class
- `src/predictive_maintenance_agent/generate_sql_query_and_retrieve_tool.py` - Updated to use VannaManager
- `reset_vanna_state.py` - Reset utility
- `monitor_vanna_state.py` - Monitoring utility

## Usage

### Normal Operation

The system now works automatically with contamination prevention. No changes are needed for normal queries.

### Monitoring

Check the system status:
```bash
python monitor_vanna_state.py
```

Continuous monitoring:
```bash
python monitor_vanna_state.py --watch
```

Export statistics:
```bash
python monitor_vanna_state.py --export-stats
```

### Cleanup

Reset VannaManager instances (soft reset):
```bash
python reset_vanna_state.py
```

Aggressive cleanup (clears vector database):
```bash
python reset_vanna_state.py --force-clean-db
```

### Troubleshooting

If you notice performance degradation:

1. **Check status**: `python monitor_vanna_state.py`
2. **Soft reset**: `python reset_vanna_state.py`
3. **Hard reset**: `python reset_vanna_state.py --force-clean-db`

## Configuration

### Contamination Threshold

The default contamination threshold is 50 queries. You can adjust this in `VannaManager`:

```python
self.contamination_threshold = 50  # Adjust as needed
```

### Warning Threshold

The monitoring utility warns at 40 queries by default:

```bash
python monitor_vanna_state.py --threshold 30  # Warn at 30 queries
```

## Expected Behavior

After implementing this fix:

1. **Complex queries work consistently** without degradation
2. **No more JSON parsing errors** from malformed responses
3. **Automatic contamination prevention** without manual intervention
4. **Monitoring capabilities** to detect issues early
5. **Easy cleanup** when needed

## Testing

Test the fix with your problematic queries:

```
# This should now work consistently:
Retrieve time in cycles, all sensor measurements and RUL value for engine unit 24 from FD001 test and RUL tables. Predict RUL for it. Finally, generate a plot to compare actual RUL value with predicted RUL value across time.
```

Run the monitoring utility during testing:
```bash
python monitor_vanna_state.py --watch
```

## Technical Details

### Contamination Indicators

The system detects contamination based on:
- "not allowed to see the data"
- "database introspection"
- "Error:" responses
- JSON-like responses in SQL
- "[object Object]" responses

### Thread Safety

All operations are thread-safe using:
- Class-level locks for singleton management
- Instance-level locks for operations
- Proper synchronization patterns

### Memory Management

- Instances are properly cleaned up on reset
- No memory leaks from persistent connections
- Efficient singleton pattern implementation

## Maintenance

### Regular Monitoring

Set up periodic monitoring:
```bash
# Add to crontab for hourly checks
0 * * * * /path/to/python monitor_vanna_state.py --threshold 40
```

### Automated Cleanup

Consider automating cleanup before evaluation runs:
```bash
# Reset before running evaluations
python reset_vanna_state.py
python run_eval_script.py
```

### Log Monitoring

Watch for these log messages:
- "Contamination threshold reached" - Automatic reset triggered
- "Contaminated response detected" - Bad response blocked
- "Blocked training attempt" - Training prevented

## Support

If you encounter issues:

1. Check the logs for contamination warnings
2. Run the monitoring utility
3. Try a soft reset first, then hard reset if needed
4. Ensure proper imports in your code

The system is now robust against vector store contamination and should provide consistent performance across all query types. 