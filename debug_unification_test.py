#!/usr/bin/env python3
"""
Targeted test to isolate the dynamics duplication in the unification process.
"""

import sys
import os
from pathlib import Path
import music21

# Add the current directory to Python path
sys.path.insert(0, '.')

from satb_splitter.utils import ProcessingOptions, load_score, ProcessingContext
from satb_splitter.voice_identifier import VoiceIdentifier
from satb_splitter.score_processor import ScoreProcessor
from satb_splitter.contextual_unifier import ContextualUnifier

def analyze_dynamics_detailed(score, voice_name=""):
    """Detailed analysis of all dynamics in a score."""
    print(f"\n--- Detailed dynamics analysis ({voice_name}) ---")
    
    all_dynamics = []
    
    for part_idx, part in enumerate(score.parts):
        print(f"Part {part_idx}:")
        
        for measure in part.getElementsByClass(music21.stream.Measure):
            measure_dynamics = []
            
            # Check all elements in the measure
            for element in measure:
                if isinstance(element, music21.dynamics.Dynamic):
                    dyn_info = {
                        'dynamic': element.value,
                        'offset': element.offset,
                        'measure_number': measure.number,
                        'part_index': part_idx,
                        'element_type': 'Dynamic'
                    }
                    measure_dynamics.append(dyn_info)
                    all_dynamics.append(dyn_info)
                
                # Check for Direction elements containing dynamics
                elif hasattr(element, 'classes') and 'Direction' in element.classes:
                    # This might contain dynamics
                    if hasattr(element, 'dynamicSymbol'):
                        dyn_info = {
                            'dynamic': str(element.dynamicSymbol),
                            'offset': element.offset,
                            'measure_number': measure.number,
                            'part_index': part_idx,
                            'element_type': 'Direction'
                        }
                        measure_dynamics.append(dyn_info)
                        all_dynamics.append(dyn_info)
            
            if measure_dynamics:
                print(f"  Measure {measure.number}: {len(measure_dynamics)} dynamics")
                for dyn in measure_dynamics:
                    print(f"    {dyn['dynamic']} at offset {dyn['offset']} ({dyn['element_type']})")
    
    print(f"Total dynamics in score: {len(all_dynamics)}")
    return all_dynamics

def test_unification_step_by_step():
    """Test the unification process step by step."""
    print("=" * 70)
    print("STEP-BY-STEP UNIFICATION DEBUGGING")
    print("=" * 70)
    
    # Load and prepare
    original_score = load_score("Crossing The Bar.musicxml")
    options = ProcessingOptions(
        apply_dynamics_unification=True,
        apply_lyrics_unification=False,
        apply_spanner_unification=False
    )
    
    # Create voice identifier and mapping
    voice_identifier = VoiceIdentifier(original_score, options)
    voice_mapping = voice_identifier.analyze_score()
    
    # Create context
    context = ProcessingContext(
        original_score=original_score,
        voice_mapping=voice_mapping,
        processing_options=options
    )
    
    # Create voice copies
    processor = ScoreProcessor(options)
    voice_scores = processor.create_voice_copies(original_score)
    
    print("\n--- BEFORE UNIFICATION ---")
    soprano_dynamics_before = analyze_dynamics_detailed(voice_scores['Soprano'], "Soprano Before")
    
    # Create unifier and test individual methods
    unifier = ContextualUnifier(context)
    
    print("\n--- TESTING CROSS-REFERENCE ---")
    cross_ref = unifier.cross_reference_elements(voice_scores)
    print(f"Common dynamics found: {len(cross_ref['common_elements']['dynamics'])}")
    for dyn in cross_ref['common_elements']['dynamics']:
        print(f"  Common: {dyn}")
    
    print(f"Voice-specific elements:")
    for voice, elements in cross_ref['voice_specific_elements'].items():
        print(f"  {voice}: {len(elements)} elements")
        for elem in elements:
            print(f"    {elem}")
    
    print("\n--- TESTING SOPRANO-ONLY DYNAMICS ---")
    soprano_only = unifier._find_soprano_only_dynamics(voice_scores)
    print(f"Soprano-only dynamics found: {len(soprano_only)}")
    for dyn in soprano_only:
        print(f"  Soprano-only: {dyn}")
    
    print("\n--- APPLYING DYNAMICS UNIFICATION ---")
    dynamics_result = unifier.unify_dynamics(voice_scores)
    print(f"Unification result: {dynamics_result}")
    
    print("\n--- AFTER UNIFICATION ---")
    soprano_dynamics_after = analyze_dynamics_detailed(voice_scores['Soprano'], "Soprano After")
    
    # Compare
    print("\n--- COMPARISON ---")
    print(f"Before: {len(soprano_dynamics_before)} dynamics")
    print(f"After: {len(soprano_dynamics_after)} dynamics")
    
    if len(soprano_dynamics_after) > len(soprano_dynamics_before):
        print("🚨 DUPLICATION DETECTED IN UNIFICATION!")
        
        # Find the new dynamics
        before_offsets = {(d['measure_number'], d['offset'], d['dynamic']) for d in soprano_dynamics_before}
        after_offsets = {(d['measure_number'], d['offset'], d['dynamic']) for d in soprano_dynamics_after}
        
        new_dynamics = after_offsets - before_offsets
        print(f"New dynamics added: {new_dynamics}")
        
        return True
    else:
        print("✓ No duplication in unification step")
        return False

def main():
    """Run the targeted unification test."""
    print("🔍 TARGETED UNIFICATION DEBUGGING")
    
    try:
        duplication_found = test_unification_step_by_step()
        
        if duplication_found:
            print("\n" + "=" * 70)
            print("🎯 ROOT CAUSE IDENTIFIED")
            print("=" * 70)
            print("The dynamics duplication occurs in the ContextualUnifier.unify_dynamics() method!")
            return 1
        else:
            print("\n❓ Duplication not found in unification step")
            return 0
            
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    sys.exit(main())