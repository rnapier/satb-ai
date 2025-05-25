#!/usr/bin/env python3
"""
Reproduce the exact note splitting corruption seen in measure 29.
"""

import music21
import copy
from pathlib import Path


def reproduce_measure_append_corruption():
    """Try to reproduce the corruption during measure append process."""
    print("=== REPRODUCING MEASURE APPEND CORRUPTION ===")
    
    # Create a soprano part like the voice splitter does
    soprano_part = music21.stream.Part()
    soprano_part.partName = "Soprano"
    soprano_part.insert(0, music21.clef.TrebleClef())
    
    # Add measures 1-28 first (to simulate the actual context)
    print("Adding measures 1-28...")
    for measure_num in range(1, 29):
        measure = music21.stream.Measure(number=measure_num)
        # Add dummy content
        note = music21.note.Note("C4", quarterLength=4.0)
        measure.append(note)
        soprano_part.append(measure)
    
    print(f"Part duration after 28 measures: {soprano_part.duration.quarterLength}")
    
    # Create measure 29 with the exact content from base score
    print("\nCreating measure 29...")
    measure_29 = music21.stream.Measure(number=29)
    
    # Add the original notes (like in base score Voice 1)
    note1 = music21.note.Note("G4", quarterLength=3.0)
    note1.offset = 0.0
    note2 = music21.note.Note("G4", quarterLength=1.0)
    note2.offset = 3.0
    
    measure_29.append(note1)
    measure_29.append(note2)
    
    print("Measure 29 BEFORE adding to part:")
    notes = list(measure_29.getElementsByClass(music21.note.Note))
    rests = list(measure_29.getElementsByClass(music21.note.Rest))
    print(f"  {len(notes)} notes, {len(rests)} rests")
    for i, note in enumerate(notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    
    # Add dynamic BEFORE appending to part (like unification does)
    dynamic = music21.dynamics.Dynamic('f')
    measure_29.insert(3.5, dynamic)
    
    print("Measure 29 AFTER adding dynamic:")
    notes = list(measure_29.getElementsByClass(music21.note.Note))
    rests = list(measure_29.getElementsByClass(music21.note.Rest))
    dynamics = list(measure_29.getElementsByClass(music21.dynamics.Dynamic))
    print(f"  {len(notes)} notes, {len(rests)} rests, {len(dynamics)} dynamics")
    for i, note in enumerate(notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    # Now append to part (this might cause corruption)
    print(f"\nPart duration before appending measure 29: {soprano_part.duration.quarterLength}")
    soprano_part.append(measure_29)
    print(f"Part duration after appending measure 29: {soprano_part.duration.quarterLength}")
    
    # Check measure 29 in the part
    part_measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
    part_measure_29 = part_measures[28]  # 0-based
    
    print("Measure 29 AFTER appending to part:")
    part_notes = list(part_measure_29.getElementsByClass(music21.note.Note))
    part_rests = list(part_measure_29.getElementsByClass(music21.note.Rest))
    part_dynamics = list(part_measure_29.getElementsByClass(music21.dynamics.Dynamic))
    
    print(f"  {len(part_notes)} notes, {len(part_rests)} rests, {len(part_dynamics)} dynamics")
    for i, note in enumerate(part_notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(part_rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    for i, dyn in enumerate(part_dynamics):
        print(f"    Dynamic {i+1}: {dyn.value} offset={dyn.offset}")
    
    # Check for corruption
    corruption_detected = len(part_rests) > 0 or (len(part_notes) > 0 and abs(part_notes[0].offset - 0.0) > 0.1)
    
    return corruption_detected


def test_different_append_orders():
    """Test different orders of operations to isolate the corruption."""
    print("\n=== TESTING DIFFERENT APPEND ORDERS ===")
    
    results = {}
    
    # Test 1: Add notes, then dynamic, then append to part
    print("\n--- Test 1: Notes → Dynamic → Append ---")
    part1 = music21.stream.Part()
    part1.partName = "Test1"
    
    measure1 = music21.stream.Measure(number=29)
    note1 = music21.note.Note("G4", quarterLength=3.0)
    note2 = music21.note.Note("G4", quarterLength=1.0)
    note1.offset = 0.0
    note2.offset = 3.0
    
    measure1.append(note1)
    measure1.append(note2)
    
    dynamic1 = music21.dynamics.Dynamic('f')
    measure1.insert(3.5, dynamic1)
    
    part1.append(measure1)
    
    final_measure1 = list(part1.getElementsByClass(music21.stream.Measure))[0]
    notes1 = list(final_measure1.getElementsByClass(music21.note.Note))
    rests1 = list(final_measure1.getElementsByClass(music21.note.Rest))
    
    results['test1'] = len(rests1) > 0
    print(f"  Result: {len(notes1)} notes, {len(rests1)} rests - Corruption: {results['test1']}")
    
    # Test 2: Add notes, append to part, then add dynamic
    print("\n--- Test 2: Notes → Append → Dynamic ---")
    part2 = music21.stream.Part()
    part2.partName = "Test2"
    
    measure2 = music21.stream.Measure(number=29)
    note1 = music21.note.Note("G4", quarterLength=3.0)
    note2 = music21.note.Note("G4", quarterLength=1.0)
    note1.offset = 0.0
    note2.offset = 3.0
    
    measure2.append(note1)
    measure2.append(note2)
    
    part2.append(measure2)
    
    # Add dynamic after appending
    final_measure2 = list(part2.getElementsByClass(music21.stream.Measure))[0]
    dynamic2 = music21.dynamics.Dynamic('f')
    final_measure2.insert(3.5, dynamic2)
    
    notes2 = list(final_measure2.getElementsByClass(music21.note.Note))
    rests2 = list(final_measure2.getElementsByClass(music21.note.Rest))
    
    results['test2'] = len(rests2) > 0
    print(f"  Result: {len(notes2)} notes, {len(rests2)} rests - Corruption: {results['test2']}")
    
    # Test 3: Create empty measure, append to part, then add content
    print("\n--- Test 3: Empty → Append → Content ---")
    part3 = music21.stream.Part()
    part3.partName = "Test3"
    
    measure3 = music21.stream.Measure(number=29)
    part3.append(measure3)
    
    # Add content after appending
    final_measure3 = list(part3.getElementsByClass(music21.stream.Measure))[0]
    
    note1 = music21.note.Note("G4", quarterLength=3.0)
    note2 = music21.note.Note("G4", quarterLength=1.0)
    note1.offset = 0.0
    note2.offset = 3.0
    
    final_measure3.append(note1)
    final_measure3.append(note2)
    
    dynamic3 = music21.dynamics.Dynamic('f')
    final_measure3.insert(3.5, dynamic3)
    
    notes3 = list(final_measure3.getElementsByClass(music21.note.Note))
    rests3 = list(final_measure3.getElementsByClass(music21.note.Rest))
    
    results['test3'] = len(rests3) > 0
    print(f"  Result: {len(notes3)} notes, {len(rests3)} rests - Corruption: {results['test3']}")
    
    return results


def main():
    corruption1 = reproduce_measure_append_corruption()
    test_results = test_different_append_orders()
    
    print(f"\n=== RESULTS ===")
    print(f"Full context reproduction: {'❌ CORRUPTION' if corruption1 else '✅ NO CORRUPTION'}")
    print(f"Test 1 (Notes→Dynamic→Append): {'❌ CORRUPTION' if test_results['test1'] else '✅ NO CORRUPTION'}")
    print(f"Test 2 (Notes→Append→Dynamic): {'❌ CORRUPTION' if test_results['test2'] else '✅ NO CORRUPTION'}")
    print(f"Test 3 (Empty→Append→Content): {'❌ CORRUPTION' if test_results['test3'] else '✅ NO CORRUPTION'}")
    
    if any([corruption1] + list(test_results.values())):
        print("\n🎯 CORRUPTION REPRODUCED! Found the exact mechanism.")
    else:
        print("\n🤔 Could not reproduce corruption - need to investigate further.")


if __name__ == "__main__":
    main()