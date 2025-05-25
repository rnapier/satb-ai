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
    
    def get_summary(self) -> str:
        """Get a summary of the timing snapshot."""
        notes = [e for e in self.elements if e['type'] == 'Note']
        rests = [e for e in self.elements if e['type'] == 'Rest']
        return f"Measure {self.measure_number}: {len(notes)} notes, {len(rests)} rests"


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


def get_affected_measures(part: music21.stream.Part, spanner_info: Dict[str, Any]) -> List[music21.stream.Measure]:
    """Get measures that might be affected by a spanner operation."""
    affected_measures = []
    
    # For ties, get the specific measure
    if spanner_info['type'] == 'Tie':
        measure_number = spanner_info.get('measure_number')
        if measure_number:
            for measure in part.getElementsByClass(music21.stream.Measure):
                if measure.number == measure_number:
                    affected_measures.append(measure)
                    break
    
    # For slurs and wedges, get measures containing spanned notes
    elif spanner_info['type'] in ['Slur', 'Crescendo', 'Diminuendo']:
        spanned_notes = spanner_info.get('spanned_notes', [])
        measure_numbers = set()
        
        for note_info in spanned_notes:
            measure_number = note_info.get('measure_number')
            if measure_number:
                measure_numbers.add(measure_number)
        
        for measure_number in measure_numbers:
            for measure in part.getElementsByClass(music21.stream.Measure):
                if measure.number == measure_number:
                    affected_measures.append(measure)
                    break
    
    return affected_measures


def validate_part_timing_integrity(part: music21.stream.Part, 
                                 voice_name: str = "Unknown") -> Tuple[bool, List[str]]:
    """Validate overall timing integrity of a part."""
    errors = []
    measures = list(part.getElementsByClass(music21.stream.Measure))
    
    print(f"Validating timing integrity for {voice_name} ({len(measures)} measures)")
    
    for measure in measures:
        # Check for basic timing issues
        notes = list(measure.getElementsByClass(music21.note.Note))
        rests = list(measure.getElementsByClass(music21.note.Rest))
        
        # Check for overlapping elements
        all_elements = []
        for note in notes:
            all_elements.append(('Note', note.offset, note.duration.quarterLength, str(note.pitch)))
        for rest in rests:
            all_elements.append(('Rest', rest.offset, rest.duration.quarterLength, 'rest'))
        
        # Sort by offset
        all_elements.sort(key=lambda x: x[1])
        
        # Check for gaps or overlaps
        for i in range(len(all_elements) - 1):
            current_end = all_elements[i][1] + all_elements[i][2]
            next_start = all_elements[i + 1][1]
            gap = next_start - current_end
            
            if abs(gap) > 0.1:  # More than 0.1 beat gap/overlap
                errors.append(f"Measure {measure.number}: Gap/overlap of {gap:.2f} beats between elements")
        
        # Check for unexpected rests in measures that shouldn't have them
        if measure.number == 29 and voice_name == "Soprano" and len(rests) > 0:
            errors.append(f"Measure 29 Soprano: Unexpected {len(rests)} rests found")
    
    is_valid = len(errors) == 0
    if not is_valid:
        print(f"  Found {len(errors)} timing issues in {voice_name}")
        for error in errors[:5]:  # Show first 5 errors
            print(f"    {error}")
        if len(errors) > 5:
            print(f"    ... and {len(errors) - 5} more errors")
    else:
        print(f"  {voice_name} timing integrity: OK")
    
    return is_valid, errors