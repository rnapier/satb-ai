#!/usr/bin/env python3
"""
Test the copy_dynamics_to_parts function to confirm it's causing the corruption.
"""

import music21
import copy
from pathlib import Path

def test_dynamics_corruption():
    """Test if copy_dynamics_to_parts corrupts note timing."""
    print("=== TESTING DYNAMICS CORRUPTION ===")
    
    # Create a test measure like measure 29
    print("\n--- Creating Test Measure ---")
    test_measure = music21.stream.Measure(number=29)
    
    # Add notes like in measure 29
    note1 = music21.note.Note("G4", quarterLength=3.0)
    note1.offset = 0.0
    note2 = music21.note.Note("G4", quarterLength=1.0)
    note2.offset = 3.0
    
    test_measure.append(note1)
    test_measure.append(note2)
    
    print("Test measure BEFORE dynamics:")
    print(f"  Measure offset: {test_measure.offset}")
    print(f"  Measure duration: {test_measure.duration.quarterLength}")
    
    notes = list(test_measure.getElementsByClass(music21.note.Note))
    rests = list(test_measure.getElementsByClass(music21.note.Rest))
    
    for i, note in enumerate(notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    # Create a test part with this measure
    test_part = music21.stream.Part()
    test_part.partName = "Test"
    test_part.append(test_measure)
    
    # Create a dynamic info like the one from measure 29
    print("\n--- Creating Dynamic Info ---")
    dynamic_obj = music21.dynamics.Dynamic('f')
    dynamic_info = {
        'measure': 29,
        'offset': 3.5,
        'value': 'f',
        'object': dynamic_obj,
        'type': 'measure'
    }
    
    print(f"Dynamic info: {dynamic_info['value']} at measure {dynamic_info['measure']}, offset {dynamic_info['offset']}")
    
    # Test the copy_dynamics_to_parts function
    print("\n--- Testing copy_dynamics_to_parts Function ---")
    from satb_splitter.unification import copy_dynamics_to_parts
    
    voices_dict = {'Test': test_part}
    source_dynamics = [dynamic_info]
    
    print("Calling copy_dynamics_to_parts...")
    copy_dynamics_to_parts(source_dynamics, ['Test'], voices_dict)
    
    # Check the measure after dynamics processing
    print("\nTest measure AFTER dynamics:")
    part_measures = list(test_part.getElementsByClass(music21.stream.Measure))
    processed_measure = part_measures[0]
    
    print(f"  Measure offset: {processed_measure.offset}")
    print(f"  Measure duration: {processed_measure.duration.quarterLength}")
    
    notes = list(processed_measure.getElementsByClass(music21.note.Note))
    rests = list(processed_measure.getElementsByClass(music21.note.Rest))
    dynamics = list(processed_measure.getElementsByClass(music21.dynamics.Dynamic))
    
    print(f"  Found: {len(notes)} notes, {len(rests)} rests, {len(dynamics)} dynamics")
    
    for i, note in enumerate(notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    for i, dyn in enumerate(dynamics):
        print(f"    Dynamic {i+1}: {dyn.value} offset={dyn.offset}")
    
    # Check if corruption occurred
    print("\n--- CORRUPTION ANALYSIS ---")
    
    if len(rests) > 0:
        print("⚠️  CORRUPTION DETECTED: Unexpected rests found!")
    
    if len(notes) != 2:
        print(f"⚠️  CORRUPTION DETECTED: Expected 2 notes, found {len(notes)}")
    
    # Check note timing
    expected_notes = [
        ("G4", 3.0, 0.0),
        ("G4", 1.0, 3.0)
    ]
    
    for i, (expected_pitch, expected_dur, expected_offset) in enumerate(expected_notes):
        if i < len(notes):
            note = notes[i]
            actual_pitch = f"{note.pitch.name}{note.pitch.octave}"
            actual_dur = note.duration.quarterLength
            actual_offset = note.offset
            
            if (actual_pitch != expected_pitch or 
                abs(actual_dur - expected_dur) > 0.1 or 
                abs(actual_offset - expected_offset) > 0.1):
                print(f"⚠️  CORRUPTION DETECTED in Note {i+1}:")
                print(f"    Expected: {expected_pitch} dur={expected_dur} offset={expected_offset}")
                print(f"    Actual: {actual_pitch} dur={actual_dur} offset={actual_offset}")
            else:
                print(f"✅ Note {i+1} is correct")

def test_measure_insert_behavior():
    """Test how music21 measure.insert() behaves with different offsets."""
    print("\n=== TESTING MEASURE INSERT BEHAVIOR ===")
    
    # Create a measure with notes
    measure = music21.stream.Measure(number=1)
    
    # Add notes first
    note1 = music21.note.Note("C4", quarterLength=2.0)
    note2 = music21.note.Note("D4", quarterLength=2.0)
    
    measure.append(note1)  # Should be at offset 0.0
    measure.append(note2)  # Should be at offset 2.0
    
    print("Measure after adding notes:")
    notes = list(measure.getElementsByClass(music21.note.Note))
    for i, note in enumerate(notes):
        print(f"  Note {i+1}: {note.pitch.name} dur={note.duration.quarterLength} offset={note.offset}")
    
    # Now insert a dynamic at offset 1.5 (between the notes)
    dynamic = music21.dynamics.Dynamic('f')
    measure.insert(1.5, dynamic)
    
    print("\nMeasure after inserting dynamic at offset 1.5:")
    notes = list(measure.getElementsByClass(music21.note.Note))
    rests = list(measure.getElementsByClass(music21.note.Rest))
    dynamics = list(measure.getElementsByClass(music21.dynamics.Dynamic))
    
    print(f"Found: {len(notes)} notes, {len(rests)} rests, {len(dynamics)} dynamics")
    
    for i, note in enumerate(notes):
        print(f"  Note {i+1}: {note.pitch.name} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(rests):
        print(f"  Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    for i, dyn in enumerate(dynamics):
        print(f"  Dynamic {i+1}: {dyn.value} offset={dyn.offset}")
    
    # Test inserting at offset 3.5 (after the notes)
    print("\n--- Testing insert at offset 3.5 (after notes) ---")
    measure2 = music21.stream.Measure(number=2)
    
    note1 = music21.note.Note("G4", quarterLength=3.0)
    note2 = music21.note.Note("G4", quarterLength=1.0)
    
    measure2.append(note1)  # offset 0.0
    measure2.append(note2)  # offset 3.0
    
    print("Before inserting dynamic:")
    notes = list(measure2.getElementsByClass(music21.note.Note))
    for i, note in enumerate(notes):
        print(f"  Note {i+1}: {note.pitch.name} dur={note.duration.quarterLength} offset={note.offset}")
    
    # Insert dynamic at 3.5 (between note2 start at 3.0 and its end at 4.0)
    dynamic2 = music21.dynamics.Dynamic('f')
    measure2.insert(3.5, dynamic2)
    
    print("After inserting dynamic at offset 3.5:")
    notes = list(measure2.getElementsByClass(music21.note.Note))
    rests = list(measure2.getElementsByClass(music21.note.Rest))
    dynamics = list(measure2.getElementsByClass(music21.dynamics.Dynamic))
    
    print(f"Found: {len(notes)} notes, {len(rests)} rests, {len(dynamics)} dynamics")
    
    for i, note in enumerate(notes):
        print(f"  Note {i+1}: {note.pitch.name} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(rests):
        print(f"  Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    for i, dyn in enumerate(dynamics):
        print(f"  Dynamic {i+1}: {dyn.value} offset={dyn.offset}")

def main():
    test_dynamics_corruption()
    test_measure_insert_behavior()

if __name__ == "__main__":
    main()