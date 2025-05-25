# Spanner Corruption Fix Plan

## Problem Summary
The spanner rebuilding process in `satb_splitter/spanner_builder.py` is corrupting note timing specifically in the Soprano voice, causing:
- Notes to shift from correct offsets (0.0, 3.0) to incorrect offsets (3.5, 6.5) in measure 29
- Insertion of unexpected 3.5-beat rest at measure beginning
- Cumulative timing drift in subsequent measures

## Root Cause
The `recreate_spanner_in_part()` function is modifying note timing when rebuilding spanners, likely through:
1. Incorrect note finding/matching logic
2. Side effects from spanner insertion operations
3. Music21 internal timing recalculation issues

## Fix Strategy

### Phase 1: Defensive Spanner Processing
1. **Backup note timing** before spanner operations
2. **Validate timing integrity** after each spanner operation
3. **Rollback on corruption detection**
4. **Add detailed logging** for debugging

### Phase 2: Improved Note Finding
1. **Enhanced note matching** in `find_note_in_part()`
2. **Stricter tolerance checks** for note identification
3. **Better error handling** for missing notes

### Phase 3: Safe Spanner Insertion
1. **Non-destructive spanner insertion** methods
2. **Timing preservation** during spanner creation
3. **Validation of spanner placement**

## Implementation Plan

### 1. Create Timing Validation Utilities
- `backup_measure_timing()` - Save original note/rest positions
- `validate_measure_timing()` - Check for timing corruption
- `restore_measure_timing()` - Rollback corrupted timing

### 2. Enhance Spanner Builder
- Add timing validation to `recreate_spanner_in_part()`
- Improve `find_note_in_part()` accuracy
- Add corruption detection and recovery

### 3. Add Safety Checks
- Pre/post spanner processing validation
- Detailed logging for debugging
- Graceful degradation on errors

## Testing Strategy
1. **Unit tests** for timing validation utilities
2. **Integration tests** for spanner processing
3. **Regression tests** for measure 29 specifically
4. **Full pipeline tests** to ensure no side effects