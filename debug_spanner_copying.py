#!/usr/bin/env python3
"""
Debug script to test if spanners are being copied properly.
"""

from music21 import converter
from pathlib import Path
from satb_splitter.main import split_satb_voices
import tempfile

def test_spanner_copying():
    """Test if spanners are being copied during voice separation."""
    
    # Load original score
    original_file = Path("Crossing The Bar.musicxml")
    original_score = converter.parse(str(original_file))
    
    print("=== ORIGINAL SCORE SPANNERS ===")
    for part_idx, part in enumerate(original_score.parts):
        spanners = part.getElementsByClass('Spanner')
        print(f"Part {part_idx}: {len(spanners)} spanners")
        for spanner in spanners:
            print(f"  - {spanner} (type: {type(spanner)})")
    
    print("\n=== PROCESSING WITH VOICE SEPARATION ===")
    
    # Create temporary directory and split voices
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        voices = split_satb_voices(str(original_file), str(temp_path))
        
        print(f"Voices created: {list(voices.keys())}")
        
        # Check soprano voice
        soprano_score = voices.get('Soprano')
        if soprano_score:
            print(f"\n=== SOPRANO SCORE SPANNERS ===")
            for part_idx, part in enumerate(soprano_score.parts):
                spanners = part.getElementsByClass('Spanner')
                print(f"Part {part_idx}: {len(spanners)} spanners")
                for spanner in spanners:
                    print(f"  - {spanner} (type: {type(spanner)})")
            
            # Also check if any crescendos exist in the entire soprano score
            all_crescendos = []
            for element in soprano_score.recurse():
                if 'Crescendo' in str(type(element)):
                    all_crescendos.append(element)
            
            print(f"\nTotal crescendos found in entire soprano score: {len(all_crescendos)}")
            for cresc in all_crescendos:
                print(f"  - {cresc}")
        
        else:
            print("No Soprano voice found!")

if __name__ == "__main__":
    test_spanner_copying()