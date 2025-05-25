#!/usr/bin/env python3
"""
Simple test to validate the new SATB splitter implementation.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, '.')

from satb_splitter import split_satb_voices
from satb_splitter.utils import ProcessingOptions

def test_basic_functionality():
    """Test basic functionality with the test file."""
    print("Testing new SATB splitter implementation...")
    
    # Test with MusicXML file
    test_file = "Crossing The Bar.musicxml"
    if not Path(test_file).exists():
        print(f"Test file {test_file} not found")
        return False
    
    try:
        # Test with default options
        options = ProcessingOptions()
        voice_scores = split_satb_voices(test_file, options=options)
        
        # Validate results
        expected_voices = ['Soprano', 'Alto', 'Tenor', 'Bass']
        
        print(f"✓ Successfully processed {test_file}")
        print(f"✓ Generated {len(voice_scores)} voice parts")
        
        for voice in expected_voices:
            if voice not in voice_scores:
                print(f"✗ Missing voice: {voice}")
                return False
            
            score = voice_scores[voice]
            note_count = len(score.flatten().notes)
            part_count = len(score.parts)
            
            print(f"✓ {voice}: {note_count} notes, {part_count} part(s)")
            
            if note_count == 0:
                print(f"✗ {voice} has no notes")
                return False
        
        print("✓ All voices have musical content")
        print("✓ Test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_voice_detection():
    """Test voice detection capabilities."""
    print("\nTesting voice detection...")
    
    try:
        from satb_splitter.voice_identifier import VoiceIdentifier
        from satb_splitter.utils import load_score
        
        test_file = "Crossing The Bar.musicxml"
        score = load_score(test_file)
        options = ProcessingOptions()
        
        identifier = VoiceIdentifier(score, options)
        voice_mapping = identifier.analyze_score()
        
        print(f"✓ Voice detection confidence: {voice_mapping.confidence:.2f}")
        print(f"✓ Soprano: Part {voice_mapping.soprano.part_index}, Voice {voice_mapping.soprano.voice_id}")
        print(f"✓ Alto: Part {voice_mapping.alto.part_index}, Voice {voice_mapping.alto.voice_id}")
        print(f"✓ Tenor: Part {voice_mapping.tenor.part_index}, Voice {voice_mapping.tenor.voice_id}")
        print(f"✓ Bass: Part {voice_mapping.bass.part_index}, Voice {voice_mapping.bass.voice_id}")
        
        if voice_mapping.validate():
            print("✓ Voice mapping is valid")
            return True
        else:
            print("✗ Voice mapping validation failed")
            return False
            
    except Exception as e:
        print(f"✗ Voice detection test failed: {e}")
        return False

def test_processing_options():
    """Test different processing options."""
    print("\nTesting processing options...")
    
    try:
        test_file = "Crossing The Bar.musicxml"
        
        # Test with unification disabled
        options = ProcessingOptions(
            apply_dynamics_unification=False,
            apply_lyrics_unification=False,
            apply_spanner_unification=False
        )
        
        voice_scores = split_satb_voices(test_file, options=options)
        print("✓ Processing with unification disabled works")
        
        # Test with validation disabled
        options = ProcessingOptions(validate_output=False)
        voice_scores = split_satb_voices(test_file, options=options)
        print("✓ Processing with validation disabled works")
        
        return True
        
    except Exception as e:
        print(f"✗ Processing options test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("SATB Splitter V2 Implementation Test")
    print("=" * 50)
    
    tests = [
        test_basic_functionality,
        test_voice_detection,
        test_processing_options
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Implementation is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())