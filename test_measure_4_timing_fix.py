#!/usr/bin/env python3
"""
Test that the timing fix correctly places the eighth rest at beat 3 in measure 4.
"""

import music21
from satb_splitter.voice_splitter import split_satb_voices

def test_measure_4_timing_fix():
    """Test that measure 4 timing is now correct after the fix."""
    print("=== Testing Measure 4 Timing Fix ===")
    
    # Split the voices using the fixed code
    print("\n1. Running voice splitting with timing fix...")
    split_result = split_satb_voices("Crossing The Bar.musicxml")
    
    # Get soprano measure 4
    soprano_score = split_result['Soprano']
    soprano_part = soprano_score.parts[0]
    soprano_measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
    soprano_measure_4 = soprano_measures[3]  # 0-indexed
    
    print(f"\n2. Analyzing fixed Soprano measure 4:")
    print(f"   Measure number: {soprano_measure_4.number}")
    print(f"   Measure duration: {soprano_measure_4.duration.quarterLength}")
    
    # Get all elements with their offsets
    elements = []
    for element in soprano_measure_4.getElementsByClass([music21.note.Note, music21.note.Rest]):
        elements.append((element.offset, element))
    
    # Sort by offset
    elements.sort(key=lambda x: x[0])
    
    print(f"\n3. Fixed Soprano measure 4 elements:")
    eighth_rest_found_at_beat_3 = False
    eighth_rest_found_at_beat_4_5 = False
    
    for offset, element in elements:
        beat = offset + 1  # Convert 0-based offset to 1-based beat
        if isinstance(element, music21.note.Note):
            print(f"   Beat {beat}: Note {element.pitch} (duration: {element.duration.quarterLength})")
        else:
            print(f"   Beat {beat}: Rest (duration: {element.duration.quarterLength})")
            
            # Check if this is the eighth rest and where it's positioned
            if element.duration.quarterLength == 0.5:  # eighth rest
                if beat == 3.0:
                    eighth_rest_found_at_beat_3 = True
                    print(f"     ✓ CORRECT: Eighth rest at beat {beat}")
                elif beat == 4.5:
                    eighth_rest_found_at_beat_4_5 = True
                    print(f"     ✗ PROBLEM: Eighth rest still at beat {beat}")
    
    # Verify the expected sequence
    print(f"\n4. Verification:")
    expected_sequence = [
        (1.0, "Note", "D4", 2.0),    # Half note D4 at beat 1
        (3.0, "Rest", None, 0.5),   # Eighth rest at beat 3
        (3.5, "Note", "D4", 0.5),   # Eighth note D4 at beat 3.5
        (4.0, "Note", "E4", 0.5),   # Eighth note E4 at beat 4
        (4.5, "Note", "F4", 0.5),   # Eighth note F4 at beat 4.5
    ]
    
    sequence_correct = True
    if len(elements) != len(expected_sequence):
        print(f"   ✗ Wrong number of elements: expected {len(expected_sequence)}, got {len(elements)}")
        sequence_correct = False
    else:
        for i, ((actual_offset, actual_element), (expected_beat, expected_type, expected_pitch, expected_duration)) in enumerate(zip(elements, expected_sequence)):
            actual_beat = actual_offset + 1
            actual_type = "Note" if isinstance(actual_element, music21.note.Note) else "Rest"
            actual_duration = actual_element.duration.quarterLength
            
            if actual_beat != expected_beat:
                print(f"   ✗ Element {i}: Wrong beat - expected {expected_beat}, got {actual_beat}")
                sequence_correct = False
            elif actual_type != expected_type:
                print(f"   ✗ Element {i}: Wrong type - expected {expected_type}, got {actual_type}")
                sequence_correct = False
            elif actual_duration != expected_duration:
                print(f"   ✗ Element {i}: Wrong duration - expected {expected_duration}, got {actual_duration}")
                sequence_correct = False
            elif expected_type == "Note":
                actual_pitch = str(actual_element.pitch)
                if actual_pitch != expected_pitch:
                    print(f"   ✗ Element {i}: Wrong pitch - expected {expected_pitch}, got {actual_pitch}")
                    sequence_correct = False
    
    if sequence_correct:
        print(f"   ✓ All elements in correct sequence and timing")
    
    # Final result
    print(f"\n5. Test Result:")
    if eighth_rest_found_at_beat_3 and not eighth_rest_found_at_beat_4_5 and sequence_correct:
        print(f"   ✓ SUCCESS: Measure 4 timing fix is working correctly!")
        print(f"   ✓ Eighth rest is now correctly positioned at beat 3")
        return True
    else:
        print(f"   ✗ FAILURE: Timing issue still exists")
        if eighth_rest_found_at_beat_4_5:
            print(f"   ✗ Eighth rest is still at beat 4.5")
        if not eighth_rest_found_at_beat_3:
            print(f"   ✗ Eighth rest not found at beat 3")
        if not sequence_correct:
            print(f"   ✗ Element sequence is incorrect")
        return False

if __name__ == "__main__":
    success = test_measure_4_timing_fix()
    exit(0 if success else 1)