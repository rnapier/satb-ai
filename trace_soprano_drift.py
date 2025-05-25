#!/usr/bin/env python3
"""
Investigate the exact mechanism causing Soprano timing drift.
"""

import music21
import copy
from pathlib import Path

def trace_measure_offsets_during_creation():
    """Trace how measure offsets are calculated during the voice splitting process."""
    print("=== TRACING MEASURE OFFSET CALCULATION ===")
    
    # Load base score
    score = music21.converter.parse('Crossing The Bar-base.musicxml')
    
    # Get all measures from the first part to establish unified measure numbering
    first_part_measures = list(score.parts[0].getElementsByClass(music21.stream.Measure))
    total_measures = len(first_part_measures)
    
    print(f"Total measures in base score: {total_measures}")
    print("\nOriginal measure offsets:")
    for i, measure in enumerate(first_part_measures[25:35]):  # Focus on measures around 29
        measure_num = i + 26
        print(f"  Measure {measure_num}: offset={measure.offset}")
    
    # Simulate the measure creation process from voice_splitter.py
    print(f"\n=== SIMULATING MEASURE CREATION PROCESS ===")
    soprano_measures = []
    for measure_num in range(1, total_measures + 1):
        soprano_measure = music21.stream.Measure(number=measure_num)
        soprano_measures.append(soprano_measure)
        if 26 <= measure_num <= 35:  # Focus on measures around 29
            print(f"Created Soprano measure {measure_num}: offset={soprano_measure.offset}")
    
    return soprano_measures, first_part_measures

def trace_note_copying_process():
    """Trace the note copying process for measures 28-30 to see where timing goes wrong."""
    print(f"\n=== TRACING NOTE COPYING PROCESS ===")
    
    # Load base score
    score = music21.converter.parse('Crossing The Bar-base.musicxml')
    part_0 = score.parts[0]
    
    # Create soprano measures like the voice splitter does
    soprano_measures = []
    for measure_num in range(1, 37):  # 36 total measures
        soprano_measures.append(music21.stream.Measure(number=measure_num))
    
    # Process measures 28, 29, 30 specifically
    for measure_idx in [27, 28, 29]:  # 0-based indices for measures 28, 29, 30
        measure_num = measure_idx + 1
        print(f"\n--- Processing Measure {measure_num} ---")
        
        # Get original measure
        original_measures = list(part_0.getElementsByClass(music21.stream.Measure))
        original_measure = original_measures[measure_idx]
        
        print(f"Original measure {measure_num}:")
        print(f"  Number: {original_measure.number}")
        print(f"  Offset: {original_measure.offset}")
        
        # Get Voice 1 (Soprano)
        voices = list(original_measure.getElementsByClass(music21.stream.Voice))
        voice_1 = None
        for voice in voices:
            if str(voice.id) == '1':
                voice_1 = voice
                break
        
        if voice_1:
            notes = list(voice_1.getElementsByClass(music21.note.Note))
            rests = list(voice_1.getElementsByClass(music21.note.Rest))
            
            print(f"  Voice 1 content: {len(notes)} notes, {len(rests)} rests")
            for i, note in enumerate(notes):
                print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
            for i, rest in enumerate(rests):
                print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
            
            # Get target soprano measure
            soprano_measure = soprano_measures[measure_idx]
            print(f"Target soprano measure {measure_num}:")
            print(f"  Number: {soprano_measure.number}")
            print(f"  Offset: {soprano_measure.offset}")
            
            # Copy notes and rests (simulate the voice splitter process)
            print(f"  Copying notes and rests...")
            for note in notes:
                note_copy = copy.deepcopy(note)
                soprano_measure.append(note_copy)
                print(f"    Copied note: {note_copy.pitch.name}{note_copy.pitch.octave} dur={note_copy.duration.quarterLength} offset={note_copy.offset}")
            
            for rest in rests:
                rest_copy = copy.deepcopy(rest)
                soprano_measure.append(rest_copy)
                print(f"    Copied rest: dur={rest_copy.duration.quarterLength} offset={rest_copy.offset}")
            
            # Check what's in the soprano measure after copying
            soprano_notes = list(soprano_measure.getElementsByClass(music21.note.Note))
            soprano_rests = list(soprano_measure.getElementsByClass(music21.note.Rest))
            
            print(f"  After copying: {len(soprano_notes)} notes, {len(soprano_rests)} rests")
            for i, note in enumerate(soprano_notes):
                print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
            for i, rest in enumerate(soprano_rests):
                print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")

