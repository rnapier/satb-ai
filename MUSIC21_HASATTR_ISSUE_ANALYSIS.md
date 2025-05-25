# Music21 Code Review: hasattr Usage Issue

## Issue Identified

**Location:** `satb_splitter/main.py:38`

**Problematic Code:**
```python
if hasattr(voice_score.metadata, 'movementName') and voice_score.metadata.movementName:
    voice_score.metadata.movementName = f"{base_name} ({voice_name})"
```

## Problem Analysis

### Why This is Problematic

1. **API Uncertainty:** Using `hasattr()` suggests uncertainty about whether `movementName` is part of the stable music21 metadata API
2. **Fragile Pattern:** This approach may break if music21 changes its internal metadata structure
3. **Internal Detail Access:** The code may be relying on implementation details rather than documented public API

### Risk Assessment

- **Risk Level:** High
- **Impact:** Code could break with music21 library updates
- **Likelihood:** Medium (depends on music21's API stability commitments)

## Recommended Solution

Replace the `hasattr` check with a proper try/except pattern:

```python
# Current problematic code:
if hasattr(voice_score.metadata, 'movementName') and voice_score.metadata.movementName:
    voice_score.metadata.movementName = f"{base_name} ({voice_name})"

# Recommended replacement:
try:
    if voice_score.metadata.movementName:
        voice_score.metadata.movementName = f"{base_name} ({voice_name})"
except AttributeError:
    # movementName not available in this music21 version or score
    pass
```

## Benefits of the Fix

1. **More Pythonic:** Uses EAFP (Easier to Ask for Forgiveness than Permission) principle
2. **Cleaner Code:** Eliminates the `hasattr` check
3. **Better Error Handling:** Gracefully handles cases where `movementName` doesn't exist
4. **API Agnostic:** Works regardless of whether `movementName` is a property, attribute, or method

## Implementation Plan

### Step 1: Replace hasattr Usage
- Modify `satb_splitter/main.py` line 38
- Replace `hasattr` check with try/except block
- Test the change with existing functionality

### Step 2: Validation
- Test with various MusicXML files
- Verify that metadata handling works correctly
- Ensure no regression in functionality

## Code Change Details

**File:** `satb_splitter/main.py`
**Lines:** 37-39

**Before:**
```python
# Clean up movement title to match the work title
if hasattr(voice_score.metadata, 'movementName') and voice_score.metadata.movementName:
    voice_score.metadata.movementName = f"{base_name} ({voice_name})"
```

**After:**
```python
# Clean up movement title to match the work title
try:
    if voice_score.metadata.movementName:
        voice_score.metadata.movementName = f"{base_name} ({voice_name})"
except AttributeError:
    # movementName not available in this music21 version or score
    pass
```

## Testing Strategy

1. **Existing Functionality:** Ensure current test cases still pass
2. **Edge Cases:** Test with scores that may not have movementName
3. **Different Music21 Versions:** Verify compatibility across versions
4. **Error Scenarios:** Confirm graceful handling when movementName is unavailable

## Conclusion

This single change will eliminate the improper use of `hasattr` to access potentially internal music21 details, making the code more robust and following Python best practices for attribute access.