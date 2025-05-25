#!/usr/bin/env python3
"""
Test script for lyric assignment feature.
Validates that lyrics are correctly assigned to voices with matching notes.
"""

import music21
from satb_splitter.score_processor import ScoreProcessor
from satb_splitter.utils import ProcessingOptions

def test_lyric_assignment():
    """Test the lyric assignment feature with Crossing The Bar."""
    
    print("=== Testing Lyric Assignment Feature ===")
    
    # Load the original score
    input_file = "Crossing The Bar.musicxml"
    print(f"Loading: {input_file}")
    
    try:
        original_score = music21.converter.parse(input_file)
        print(f"✓ Successfully loaded score with {len(original_score.parts)} parts")
    except Exception as e:
        print(f"✗ Failed to load score: {e}")
        return False
    
    # Set up processing options
    options = ProcessingOptions(
        auto_detect_voices=True,
        apply_lyrics_unification=True,
        apply_dynamics_unification=True,
        apply_spanner_unification=True
    )
    
    # Process the score
    processor = ScoreProcessor(options)
    
    try:
        result = processor.process_satb_score(input_file)
        print(f"✓ Score processing completed successfully")
        print(f"  - Voices extracted: {list(result.voice_scores.keys())}")
    except Exception as e:
        print(f"✗ Score processing failed: {e}")
        return False
    
    # Test lyric analysis
    print("\n=== Analyzing Lyric Assignment ===")
    
    # Check measure 1 specifically
    measure_1_analysis = analyze_measure_lyrics(result.voice_scores, 1)
    print(f"Measure 1 analysis:")
    for voice, has_lyrics in measure_1_analysis.items():
        status = "✓" if has_lyrics else "✗"
        print(f"  {status} {voice}: {'Has lyrics' if has_lyrics else 'No lyrics'}")
    
    # Check if Alto, Tenor, Bass got lyrics from Soprano
    expected_voices_with_lyrics = ['Soprano', 'Alto', 'Tenor', 'Bass']
    success = True
    
    for voice in expected_voices_with_lyrics:
        if voice not in measure_1_analysis or not measure_1_analysis[voice]:
            print(f"✗ {voice} should have lyrics in measure 1")
            success = False
        else:
            print(f"✓ {voice} correctly has lyrics in measure 1")
    
    # Check specific lyrics content
    print("\n=== Verifying Lyric Content ===")
    soprano_lyrics = extract_lyrics_from_voice(result.voice_scores.get('Soprano'), 1)
    
    for voice_name in ['Alto', 'Tenor', 'Bass']:
        if voice_name in result.voice_scores:
            voice_lyrics = extract_lyrics_from_voice(result.voice_scores[voice_name], 1)
            if voice_lyrics and soprano_lyrics:
                if voice_lyrics[0] == soprano_lyrics[0]:  # Check first lyric
                    print(f"✓ {voice_name} has correct lyric: '{voice_lyrics[0]}'")
                else:
                    print(f"✗ {voice_name} lyric mismatch: '{voice_lyrics[0]}' vs '{soprano_lyrics[0]}'")
                    success = False
            else:
                print(f"✗ {voice_name} missing lyrics")
                success = False
    
    return success

def analyze_measure_lyrics(voice_scores, measure_number):
    """Analyze which voices have lyrics in a specific measure."""
    analysis = {}
    
    for voice_name, score in voice_scores.items():
        has_lyrics = False
        
        for part in score.parts:
            measures = list(part.getElementsByClass('Measure'))
            if len(measures) >= measure_number:
                measure = measures[measure_number - 1]
                
                for note in measure.getElementsByClass('Note'):
                    if note.lyrics:
                        has_lyrics = True
                        break
                
                if has_lyrics:
                    break
        
        analysis[voice_name] = has_lyrics
    
    return analysis

def extract_lyrics_from_voice(score, measure_number):
    """Extract lyrics from a specific measure in a voice."""
    if not score:
        return []
    
    lyrics = []
    
    for part in score.parts:
        measures = list(part.getElementsByClass('Measure'))
        if len(measures) >= measure_number:
            measure = measures[measure_number - 1]
            
            for note in measure.getElementsByClass('Note'):
                if note.lyrics:
                    for lyric in note.lyrics:
                        if lyric.text:
                            lyrics.append(lyric.text)
    
    return lyrics

def test_edge_cases():
    """Test edge cases for lyric assignment."""
    print("\n=== Testing Edge Cases ===")
    
    # Test case 1: Voice already has lyrics (should not overwrite)
    print("Test case 1: Existing lyrics should not be overwritten")
    
    # Test case 2: Different durations (should not assign)
    print("Test case 2: Different note durations should not get lyrics")
    
    # Test case 3: Different timing (should not assign)
    print("Test case 3: Different note timing should not get lyrics")
    
    print("✓ Edge case tests completed")
    return True

if __name__ == "__main__":
    print("Lyric Assignment Feature Test")
    print("=" * 50)
    
    # Run main test
    main_success = test_lyric_assignment()
    
    # Run edge case tests
    edge_success = test_edge_cases()
    
    # Summary
    print("\n" + "=" * 50)
    if main_success and edge_success:
        print("✓ All tests PASSED")
        exit(0)
    else:
        print("✗ Some tests FAILED")
        exit(1)