def trace_part_assembly_process():
    """Trace how measures are added to the soprano part and how offsets change."""
    print(f"\n=== TRACING PART ASSEMBLY PROCESS ===")
    
    # Create soprano part like the voice splitter does
    soprano_part = music21.stream.Part()
    soprano_part.partName = "Soprano"
    soprano_part.insert(0, music21.clef.TrebleClef())
    
    # Create some test measures with content
    test_measures = []
    for measure_num in [28, 29, 30]:
        measure = music21.stream.Measure(number=measure_num)
        
        # Add some test notes
        if measure_num == 28:
            measure.append(music21.note.Note("G4", quarterLength=2.0))
            measure.append(music21.note.Note("F#4", quarterLength=2.0))
        elif measure_num == 29:
            measure.append(music21.note.Note("G4", quarterLength=3.0))
            measure.append(music21.note.Note("G4", quarterLength=1.0))
        elif measure_num == 30:
            measure.append(music21.note.Note("A4", quarterLength=1.0))
            measure.append(music21.note.Note("G4", quarterLength=1.0))
            measure.append(music21.note.Note("F4", quarterLength=1.0))
            measure.append(music21.note.Note("G4", quarterLength=1.0))
        
        test_measures.append(measure)
        print(f"Created test measure {measure_num}: offset={measure.offset}")
    
    # Add measures to part one by one and track offset changes
    print(f"\nAdding measures to soprano part:")
    for i, measure in enumerate(test_measures):
        print(f"  Before adding measure {measure.number}: part duration={soprano_part.duration.quarterLength}")
        soprano_part.append(measure)
        print(f"  After adding measure {measure.number}: part duration={soprano_part.duration.quarterLength}")
        print(f"    Measure offset in part: {measure.offset}")
        
        # Check all measures in the part
        part_measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
        print(f"    Part now has {len(part_measures)} measures:")
        for j, part_measure in enumerate(part_measures):
            print(f"      Measure {part_measure.number}: offset={part_measure.offset}")

def trace_dynamics_impact():
    """Trace how dynamics processing affects measure timing."""
    print(f"\n=== TRACING DYNAMICS IMPACT ===")
    
    # Create a test measure with dynamics like measure 29
    test_measure = music21.stream.Measure(number=29)
    
    # Add notes first
    note1 = music21.note.Note("G4", quarterLength=3.0)
    note1.offset = 0.0
    note2 = music21.note.Note("G4", quarterLength=1.0)
    note2.offset = 3.0
    
    test_measure.append(note1)
    test_measure.append(note2)
    
    print(f"Test measure before dynamics:")
    print(f"  Offset: {test_measure.offset}")
    print(f"  Duration: {test_measure.duration.quarterLength}")
    
    notes = list(test_measure.getElementsByClass(music21.note.Note))
    for i, note in enumerate(notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    
    # Add dynamic like the unification process does
    dynamic = music21.dynamics.Dynamic('f')
    test_measure.insert(3.5, dynamic)
    
    print(f"\nTest measure after adding dynamic at offset 3.5:")
    print(f"  Offset: {test_measure.offset}")
    print(f"  Duration: {test_measure.duration.quarterLength}")
    
    notes = list(test_measure.getElementsByClass(music21.note.Note))
    rests = list(test_measure.getElementsByClass(music21.note.Rest))
    dynamics = list(test_measure.getElementsByClass(music21.dynamics.Dynamic))
    
    for i, note in enumerate(notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    for i, dyn in enumerate(dynamics):
        print(f"    Dynamic {i+1}: {dyn.value} offset={dyn.offset}")

def main():
    """Main investigation function."""
    print("=== INVESTIGATING SOPRANO TIMING DRIFT MECHANISM ===")
    
    trace_measure_offsets_during_creation()
    trace_note_copying_process()
    trace_part_assembly_process()
    trace_dynamics_impact()

if __name__ == "__main__":
    main()