#!/usr/bin/env python3
"""
Test if corruption happens during file write/read cycle.
"""

import music21
import copy
from pathlib import Path


def test_file_write_read_corruption():
    """Test if corruption occurs during file write/read."""
    print("=== Testing File Write/Read Corruption ===")
    
    # Create a clean soprano part like our trace
    soprano_part = music21.stream.Part()
    soprano_part.partName = "Soprano"
    soprano_part.insert(0, music21.clef.TrebleClef())
    
    # Create measure 29 with correct timing
    measure_29 = music21.stream.Measure(number=29)
    
    note1 = music21.note.Note("G4", quarterLength=3.0)
    note1.offset = 0.0
    note2 = music21.note.Note("G4", quarterLength=1.0)
    note2.offset = 3.0
    
    measure_29.append(note1)
    measure_29.append(note2)
    
    # Add dynamic
    dynamic = music21.dynamics.Dynamic('f')
    measure_29.insert(3.5, dynamic)
    
    soprano_part.append(measure_29)
    
    print("BEFORE file write:")
    notes = list(measure_29.getElementsByClass(music21.note.Note))
    rests = list(measure_29.getElementsByClass(music21.note.Rest))
    dynamics = list(measure_29.getElementsByClass(music21.dynamics.Dynamic))
    
    print(f"  {len(notes)} notes, {len(rests)} rests, {len(dynamics)} dynamics")
    for i, note in enumerate(notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    # Create score and write to file
    score = music21.stream.Score()
    score.append(soprano_part)
    
    temp_file = "test_corruption.musicxml"
    print(f"\nWriting to file: {temp_file}")
    score.write('musicxml', fp=temp_file)
    
    # Read back from file
    print(f"Reading back from file...")
    reloaded_score = music21.converter.parse(temp_file)
    reloaded_part = reloaded_score.parts[0]
    reloaded_measures = list(reloaded_part.getElementsByClass(music21.stream.Measure))
    reloaded_measure_29 = reloaded_measures[0]  # Only one measure
    
    print("AFTER file read:")
    reloaded_notes = list(reloaded_measure_29.getElementsByClass(music21.note.Note))
    reloaded_rests = list(reloaded_measure_29.getElementsByClass(music21.note.Rest))
    reloaded_dynamics = list(reloaded_measure_29.getElementsByClass(music21.dynamics.Dynamic))
    
    print(f"  {len(reloaded_notes)} notes, {len(reloaded_rests)} rests, {len(reloaded_dynamics)} dynamics")
    for i, note in enumerate(reloaded_notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(reloaded_rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    for i, dyn in enumerate(reloaded_dynamics):
        print(f"    Dynamic {i+1}: {dyn.value} offset={dyn.offset}")
    
    # Clean up
    Path(temp_file).unlink(missing_ok=True)
    
    # Check for corruption
    corruption_detected = (len(reloaded_rests) > 0 or 
                          (len(reloaded_notes) > 0 and abs(reloaded_notes[0].offset - 0.0) > 0.1))
    
    return corruption_detected


def test_full_score_context():
    """Test with full score context like the actual voice splitter."""
    print("\n=== Testing Full Score Context ===")
    
    # Create a full score with multiple measures like the actual voice splitter
    soprano_part = music21.stream.Part()
    soprano_part.partName = "Soprano"
    soprano_part.insert(0, music21.clef.TrebleClef())
    
    # Add multiple measures (like the actual voice splitter does)
    for measure_num in range(1, 37):  # 36 measures total
        measure = music21.stream.Measure(number=measure_num)
        
        if measure_num == 29:
            # Special handling for measure 29
            note1 = music21.note.Note("G4", quarterLength=3.0)
            note1.offset = 0.0
            note2 = music21.note.Note("G4", quarterLength=1.0)
            note2.offset = 3.0
            
            measure.append(note1)
            measure.append(note2)
            
            # Add dynamic
            dynamic = music21.dynamics.Dynamic('f')
            measure.insert(3.5, dynamic)
        else:
            # Add dummy content for other measures
            note = music21.note.Note("C4", quarterLength=4.0)
            measure.append(note)
        
        soprano_part.append(measure)
    
    # Check measure 29 before file operations
    measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
    measure_29 = measures[28]  # 0-based
    
    print("Measure 29 BEFORE file write (in full score context):")
    notes = list(measure_29.getElementsByClass(music21.note.Note))
    rests = list(measure_29.getElementsByClass(music21.note.Rest))
    print(f"  {len(notes)} notes, {len(rests)} rests")
    for i, note in enumerate(notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    
    # Create score and write to file
    score = music21.stream.Score()
    score.append(soprano_part)
    
    temp_file = "test_full_score.musicxml"
    print(f"\nWriting full score to file: {temp_file}")
    score.write('musicxml', fp=temp_file)
    
    # Read back from file
    print(f"Reading back full score...")
    reloaded_score = music21.converter.parse(temp_file)
    reloaded_part = reloaded_score.parts[0]
    reloaded_measures = list(reloaded_part.getElementsByClass(music21.stream.Measure))
    reloaded_measure_29 = reloaded_measures[28]  # 0-based
    
    print("Measure 29 AFTER file read (in full score context):")
    reloaded_notes = list(reloaded_measure_29.getElementsByClass(music21.note.Note))
    reloaded_rests = list(reloaded_measure_29.getElementsByClass(music21.note.Rest))
    reloaded_dynamics = list(reloaded_measure_29.getElementsByClass(music21.dynamics.Dynamic))
    
    print(f"  {len(reloaded_notes)} notes, {len(reloaded_rests)} rests, {len(reloaded_dynamics)} dynamics")
    for i, note in enumerate(reloaded_notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(reloaded_rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    # Clean up
    Path(temp_file).unlink(missing_ok=True)
    
    # Check for corruption
    corruption_detected = (len(reloaded_rests) > 0 or 
                          (len(reloaded_notes) > 0 and abs(reloaded_notes[0].offset - 0.0) > 0.1))
    
    return corruption_detected


def main():
    corruption1 = test_file_write_read_corruption()
    corruption2 = test_full_score_context()
    
    print(f"\n=== RESULTS ===")
    print(f"Single measure file corruption: {'❌ DETECTED' if corruption1 else '✅ NOT DETECTED'}")
    print(f"Full score file corruption: {'❌ DETECTED' if corruption2 else '✅ NOT DETECTED'}")
    
    if corruption1 or corruption2:
        print("\n🎯 File write/read cycle causes corruption!")
    else:
        print("\n🤔 File write/read cycle does not cause corruption - issue is elsewhere")


if __name__ == "__main__":
    main()