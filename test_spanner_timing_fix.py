#!/usr/bin/env python3
"""
Test the spanner timing corruption fix.
"""

import music21
from pathlib import Path
from satb_splitter.voice_splitter import split_satb_voices


def test_measure_29_corruption_fix():
    """Test that measure 29 corruption is fixed."""
    print("=== Testing Measure 29 Corruption Fix ===")
    
    # Run voice splitter with enhanced timing validation
    print("Running voice splitter with timing validation...")
    voices = split_satb_voices("Crossing The Bar.mscz")
    
    # Check measure 29 in Soprano
    print("\nValidating Soprano measure 29...")
    soprano_part = voices['Soprano'].parts[0]
    measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
    measure_29 = measures[28]  # 0-based
    
    notes = list(measure_29.getElementsByClass(music21.note.Note))
    rests = list(measure_29.getElementsByClass(music21.note.Rest))
    
    print(f"Measure 29 content: {len(notes)} notes, {len(rests)} rests")
    
    # Validate correct timing
    success = True
    
    if len(notes) != 2:
        print(f"❌ FAIL: Expected 2 notes, got {len(notes)}")
        success = False
    else:
        print(f"✅ PASS: Found expected 2 notes")
    
    if len(rests) != 0:
        print(f"❌ FAIL: Expected 0 rests, got {len(rests)}")
        success = False
    else:
        print(f"✅ PASS: No unexpected rests found")
    
    # Check note timing
    if len(notes) >= 1:
        note1 = notes[0]
        expected_offset = 0.0
        expected_duration = 3.0
        
        if abs(note1.offset - expected_offset) > 0.1:
            print(f"❌ FAIL: First note offset should be {expected_offset}, got {note1.offset}")
            success = False
        else:
            print(f"✅ PASS: First note offset correct ({note1.offset})")
        
        if abs(note1.duration.quarterLength - expected_duration) > 0.1:
            print(f"❌ FAIL: First note duration should be {expected_duration}, got {note1.duration.quarterLength}")
            success = False
        else:
            print(f"✅ PASS: First note duration correct ({note1.duration.quarterLength})")
    
    if len(notes) >= 2:
        note2 = notes[1]
        expected_offset = 3.0
        expected_duration = 1.0
        
        if abs(note2.offset - expected_offset) > 0.1:
            print(f"❌ FAIL: Second note offset should be {expected_offset}, got {note2.offset}")
            success = False
        else:
            print(f"✅ PASS: Second note offset correct ({note2.offset})")
        
        if abs(note2.duration.quarterLength - expected_duration) > 0.1:
            print(f"❌ FAIL: Second note duration should be {expected_duration}, got {note2.duration.quarterLength}")
            success = False
        else:
            print(f"✅ PASS: Second note duration correct ({note2.duration.quarterLength})")
    
    # Print detailed note information
    print(f"\nDetailed note information:")
    for i, note in enumerate(notes):
        print(f"  Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    
    for i, rest in enumerate(rests):
        print(f"  Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    return success


def test_no_regression_other_measures():
    """Test that other measures are not affected by the fix."""
    print("\n=== Testing No Regression in Other Measures ===")
    
    # Test a few key measures to ensure no regression
    test_measures = [1, 10, 20, 28, 30, 35]
    
    voices = split_satb_voices("Crossing The Bar.mscz")
    
    success = True
    for voice_name, voice_score in voices.items():
        voice_part = voice_score.parts[0]
        measures = list(voice_part.getElementsByClass(music21.stream.Measure))
        
        print(f"\nChecking {voice_name}:")
        for measure_num in test_measures:
            if measure_num <= len(measures):
                measure = measures[measure_num - 1]  # 0-based
                notes = list(measure.getElementsByClass(music21.note.Note))
                rests = list(measure.getElementsByClass(music21.note.Rest))
                
                # Basic sanity checks
                if len(notes) == 0 and len(rests) == 0:
                    print(f"  ❌ Measure {measure_num}: No content found")
                    success = False
                else:
                    print(f"  ✅ Measure {measure_num}: {len(notes)} notes, {len(rests)} rests")
    
    return success


def test_measure_30_fix():
    """Test that measure 30 is also fixed (cumulative corruption)."""
    print("\n=== Testing Measure 30 Fix ===")
    
    voices = split_satb_voices("Crossing The Bar.mscz")
    
    # Check measure 30 in Soprano
    soprano_part = voices['Soprano'].parts[0]
    measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
    measure_30 = measures[29]  # 0-based
    
    notes = list(measure_30.getElementsByClass(music21.note.Note))
    rests = list(measure_30.getElementsByClass(music21.note.Rest))
    
    print(f"Measure 30 content: {len(notes)} notes, {len(rests)} rests")
    
    success = True
    
    # Expected: 4 notes (F5, E5, D5, C5) at offsets 0, 1, 2, 3
    if len(notes) != 4:
        print(f"❌ FAIL: Expected 4 notes, got {len(notes)}")
        success = False
    else:
        print(f"✅ PASS: Found expected 4 notes")
    
    if len(rests) != 0:
        print(f"❌ FAIL: Expected 0 rests, got {len(rests)}")
        success = False
    else:
        print(f"✅ PASS: No unexpected rests found")
    
    # Check note timing
    expected_offsets = [0.0, 1.0, 2.0, 3.0]
    for i, (note, expected_offset) in enumerate(zip(notes, expected_offsets)):
        if abs(note.offset - expected_offset) > 0.1:
            print(f"❌ FAIL: Note {i+1} offset should be {expected_offset}, got {note.offset}")
            success = False
        else:
            print(f"✅ PASS: Note {i+1} offset correct ({note.offset})")
    
    # Print detailed note information
    print(f"\nDetailed note information:")
    for i, note in enumerate(notes):
        print(f"  Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    
    return success


def main():
    """Run all tests."""
    print("Running spanner timing corruption fix tests...")
    
    test1_success = test_measure_29_corruption_fix()
    test2_success = test_no_regression_other_measures()
    test3_success = test_measure_30_fix()
    
    print(f"\n=== TEST RESULTS ===")
    print(f"Measure 29 fix: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"No regression: {'✅ PASS' if test2_success else '❌ FAIL'}")
    print(f"Measure 30 fix: {'✅ PASS' if test3_success else '❌ FAIL'}")
    
    overall_success = test1_success and test2_success and test3_success
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success


if __name__ == "__main__":
    main()