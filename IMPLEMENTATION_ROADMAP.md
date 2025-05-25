# Spanner Corruption Fix - Implementation Roadmap

## Executive Summary

I have identified and designed a fix for the spanner processing corruption that affects measure 29 in the SATB voice splitter. The corruption occurs during the spanner rebuilding phase and specifically affects the Soprano voice, causing note timing to shift incorrectly.

## Problem Analysis Complete ✅

### Root Cause Confirmed
- **Location**: `satb_splitter/spanner_builder.py` - `recreate_spanner_in_part()` function
- **Mechanism**: Spanner rebuilding process corrupts note offsets during processing
- **Scope**: Soprano voice only, measures 29-30+ (cumulative effect)
- **Evidence**: Notes shift from correct timing (0.0, 3.0) to incorrect timing (3.5, 6.5)

### Diagnostic Tools Created ✅
- `analyze_measure_29.py` - Comprehensive measure analysis
- `systematic_analysis.py` - Multi-measure corruption detection
- `trace_offset_drift.py` - Exact corruption point identification
- `test_dynamics_corruption.py` - Ruled out dynamics as cause

## Solution Design Complete ✅

### Fix Strategy
1. **Defensive Programming**: Add timing validation before/after spanner operations
2. **Enhanced Error Detection**: Implement comprehensive corruption detection
3. **Improved Note Matching**: Better note finding logic in spanner rebuilding
4. **Graceful Degradation**: Safe fallback when corruption is detected

### Architecture
- **New Module**: `timing_validator.py` - Timing validation utilities
- **Enhanced Module**: `spanner_builder.py` - Add validation and safety checks
- **Integration Points**: `voice_splitter.py` - Add validation hooks

## Implementation Plan

### Phase 1: Core Utilities (Priority: HIGH)
- [ ] Create `satb_splitter/timing_validator.py`
  - `MeasureTimingSnapshot` class for state capture
  - `backup_measure_timing()` function
  - `validate_measure_timing()` function
  - `restore_measure_timing()` function (future)

### Phase 2: Spanner Builder Enhancement (Priority: HIGH)
- [ ] Modify `satb_splitter/spanner_builder.py`
  - Add timing validation to `recreate_spanner_in_part()`
  - Enhance `find_note_in_part()` with better matching
  - Add comprehensive error handling
  - Implement corruption detection and logging

### Phase 3: Integration (Priority: MEDIUM)
- [ ] Modify `satb_splitter/voice_splitter.py`
  - Add pre/post spanner processing validation
  - Add detailed logging for debugging
  - Add option to disable spanner processing on corruption

### Phase 4: Testing (Priority: HIGH)
- [ ] Create `test_spanner_timing_fix.py`
  - Unit tests for timing validation
  - Integration tests for measure 29 fix
  - Regression tests for other measures
  - Performance impact tests

### Phase 5: Validation (Priority: HIGH)
- [ ] Test fix on "Crossing The Bar.mscz"
- [ ] Verify measure 29 corruption is resolved
- [ ] Ensure no regression in other measures
- [ ] Validate all voice parts remain correct

## Success Criteria

### Primary Goals
1. **Measure 29 Soprano timing is correct**:
   - Note 1: G4, duration=3.0, offset=0.0
   - Note 2: G4, duration=1.0, offset=3.0
   - No unexpected rests

2. **No regression in other measures**:
   - All other measures remain unchanged
   - Alto, Tenor, Bass voices unaffected

3. **Robust error handling**:
   - Corruption detection works reliably
   - Graceful degradation on spanner failures
   - Detailed logging for debugging

### Secondary Goals
1. **Performance impact minimal** (< 10% slowdown)
2. **Code maintainability improved** with better error handling
3. **Future corruption prevention** through validation framework

## Risk Assessment

### Low Risk
- Timing validation utilities (isolated, defensive)
- Enhanced error logging (non-functional)

### Medium Risk
- Spanner builder modifications (core functionality)
- Note finding algorithm changes (could affect matching)

### High Risk
- Integration changes to main voice splitter (could affect all processing)

### Mitigation Strategy
- **Incremental implementation** with testing at each phase
- **Comprehensive test suite** before integration
- **Rollback plan** if issues are discovered
- **Feature flag** to disable new validation if needed

## Next Steps

1. **Switch to Code mode** for implementation
2. **Implement Phase 1** (timing validation utilities)
3. **Test utilities** in isolation
4. **Implement Phase 2** (spanner builder enhancement)
5. **Integration testing** with measure 29
6. **Full validation** across all measures

## Timeline Estimate

- **Phase 1-2**: 2-3 hours (core implementation)
- **Phase 3**: 1 hour (integration)
- **Phase 4-5**: 2-3 hours (testing and validation)
- **Total**: 5-7 hours for complete fix

## Implementation Ready ✅

All analysis is complete, solution is designed, and implementation plan is ready. Ready to switch to Code mode and begin implementation.