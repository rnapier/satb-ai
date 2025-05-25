#!/usr/bin/env python3
"""
Test script for the spanner extractor module.
"""

import sys
from pathlib import Path

# Add the satb_splitter module to the path
sys.path.insert(0, str(Path(__file__).parent))

from satb_splitter.spanner_extractor import extract_spanners_from_score, categorize_spanner_scope, get_voice_assignment_for_spanner
import music21

def test_spanner_extraction():
    """Test spanner extraction on the Crossing The Bar file."""
    test_file = Path("Crossing The Bar.musicxml")
    
    if not test_file.exists():
        print(f"Error: Test file '{test_file}' not found")
        return
    
    print("=== Testing Spanner Extraction ===")
    
    # Load the score
    score = music21.converter.parse(str(test_file))
    
    # Extract spanners
    extracted_spanners = extract_spanners_from_score(score)
    
    # Test results
    print(f"\n=== Extraction Results ===")
    for category, spanners in extracted_spanners.items():
        print(f"{category.capitalize()}: {len(spanners)}")
        
        # Show details for first few spanners in each category
        for i, spanner_info in enumerate(spanners[:3]):
            print(f"  {i+1}. {spanner_info['type']} in {spanner_info['part_name']}")
            if spanner_info.get('voice_id'):
                print(f"     Voice: {spanner_info['voice_id']}")
            if spanner_info.get('spanned_notes'):
                notes = [note['pitch'] for note in spanner_info['spanned_notes']]
                print(f"     Notes: {' -> '.join(notes)}")
            
            # Test voice assignment
            voice_assignment = get_voice_assignment_for_spanner(spanner_info)
            print(f"     Assigned to: {voice_assignment}")
            
            # Test scope categorization
            scope = categorize_spanner_scope(spanner_info, extracted_spanners)
            print(f"     Scope: {scope}")
            print()

def main():
    """Main test function."""
    try:
        test_spanner_extraction()
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()