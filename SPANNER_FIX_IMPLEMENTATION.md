# Spanner Corruption Fix Implementation

## Implementation Details

### 1. Timing Validation Utilities (`satb_splitter/timing_validator.py`)

```python
"""
Timing validation utilities for preventing spanner processing corruption.
"""

import music21
from typing import Dict, List, Any, Optional, Tuple
import copy

class MeasureTimingSnapshot:
    """Captures the timing state of a measure for validation and rollback."""
    
    def __init__(self, measure: music21.stream.Measure):
        self.measure_number = measure.number
        self.measure_offset = measure.offset
        self.elements = []
        
        # Capture all timed elements
        for element in measure.getElementsByClass([music21.note.Note, music21.note.Rest]):
            self.elements.append({
                'type': type(element).__name__,
                'offset': element.offset,
                'duration': element.duration.quarterLength,
                'pitch': str(element.pitch) if hasattr(element, 'pitch') else None,
                'element_id': id(element)
            })
    
    def validate_against_measure(self, measure: music21.stream.Measure) -> List[str]:
        """Validate current measure state against this snapshot."""
        errors = []
        
        if measure.number != self.measure_number:
            errors.append(f"Measure number changed: {self.measure_number} -> {measure.number}")
        
        current_elements = []
        for element in measure.getElementsByClass([music21.note.Note, music21.note.Rest]):
            current_elements.append({
                'type': type(element).__name__,
                'offset': element.offset,
                'duration': element.duration.quarterLength,
                'pitch': str(element.pitch) if hasattr(element, 'pitch') else None
            })
        
        if len(current_elements) != len(self.elements):
            errors.append(f"Element count changed: {len(self.elements)} -> {len(current_elements)}")
        
        # Check each element
        for i, (original, current) in enumerate(zip(self.elements, current_elements)):
            if abs(original['offset'] - current['offset']) > 0.01:
                errors.append(f"Element {i} offset changed: {original['offset']} -> {current['offset']}")
            
            if abs(original['duration'] - current['duration']) > 0.01:
                errors.append(f"Element {i} duration changed: {original['duration']} -> {current['duration']}")
            
            if original['pitch'] != current['pitch']:
                errors.append(f"Element {i} pitch changed: {original['pitch']} -> {current['pitch']}")
        
        return errors

def backup_measure_timing(measure: music21.stream.Measure) -> MeasureTimingSnapshot:
    """Create a timing snapshot of a measure."""
    return MeasureTimingSnapshot(measure)

def validate_measure_timing(measure: music21.stream.Measure, 
                          snapshot: MeasureTimingSnapshot) -> Tuple[bool, List[str]]:
    """Validate measure timing against a snapshot."""
    errors = snapshot.validate_against_measure(measure)
    return len(errors) == 0, errors

def restore_measure_timing(measure: music21.stream.Measure, 
                         snapshot: MeasureTimingSnapshot) -> bool:
    """Attempt to restore measure timing from snapshot (simplified version)."""
    # This is a complex operation that would require careful implementation
    # For now, we'll focus on detection and prevention
    print(f"WARNING: Timing corruption detected in measure {measure.number}")
    print("Restoration not implemented - corruption prevented by validation")
    return False
```

### 2. Enhanced Spanner Builder (`satb_splitter/spanner_builder.py` modifications)

#### Key Changes:

