# Deterministic Lyric Distribution Architecture

## Problem Statement

In measure 29 of "Crossing The Bar," the Soprano part sings "far" on a dotted-half note, but other parts have different slur patterns. The current strict matching rule (exact offset + exact duration) fails to copy this lyric to other voices, resulting in dropped lyrics.

## Design Principles

1. **Deterministic**: Predictable rules that always produce the same result
2. **Choral-Focused**: Every note is relevant to singers (no accompaniment complexity)
3. **Rule-Based**: Clear, simple rules rather than complex scoring algorithms
4. **Transparent**: Easy to understand why a lyric was or wasn't copied

## Proposed Solution: Deterministic Time-Window Matching

### Core Algorithm

Instead of exact matching, use **deterministic time windows** with clear precedence rules:

```
FOR each note with lyrics in source voice:
  1. Find all notes in target voices that START within the source note's duration
  2. Apply slur filtering rules (deterministic)
  3. Apply precedence rules to select exactly one candidate per voice
  4. Copy lyric with appropriate syllabic setting
```

### Time Window Definition

**Primary Rule**: A note is a candidate if it starts during the source note's duration:
```
candidate_start >= source_start AND 
candidate_start < source_start + source_duration
```

**Example (Measure 29)**:
- Soprano "far": starts at offset 2.0, duration 3.0 (dotted half)
- Candidates: any note starting between offset 2.0 and 5.0

### Slur Filtering Rules (Deterministic)

1. **Never copy lyrics to notes that are in the middle of a slur**
2. **Always prefer the first note of a slur** over middle/end notes
3. **Single notes (not slurred) are always candidates**

### Precedence Rules (Deterministic)

When multiple candidates exist in the same voice, select in this order:

1. **Longest duration first** (whole > half > quarter > eighth)
2. **Earliest start time** (if durations are equal)
3. **First note encountered** (if both duration and timing are equal)

### Syllabic Intelligence

Copy the syllabic setting from the source, with adjustments:

- `syllabic="single"` → copy as-is
- `syllabic="begin"` → copy as `"begin"` to first candidate only
- `syllabic="middle"` → copy as `"middle"`
- `syllabic="end"` → copy as `"end"` to last candidate only

## Implementation Structure

### 1. Enhanced Note Matching
```python
def find_candidates_in_time_window(self, source_note, target_measure):
    """Find all notes that start during the source note's duration."""
    candidates = []
    source_start = source_note.offset
    source_end = source_start + source_note.duration.quarterLength
    
    for note in target_measure.getElementsByClass('Note'):
        if source_start <= note.offset < source_end:
            candidates.append(note)
    
    return candidates
```

### 2. Slur Analysis
```python
def filter_slurred_notes(self, candidates, measure):
    """Remove notes that are in the middle of slurs."""
    filtered = []
    
    for note in candidates:
        if not self.is_note_in_slur_middle(note, measure):
            filtered.append(note)
    
    return filtered
```

### 3. Deterministic Selection
```python
def select_best_candidate(self, candidates):
    """Select the best candidate using deterministic rules."""
    if not candidates:
        return None
    
    # Sort by: duration (desc), then offset (asc), then creation order
    return sorted(candidates, key=lambda n: (
        -n.duration.quarterLength,  # Longest first
        n.offset,                   # Earliest first
        id(n)                       # Consistent ordering
    ))[0]
```

## Benefits

1. **Predictable**: Same input always produces same output
2. **Simple**: Easy to understand and debug
3. **Choral-Appropriate**: Respects slurs and phrase structure
4. **Flexible**: Handles different rhythmic patterns between voices
5. **Testable**: Clear rules make comprehensive testing possible

## Test Cases

### Primary Test: Measure 29 "far"
- Soprano: dotted-half note "far" at offset 2.0, duration 3.0
- Expected: Copy to appropriate notes in other voices that start between offset 2.0-5.0

### Edge Cases to Test
1. **Multiple candidates in same voice**: Ensure longest duration wins
2. **Slurred passages**: Verify only slur-start notes get lyrics
3. **Exact timing matches**: Ensure backwards compatibility
4. **No candidates found**: System should handle gracefully
5. **Grace notes**: Should be excluded from consideration

## Migration Strategy

1. **Phase 1**: Implement new algorithm alongside existing one
2. **Phase 2**: Add comprehensive tests for both algorithms
3. **Phase 3**: Switch default to new algorithm
4. **Phase 4**: Remove old algorithm after validation

## Configuration Options

For maximum determinism, provide configuration options:

```python
LYRIC_DISTRIBUTION_CONFIG = {
    'time_window_method': 'source_duration',  # 'exact_match', 'source_duration', 'overlap'
    'slur_handling': 'respect_slurs',         # 'ignore_slurs', 'respect_slurs'
    'precedence_rules': 'duration_first',     # 'duration_first', 'timing_first'
    'min_candidate_duration': 0.25           # Exclude very short notes
}
```

This ensures users can adjust behavior for different musical styles while maintaining determinism.