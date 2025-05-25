#!/usr/bin/env python3
"""
Debug script to find exactly where crescendos are located in the original score.
"""

from music21 import converter
from pathlib import Path

def find_crescendo_locations(file_path):
    """Find exactly where crescendos are located in the score structure."""
    score = converter.parse(str(file_path))
    
    print(f"=== Finding Crescendo Locations in {file_path} ===")
    
    # Search for crescendos at different levels
    crescendos_found = []
    
    # 1. Search at score level
    print("\n=== Score Level ===")
    for element in score:
        if 'Crescendo' in str(type(element)):
            print(f"FOUND CRESCENDO AT SCORE LEVEL: {element}")
            crescendos_found.append({
                'level': 'score',
                'element': element
            })
    
    # 2. Search at part level (but not recursive into measures)
    print("\n=== Part Level ===")
    for part_idx, part in enumerate(score.parts):
        print(f"\nPart {part_idx}: {part}")
        
        for element in part:
            if 'Crescendo' in str(type(element)):
                print(f"  FOUND CRESCENDO AT PART LEVEL: {element}")
                print(f"  Type: {type(element)}")
                print(f"  Offset: {element.offset}")
                if hasattr(element, 'noteStart') and hasattr(element, 'noteEnd'):
                    print(f"  Note start: {element.noteStart}")
                    print(f"  Note end: {element.noteEnd}")
                
                crescendos_found.append({
                    'level': 'part',
                    'part_idx': part_idx,
                    'element': element,
                    'offset': element.offset
                })
    
    # 3. Also check spanners specifically
    print("\n=== Spanner Check ===")
    for part_idx, part in enumerate(score.parts):
        spanners = part.getElementsByClass('Spanner')
        print(f"Part {part_idx} spanners: {len(spanners)}")
        for spanner in spanners:
            print(f"  Spanner: {spanner} (type: {type(spanner)})")
            if 'Crescendo' in str(type(spanner)):
                print(f"  ** CRESCENDO SPANNER FOUND **")
                crescendos_found.append({
                    'level': 'spanner',
                    'part_idx': part_idx,
                    'element': spanner
                })
    
    # 4. Check for any spanners throughout the score
    print("\n=== All Spanners in Score ===")
    all_spanners = score.getElementsByClass('Spanner')
    print(f"Total spanners in score: {len(all_spanners)}")
    for spanner in all_spanners:
        print(f"  {spanner} (type: {type(spanner)})")
    
    print(f"\n=== Summary ===")
    print(f"Total crescendos found: {len(crescendos_found)}")
    for i, cresc_info in enumerate(crescendos_found):
        print(f"  {i+1}. Level: {cresc_info['level']}")
        if 'part_idx' in cresc_info:
            print(f"      Part: {cresc_info['part_idx']}")
        if 'offset' in cresc_info:
            print(f"      Offset: {cresc_info['offset']}")
        print(f"      Element: {cresc_info['element']}")

def main():
    """Main analysis function."""
    
    # Analyze original file
    original_file = Path("Crossing The Bar.musicxml")
    if original_file.exists():
        find_crescendo_locations(original_file)
    else:
        print(f"Original file {original_file} not found")

if __name__ == "__main__":
    main()