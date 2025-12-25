# Evaluation Dataset Changes

## DATASET NAME CORRECTIONS - 2025-07-09

### Problem
The evaluation questions contained incorrect dataset names that don't exist in the database. This caused the SQL generation tool to return hallucinated values instead of correct answers.

### Root Cause
- **Database contains**: `'FD001'`, `'FD002'`, `'FD003'`, `'FD004'`
- **Eval questions used**: `'RUL_FD001'`, `'RUL_FD002'`, `'RUL_FD003'`, `'RUL_FD004'`

### Changes Made
Fixed the following questions in `eval_set.json`:

| Question ID | Original Dataset Name | Corrected Dataset Name |
|-------------|----------------------|------------------------|
| 1           | `RUL_FD001`         | `FD001`               |
| 2           | `RUL_FD001`         | `FD001`               |
| 3           | `RUL_FD003`         | `FD003`               |
| 4           | `RUL_FD002`         | `FD002`               |
| 5           | `RUL_FD002`         | `FD002`               |
| 6           | `RUL_FD004`         | `FD004`               |

### Expected Impact
- Simple RUL lookup queries will now return correct values directly from the database
- The agent will no longer hallucinate values like `125` for unit 59 (correct answer: `114`)
- The evaluation framework will work correctly with proper dataset names

### Example Fix
**Before:**
```json
{
  "id": "1",
  "question": "What is the remaining useful life (RUL) of unit_number 59 in dataset RUL_FD001",
  "answer": "114"
}
```

**After:**
```json
{
  "id": "1", 
  "question": "What is the remaining useful life (RUL) of unit_number 59 in dataset FD001",
  "answer": "114"
}
```

### Verification
Unit 59 in dataset FD001 has RUL = 114 (verified in database):
```sql
SELECT * FROM rul_data WHERE unit_number = 59 AND dataset = 'FD001';
-- Result: (59, 'FD001', 114)
```

---

## VANNA TRAINING UPDATES - 2025-07-09

### Problem 1: COUNT Queries with RUL Conditions
The SQL generation tool lacked proper training for COUNT queries with RUL conditions, causing incorrect results.

**Example Issue:**
- Query: "How many units have RUL of 100 or more in dataset FD003"
- Expected: 33 units
- System returned: 100 (total units in dataset, not filtered by RUL condition)

### Solution 1: Added COUNT Query Training Examples
Added specific training examples in `src/predictive_maintenance_agent/vanna_util.py`:

```python
# Add training examples for COUNT queries with RUL conditions
vn.train(question="How many units have RUL of 100 or more in dataset FD003", 
sql="SELECT COUNT(*) FROM rul_data WHERE dataset = 'FD003' AND RUL >= 100")
vn.train(question="How many units have RUL of 50 or less in dataset FD002", 
sql="SELECT COUNT(*) FROM rul_data WHERE dataset = 'FD002' AND RUL <= 50")
vn.train(question="Count units with RUL greater than 100 in FD001", 
sql="SELECT COUNT(*) FROM rul_data WHERE dataset = 'FD001' AND RUL > 100")
vn.train(question="How many units have RUL equal to 155 in FD002", 
sql="SELECT COUNT(*) FROM rul_data WHERE dataset = 'FD002' AND RUL = 155")
vn.train(question="Report the unit_number of the units that have RUL equal to 155 in FD002", 
sql="SELECT unit_number FROM rul_data WHERE dataset = 'FD002' AND RUL = 155")
vn.train(question="In the dataset FD004, how many units have RUL equal to 10 and what are their unit numbers?", 
sql="SELECT COUNT(*) as count, GROUP_CONCAT(unit_number) as unit_numbers FROM rul_data WHERE dataset = 'FD004' AND RUL = 10")
```

### Problem 2: Dataset Naming Convention Mismatch
Queries used `train_FD001`, `test_FD001` format, but database contains `FD001`, `FD002`, etc.

**Example Issue:**
- Query: "In dataset train_FD003, what was sensor_measurement_20 for unit 1 at time_in_cycles 10"
- Database table: `training_data` with dataset column containing `'FD003'` (not `'train_FD003'`)

### Solution 2: Added Dataset Naming Convention Training Examples
Added training examples to handle name translation:

```python
# Add training examples for train_FD naming convention (train_FD001 -> FD001)
vn.train(question="In dataset train_FD001, what was the 3rd operational setting at time 20 for unit_number 1", 
sql="SELECT operational_setting_3 FROM training_data WHERE dataset = 'FD001' AND unit_number = 1 AND time_in_cycles = 20")
vn.train(question="In dataset train_FD003, what was sensor_measurement_20 and sensor_measurement_21 for unit 1 at time_in_cycles 10", 
sql="SELECT sensor_measurement_20, sensor_measurement_21 FROM training_data WHERE dataset = 'FD003' AND unit_number = 1 AND time_in_cycles = 10")
vn.train(question="How many units have operational_setting_3 equal to 100 in dataset train_FD001 at time_in_cycles 40?", 
sql="SELECT COUNT(*) FROM training_data WHERE dataset = 'FD001' AND operational_setting_3 = 100 AND time_in_cycles = 40")
vn.train(question="How many units have operational_setting_3 equal to 100 in dataset train_FD001?", 
sql="SELECT COUNT(*) FROM training_data WHERE dataset = 'FD001' AND operational_setting_3 = 100")
vn.train(question="In dataset train_FD004, what was the 3rd operational setting at time 20 for unit_number 107", 
sql="SELECT operational_setting_3 FROM training_data WHERE dataset = 'FD004' AND unit_number = 107 AND time_in_cycles = 20")

# Add training examples for test_FD naming convention (test_FD001 -> FD001)
vn.train(question="In dataset test_FD001, what was the sensor_measurement_1 at time 50 for unit_number 1", 
sql="SELECT sensor_measurement_1 FROM test_data WHERE dataset = 'FD001' AND unit_number = 1 AND time_in_cycles = 50")
vn.train(question="How many units have sensor_measurement_2 greater than 500 in dataset test_FD002?", 
sql="SELECT COUNT(*) FROM test_data WHERE dataset = 'FD002' AND sensor_measurement_2 > 500")
vn.train(question="In dataset test_FD003, what was operational_setting_1 for unit 5 at time_in_cycles 30", 
sql="SELECT operational_setting_1 FROM test_data WHERE dataset = 'FD003' AND unit_number = 5 AND time_in_cycles = 30")
```

### Expected Impact
1. **COUNT queries with RUL conditions** will now generate correct SQL with proper filtering
2. **Dataset naming convention** queries will correctly translate:
   - `train_FD001` → `FD001` (in training_data table)
   - `test_FD001` → `FD001` (in test_data table)
3. **Vector database retrained** to include all new training examples

### Verification Examples
- **Q**: "How many units have RUL of 100 or more in dataset FD003" → **A**: 33
- **Q**: "In dataset train_FD004, what was the 3rd operational setting at time 20 for unit_number 107" → **A**: 100.0
- **Q**: "Report the unit_number of the units that have RUL equal to 155 in FD002" → **A**: [6, 141, 165] 