#!/usr/bin/env python3
"""
Debug test to reproduce and analyze the duplicate dynamics issue in measure 29.
"""

import sys
import os
from pathlib import Path
import music21

# Add the current directory to Python path
sys.path.insert(0, '.')

from satb_splitter import split_satb_voices
from satb_splitter.utils import load_score
from satb_splitter.voice_identifier import VoiceIdentifier
from satb_splitter.score_processor import ScoreProcessor

def analyze_dynamics_in_measure(score, measure_number, voice_name=""):
    """Analyze dynamics in a specific measure."""
    print(f"\n--- Analyzing dynamics in measure {measure_number} ({voice_name}) ---")
    
    dynamics_found = []
    
    for part_idx, part in enumerate(score.parts):
        print(f"Part {part_idx}:")
        
        for measure in part.getElementsByClass(music21.stream.Measure):
            if measure.number == measure_number:
                print(f"  Measure {measure.number}:")
                
                # Find all dynamics in this measure
                for element in measure.flatten():
                    if isinstance(element, music21.dynamics.Dynamic):
                        dynamics_found.append({
                            'dynamic': element.value,
                            'offset': element.offset,
                            'measure_number': measure.number,
                            'part_index': part_idx
                        })
                        print(f"    Dynamic: {element.value} at offset {element.offset}")
                
                # Also check for direction elements (which contain dynamics)
                for element in measure:
                    if hasattr(element, 'classes') and 'Direction' in element.classes:
                        print(f"    Direction element found at offset {element.offset}")
                        if hasattr(element, 'dynamicSymbol'):
                            print(f"      Contains dynamic: {element.dynamicSymbol}")
    
    print(f"Total dynamics found in measure {measure_number}: {len(dynamics_found)}")
    return dynamics_found

def test_original_score():
    """Test the original score to see how many dynamics are in measure 29."""
    print("=" * 60)
    print("TESTING ORIGINAL SCORE")
    print("=" * 60)
    
    original_score = load_score("Crossing The Bar.musicxml")
    original_dynamics = analyze_dynamics_in_measure(original_score, 29, "Original")
    
    return original_dynamics

def test_processing_pipeline():
    """Test each step of the processing pipeline to see where duplication occurs."""
    print("\n" + "=" * 60)
    print("TESTING PROCESSING PIPELINE")
    print("=" * 60)
    
    # Load original score
    original_score = load_score("Crossing The Bar.musicxml")
    
    # Create processor with default settings
    processor = ScoreProcessor()
    
    print("\n--- Step 1: Voice Identification ---")
    voice_identifier = VoiceIdentifier(original_score)
    voice_mapping = voice_identifier.analyze_score()
    print(f"Voice mapping confidence: {voice_mapping.confidence:.2f}")
    
    print("\n--- Step 2: Creating Voice Copies ---")
    voice_scores = processor.create_voice_copies(original_score)
    
    # Check dynamics in soprano copy before any processing
    print("\n--- Step 3: Dynamics in Soprano Copy (before processing) ---")
    soprano_dynamics_before = analyze_dynamics_in_measure(voice_scores['Soprano'], 29, "Soprano Before Processing")
    
    print("\n--- Step 4: Running Full Processing ---")
    result = processor.process_satb_score("Crossing The Bar.musicxml")
    
    if result.success:
        print("✓ Processing completed successfully")
        print(f"Processing time: {result.processing_time:.2f}s")
        print(f"Warnings: {len(result.warnings)}")
        print(f"Errors: {len(result.errors)}")
        
        if result.warnings:
            print("Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"  - {error}")
    else:
        print("✗ Processing failed")
        return None
    
    print("\n--- Step 5: Dynamics in Final Soprano Score ---")
    final_soprano_dynamics = analyze_dynamics_in_measure(result.voice_scores['Soprano'], 29, "Soprano Final")
    
    return {
        'original': analyze_dynamics_in_measure(original_score, 29, "Original"),
        'soprano_before': soprano_dynamics_before,
        'soprano_final': final_soprano_dynamics,
        'processing_result': result
    }

def compare_dynamics(results):
    """Compare dynamics across different stages."""
    print("\n" + "=" * 60)
    print("DYNAMICS COMPARISON")
    print("=" * 60)
    
    print(f"Original score dynamics in measure 29: {len(results['original'])}")
    for i, dyn in enumerate(results['original']):
        print(f"  {i+1}. {dyn['dynamic']} at offset {dyn['offset']}")
    
    print(f"\nSoprano before processing: {len(results['soprano_before'])}")
    for i, dyn in enumerate(results['soprano_before']):
        print(f"  {i+1}. {dyn['dynamic']} at offset {dyn['offset']}")
    
    print(f"\nSoprano after processing: {len(results['soprano_final'])}")
    for i, dyn in enumerate(results['soprano_final']):
        print(f"  {i+1}. {dyn['dynamic']} at offset {dyn['offset']}")
    
    # Check for duplication
    if len(results['soprano_final']) > len(results['original']):
        print(f"\n🚨 DUPLICATION DETECTED!")
        print(f"Original had {len(results['original'])} dynamics")
        print(f"Final soprano has {len(results['soprano_final'])} dynamics")
        print(f"Extra dynamics: {len(results['soprano_final']) - len(results['original'])}")
        
        return True
    else:
        print(f"\n✓ No duplication detected")
        return False

def main():
    """Run the debug test."""
    print("🪲 DEBUGGING DUPLICATE DYNAMICS IN MEASURE 29")
    print("=" * 60)
    
    try:
        # Test original score
        original_dynamics = test_original_score()
        
        # Test processing pipeline
        results = test_processing_pipeline()
        
        if results:
            # Compare results
            duplication_found = compare_dynamics(results)
            
            if duplication_found:
                print("\n" + "=" * 60)
                print("🎯 DIAGNOSIS CONFIRMED")
                print("=" * 60)
                print("The duplicate dynamics issue has been reproduced!")
                print("The processing pipeline is adding extra dynamics to measure 29.")
                
                # Additional analysis
                print("\nProcessing steps completed:")
                for step in results['processing_result'].processing_steps:
                    print(f"  ✓ {step}")
                
                return 1  # Issue confirmed
            else:
                print("\n❓ Issue not reproduced in this test run")
                return 0
        else:
            print("\n❌ Processing failed, cannot complete analysis")
            return 2
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 3

if __name__ == "__main__":
    sys.exit(main())