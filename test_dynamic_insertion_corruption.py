#!/usr/bin/env python3
"""
Test to confirm that dynamic insertion is causing note corruption.
"""

import music21
import copy


def test_dynamic_insertion_corruption():
    """Test if inserting dynamics causes note splitting."""
    print("=== Testing Dynamic Insertion Corruption ===")
    
    # Create a test measure like measure 29
    measure = music21.stream.Measure(number=29)
    
    # Add the original notes (like in base score)
    note1 = music21.note.Note("G4", quarterLength=3.0)
    note1.offset = 0.0
    note2 = music21.note.Note("G4", quarterLength=1.0)
    note2.offset = 3.0
    
    measure.append(note1)
    measure.append(note2)
    
    print("BEFORE dynamic insertion:")
    notes = list(measure.getElementsByClass(music21.note.Note))
    rests = list(measure.getElementsByClass(music21.note.Rest))
    print(f"  {len(notes)} notes, {len(rests)} rests")
    for i, note in enumerate(notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    # Insert dynamic at offset 3.5 (like the unification process does)
    dynamic = music21.dynamics.Dynamic('f')
    print(f"\nInserting dynamic 'f' at offset 3.5...")
    measure.insert(3.5, dynamic)
    
    print("\nAFTER dynamic insertion:")
    notes = list(measure.getElementsByClass(music21.note.Note))
    rests = list(measure.getElementsByClass(music21.note.Rest))
    dynamics = list(measure.getElementsByClass(music21.dynamics.Dynamic))
    print(f"  {len(notes)} notes, {len(rests)} rests, {len(dynamics)} dynamics")
    for i, note in enumerate(notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    for i, dyn in enumerate(dynamics):
        print(f"    Dynamic {i+1}: {dyn.value} offset={dyn.offset}")
    
    # Check if corruption occurred
    if len(rests) > 0:
        print("\n❌ CORRUPTION CONFIRMED: Unexpected rests created by dynamic insertion!")
        return True
    else:
        print("\n✅ No corruption detected")
        return False


def test_safe_dynamic_insertion():
    """Test safer methods of dynamic insertion."""
    print("\n=== Testing Safe Dynamic Insertion Methods ===")
    
    # Method 1: Append with explicit offset
    print("\n--- Method 1: Append with explicit offset ---")
    measure1 = music21.stream.Measure(number=29)
    
    note1 = music21.note.Note("G4", quarterLength=3.0)
    note1.offset = 0.0
    note2 = music21.note.Note("G4", quarterLength=1.0)
    note2.offset = 3.0
    
    measure1.append(note1)
    measure1.append(note2)
    
    # Safe method: append with explicit offset
    dynamic1 = music21.dynamics.Dynamic('f')
    dynamic1.offset = 3.5
    measure1.append(dynamic1)
    
    notes = list(measure1.getElementsByClass(music21.note.Note))
    rests = list(measure1.getElementsByClass(music21.note.Rest))
    dynamics = list(measure1.getElementsByClass(music21.dynamics.Dynamic))
    
    print(f"Result: {len(notes)} notes, {len(rests)} rests, {len(dynamics)} dynamics")
    corruption1 = len(rests) > 0
    
    # Method 2: Insert at end of measure
    print("\n--- Method 2: Insert at end of measure ---")
    measure2 = music21.stream.Measure(number=29)
    
    note1 = music21.note.Note("G4", quarterLength=3.0)
    note1.offset = 0.0
    note2 = music21.note.Note("G4", quarterLength=1.0)
    note2.offset = 3.0
    
    measure2.append(note1)
    measure2.append(note2)
    
    # Safe method: insert at end
    dynamic2 = music21.dynamics.Dynamic('f')
    measure2.insert(4.0, dynamic2)  # Insert after all notes
    
    notes = list(measure2.getElementsByClass(music21.note.Note))
    rests = list(measure2.getElementsByClass(music21.note.Rest))
    dynamics = list(measure2.getElementsByClass(music21.dynamics.Dynamic))
    
    print(f"Result: {len(notes)} notes, {len(rests)} rests, {len(dynamics)} dynamics")
    corruption2 = len(rests) > 0
    
    if not corruption1 and not corruption2:
        print("\n✅ Safe insertion methods work!")
        return True
    else:
        print(f"\n❌ Corruption detected: Method 1={corruption1}, Method 2={corruption2}")
        return False


def main():
    corruption_confirmed = test_dynamic_insertion_corruption()
    safe_methods_work = test_safe_dynamic_insertion()
    
    print(f"\n=== RESULTS ===")
    print(f"Dynamic insertion causes corruption: {'✅ CONFIRMED' if corruption_confirmed else '❌ NOT CONFIRMED'}")
    print(f"Safe insertion methods available: {'✅ YES' if safe_methods_work else '❌ NO'}")
    
    if corruption_confirmed and safe_methods_work:
        print("\n🎯 SOLUTION: Use safe dynamic insertion methods to prevent note corruption!")


if __name__ == "__main__":
    main()