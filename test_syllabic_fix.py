#!/usr/bin/env python3
"""
Test script to validate that syllabic markings are preserved after the fix.
"""

import music21
import sys
from pathlib import Path

def test_syllabic_preservation():
    """Test that syllabic markings are preserved during voice splitting."""
    print("=== Testing Syllabic Preservation Fix ===")
    
    file_path = "Crossing The Bar.musicxml"
    
    if not Path(file_path).exists():
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    
    # Load original file and extract syllabic information
    print("1. Analyzing original file...")
    score = music21.converter.parse(str(file_path))
    
    original_syllabics = {}
    for part_idx, part in enumerate(score.parts):
        for measure_idx, measure in enumerate(part.getElementsByClass(music21.stream.Measure)):
            # Check both measure-level notes and voice-level notes
            all_notes = list(measure.getElementsByClass(music21.note.Note))
            
            # Also check notes in voices
            for voice in measure.getElementsByClass(music21.stream.Voice):
                all_notes.extend(list(voice.getElementsByClass(music21.note.Note)))
            
            for note in all_notes:
                if hasattr(note, 'lyrics') and note.lyrics:
                    for lyric in note.lyrics:
                        if hasattr(lyric, 'syllabic') and lyric.syllabic in ['begin', 'end']:
                            key = (measure_idx + 1, note.offset, lyric.text)
                            original_syllabics[key] = lyric.syllabic
    
    print(f"   Found {len(original_syllabics)} begin/end syllabic markings in original")
    
    # Show some examples
    examples = list(original_syllabics.items())[:5]
    for (measure, offset, text), syllabic in examples:
        print(f"   Example: Measure {measure}, '{text}' - {syllabic}")
    
    # Run voice splitting with the fix
    print("\n2. Running voice splitting with syllabic fix...")
    sys.path.append('.')
    from satb_splitter.voice_splitter import split_satb_voices
    
    try:
        voices_dict = split_satb_voices(file_path)
        
        # Check syllabic preservation in split voices
        print("\n3. Checking syllabic preservation in split voices...")
        
        preserved_count = 0
        lost_count = 0
        
        for voice_name, voice_score in voices_dict.items():
            part = voice_score.parts[0]
            
            for measure_idx, measure in enumerate(part.getElementsByClass(music21.stream.Measure)):
                for note in measure.getElementsByClass(music21.note.Note):
                    if hasattr(note, 'lyrics') and note.lyrics:
                        for lyric in note.lyrics:
                            key = (measure_idx + 1, note.offset, lyric.text)
                            if key in original_syllabics:
                                expected_syllabic = original_syllabics[key]
                                actual_syllabic = lyric.syllabic if hasattr(lyric, 'syllabic') else 'unknown'
                                
                                if actual_syllabic == expected_syllabic:
                                    preserved_count += 1
                                    print(f"   ✓ {voice_name}: Measure {measure_idx + 1}, '{lyric.text}' - {actual_syllabic} (preserved)")
                                else:
                                    lost_count += 1
                                    print(f"   ✗ {voice_name}: Measure {measure_idx + 1}, '{lyric.text}' - expected {expected_syllabic}, got {actual_syllabic}")
        
        # Summary
        print(f"\n=== Test Results ===")
        print(f"Original begin/end syllabics: {len(original_syllabics)}")
        print(f"Preserved correctly: {preserved_count}")
        print(f"Lost or incorrect: {lost_count}")
        
        if lost_count == 0:
            print("✅ SUCCESS: All syllabic markings preserved correctly!")
        else:
            print(f"❌ FAILURE: {lost_count} syllabic markings were lost or incorrect")
            
        # Test specific examples from measure 1
        print(f"\n=== Measure 1 Specific Test ===")
        soprano_part = voices_dict['Soprano'].parts[0]
        measure_1 = list(soprano_part.getElementsByClass(music21.stream.Measure))[0]
        
        test_cases = [
            (0.0, "Sun", "begin"),
            (1.0, "set", "end"),
            (2.0, "ev", "begin"),
            (3.5, "'ning", "end")
        ]
        
        for offset, expected_text, expected_syllabic in test_cases:
            found = False
            for note in measure_1.getElementsByClass(music21.note.Note):
                if abs(note.offset - offset) < 0.1:
                    if hasattr(note, 'lyrics') and note.lyrics:
                        for lyric in note.lyrics:
                            if lyric.text == expected_text:
                                actual_syllabic = lyric.syllabic if hasattr(lyric, 'syllabic') else 'unknown'
                                if actual_syllabic == expected_syllabic:
                                    print(f"   ✓ Soprano measure 1: '{expected_text}' - {actual_syllabic}")
                                else:
                                    print(f"   ✗ Soprano measure 1: '{expected_text}' - expected {expected_syllabic}, got {actual_syllabic}")
                                found = True
                                break
                    break
            if not found:
                print(f"   ✗ Soprano measure 1: '{expected_text}' - NOT FOUND")
        
        return lost_count == 0
        
    except Exception as e:
        print(f"Error during voice splitting: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_syllabic_preservation()
    sys.exit(0 if success else 1)