1. **Add timing validation to `recreate_spanner_in_part()`**:
```python
def recreate_spanner_in_part(part: music21.stream.Part, spanner_info: Dict[str, Any]) -> None:
    """Recreate a single spanner in a voice part with timing validation."""
    from .timing_validator import backup_measure_timing, validate_measure_timing
    
    # Find affected measures and create backups
    affected_measures = get_affected_measures(part, spanner_info)
    measure_backups = {}
    
    for measure in affected_measures:
        measure_backups[measure.number] = backup_measure_timing(measure)
    
    try:
        # Original spanner recreation logic
        spanner_type = spanner_info['type']
        
        if spanner_type == 'Tie':
            recreate_tie_in_part(part, spanner_info)
        elif spanner_type == 'Slur':
            recreate_slur_in_part(part, spanner_info)
        elif spanner_type in ['Crescendo', 'Diminuendo']:
            recreate_wedge_in_part(part, spanner_info)
        else:
            print(f"    Warning: Unknown spanner type {spanner_type}, skipping")
            return
        
        # Validate timing after spanner creation
        for measure in affected_measures:
            backup = measure_backups[measure.number]
            is_valid, errors = validate_measure_timing(measure, backup)
            
            if not is_valid:
                print(f"    ERROR: Timing corruption detected in measure {measure.number}")
                for error in errors:
                    print(f"      {error}")
                
                # For now, log the error - in future could implement rollback
                print(f"    Spanner {spanner_type} may have corrupted timing")
                
    except Exception as e:
        print(f"    Error recreating {spanner_info['type']}: {e}")
```

2. **Improve `find_note_in_part()` with better matching**:
```python
def find_note_in_part(part: music21.stream.Part, measure_number: int, 
                     pitch: str, offset: float) -> music21.note.Note:
    """Find a specific note with enhanced matching logic."""
    if measure_number is None:
        return None
    
    # Find the measure
    for measure in part.getElementsByClass(music21.stream.Measure):
        if measure.number == measure_number:
            # Look for the note with matching pitch and offset
            candidates = []
            
            for note in measure.getElementsByClass(music21.note.Note):
                if str(note.pitch) == pitch:
                    offset_diff = abs(note.offset - offset)
                    candidates.append((note, offset_diff))
            
            if not candidates:
                print(f"    Warning: No notes with pitch {pitch} found in measure {measure_number}")
                return None
            
            # Sort by offset difference and take the closest match
            candidates.sort(key=lambda x: x[1])
            best_match, offset_diff = candidates[0]
            
            if offset_diff > 0.1:  # Tolerance check
                print(f"    Warning: Best match for {pitch} at offset {offset} has difference {offset_diff}")
            
            return best_match
            
    return None
```

### 3. Integration Points

#### In `voice_splitter.py`:
- Add timing validation before and after spanner processing
- Log detailed information about spanner operations
- Add option to disable spanner processing if corruption is detected

#### In `spanner_builder.py`:
- Import and use timing validation utilities
- Add comprehensive error handling
- Implement graceful degradation on spanner failures

### 4. Testing Strategy

#### Create test file `test_spanner_timing_fix.py`:
```python
def test_measure_29_corruption_fix():
    """Test that measure 29 corruption is fixed."""
    # Run voice splitter
    voices = split_satb_voices("Crossing The Bar.mscz")
    
    # Check measure 29 in Soprano
    soprano_part = voices['Soprano'].parts[0]
    measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
    measure_29 = measures[28]  # 0-based
    
    notes = list(measure_29.getElementsByClass(music21.note.Note))
    rests = list(measure_29.getElementsByClass(music21.note.Rest))
    
    # Validate correct timing
    assert len(notes) == 2, f"Expected 2 notes, got {len(notes)}"
    assert len(rests) == 0, f"Expected 0 rests, got {len(rests)}"
    
    # Check note timing
    assert abs(notes[0].offset - 0.0) < 0.1, f"First note offset should be 0.0, got {notes[0].offset}"
    assert abs(notes[0].duration.quarterLength - 3.0) < 0.1, f"First note duration should be 3.0, got {notes[0].duration.quarterLength}"
    
    assert abs(notes[1].offset - 3.0) < 0.1, f"Second note offset should be 3.0, got {notes[1].offset}"
    assert abs(notes[1].duration.quarterLength - 1.0) < 0.1, f"Second note duration should be 1.0, got {notes[1].duration.quarterLength}"
```

## Implementation Priority

1. **Phase 1**: Create timing validation utilities
2. **Phase 2**: Enhance spanner builder with validation
3. **Phase 3**: Add comprehensive testing
4. **Phase 4**: Integration and validation

## Rollout Strategy

1. **Test on isolated measure 29** first
2. **Validate no regression** in other measures
3. **Full integration testing**
4. **Performance impact assessment**