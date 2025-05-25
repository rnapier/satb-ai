#!/usr/bin/env python3
"""
Test the exact sequence used by the voice splitter: dynamics first, then notes.
"""

import music21
import copy


def test_voice_splitter_sequence():
    """Test the exact sequence used by the voice splitter."""
    print("=== TESTING VOICE SPLITTER SEQUENCE ===")
    print("Sequence: Create measure → Add dynamics → Add notes")
    
    # Create measure 29 (like voice splitter does)
    soprano_measure = music21.stream.Measure(number=29)
    
    print("Step 1: Created empty measure 29")
    
    # Step 2: Add measure-level dynamic FIRST (like voice splitter line 221)
    dynamic = music21.dynamics.Dynamic('f')
    soprano_measure.insert(3.5, dynamic)
    
    print("Step 2: Added dynamic 'f' at offset 3.5")
    notes = list(soprano_measure.getElementsByClass(music21.note.Note))
    rests = list(soprano_measure.getElementsByClass(music21.note.Rest))
    dynamics = list(soprano_measure.getElementsByClass(music21.dynamics.Dynamic))
    print(f"  After dynamic: {len(notes)} notes, {len(rests)} rests, {len(dynamics)} dynamics")
    
    # Step 3: Add notes SECOND (like voice splitter lines 270-271)
    note1 = music21.note.Note("G4", quarterLength=3.0)
    note1.offset = 0.0
    note2 = music21.note.Note("G4", quarterLength=1.0)
    note2.offset = 3.0
    
    print("Step 3: Adding notes...")
    print(f"  Adding note1: G4 dur=3.0 offset=0.0")
    soprano_measure.append(copy.deepcopy(note1))
    
    # Check after first note
    notes = list(soprano_measure.getElementsByClass(music21.note.Note))
    rests = list(soprano_measure.getElementsByClass(music21.note.Rest))
    print(f"  After note1: {len(notes)} notes, {len(rests)} rests")
    for i, note in enumerate(notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    print(f"  Adding note2: G4 dur=1.0 offset=3.0")
    soprano_measure.append(copy.deepcopy(note2))
    
    # Check final result
    print("Step 4: Final result")
    notes = list(soprano_measure.getElementsByClass(music21.note.Note))
    rests = list(soprano_measure.getElementsByClass(music21.note.Rest))
    dynamics = list(soprano_measure.getElementsByClass(music21.dynamics.Dynamic))
    
    print(f"  Final: {len(notes)} notes, {len(rests)} rests, {len(dynamics)} dynamics")
    for i, note in enumerate(notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    for i, dyn in enumerate(dynamics):
        print(f"    Dynamic {i+1}: {dyn.value} offset={dyn.offset}")
    
    # Check for corruption
    corruption_detected = len(rests) > 0 or (len(notes) > 0 and abs(notes[0].offset - 0.0) > 0.1)
    
    return corruption_detected


def test_step_by_step_insertion():
    """Test each step of note insertion to see exactly when corruption occurs."""
    print("\n=== STEP-BY-STEP INSERTION TEST ===")
    
    # Create measure with dynamic first
    measure = music21.stream.Measure(number=29)
    dynamic = music21.dynamics.Dynamic('f')
    measure.insert(3.5, dynamic)
    
    print("Starting state: measure with dynamic at 3.5")
    
    # Test inserting note that spans across the dynamic position
    print("\nTesting: Insert note that spans across dynamic position")
    print("Note: G4 dur=3.0 offset=0.0 (spans from 0.0 to 3.0)")
    print("Dynamic: f at offset=3.5")
    print("Question: Does inserting this note cause splitting?")
    
    note1 = music21.note.Note("G4", quarterLength=3.0)
    note1.offset = 0.0
    
    # Check before insertion
    print("\nBEFORE inserting note1:")
    notes = list(measure.getElementsByClass(music21.note.Note))
    rests = list(measure.getElementsByClass(music21.note.Rest))
    print(f"  {len(notes)} notes, {len(rests)} rests")
    
    # Insert the note
    measure.append(note1)
    
    print("\nAFTER inserting note1:")
    notes = list(measure.getElementsByClass(music21.note.Note))
    rests = list(measure.getElementsByClass(music21.note.Rest))
    print(f"  {len(notes)} notes, {len(rests)} rests")
    for i, note in enumerate(notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    # Now add the second note
    print("\nAdding second note: G4 dur=1.0 offset=3.0")
    note2 = music21.note.Note("G4", quarterLength=1.0)
    note2.offset = 3.0
    measure.append(note2)
    
    print("\nFINAL RESULT:")
    notes = list(measure.getElementsByClass(music21.note.Note))
    rests = list(measure.getElementsByClass(music21.note.Rest))
    dynamics = list(measure.getElementsByClass(music21.dynamics.Dynamic))
    
    print(f"  {len(notes)} notes, {len(rests)} rests, {len(dynamics)} dynamics")
    for i, note in enumerate(notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    corruption_detected = len(rests) > 0
    return corruption_detected


def main():
    corruption1 = test_voice_splitter_sequence()
    corruption2 = test_step_by_step_insertion()
    
    print(f"\n=== RESULTS ===")
    print(f"Voice splitter sequence: {'❌ CORRUPTION' if corruption1 else '✅ NO CORRUPTION'}")
    print(f"Step-by-step insertion: {'❌ CORRUPTION' if corruption2 else '✅ NO CORRUPTION'}")
    
    if corruption1 or corruption2:
        print("\n🎯 CORRUPTION REPRODUCED! Found the exact mechanism.")
        print("The issue is: Adding dynamics BEFORE notes causes note splitting when notes span across dynamic positions.")
    else:
        print("\n🤔 Still could not reproduce corruption.")


if __name__ == "__main__":
    main()