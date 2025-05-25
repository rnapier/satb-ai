#!/usr/bin/env python3
"""
Debug script to identify which specific crescendo is being lost.
"""

from music21 import converter
from pathlib import Path
from satb_splitter.main import split_satb_voices
import tempfile

def analyze_crescendo_details():
    """Analyze which crescendos are preserved vs lost."""
    
    original_file = Path("Crossing The Bar.musicxml")
    
    print("=== DETAILED CRESCENDO ANALYSIS ===")
    
    # Load original score
    original_score = converter.parse(str(original_file))
    print("\n=== ORIGINAL SCORE CRESCENDOS ===")
    original_crescendos = []
    for part_idx, part in enumerate(original_score.parts):
        for i, spanner in enumerate(part.getElementsByClass('Spanner')):
            if 'Crescendo' in str(type(spanner)):
                crescendo_info = {
                    'index': i,
                    'type': str(type(spanner)),
                    'repr': str(spanner),
                    'part': part_idx
                }
                print(f"  {len(original_crescendos)}: {crescendo_info['repr']}")
                original_crescendos.append(crescendo_info)
    
    # Process with voice separation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        voices = split_satb_voices(str(original_file), str(temp_path))
        
        # Check in-memory soprano
        soprano_in_memory = voices.get('Soprano')
        print(f"\n=== IN-MEMORY SOPRANO CRESCENDOS ===")
        memory_crescendos = []
        if soprano_in_memory:
            for part in soprano_in_memory.parts:
                for i, spanner in enumerate(part.getElementsByClass('Spanner')):
                    if 'Crescendo' in str(type(spanner)):
                        crescendo_info = {
                            'index': i,
                            'type': str(type(spanner)),
                            'repr': str(spanner)
                        }
                        print(f"  {len(memory_crescendos)}: {crescendo_info['repr']}")
                        memory_crescendos.append(crescendo_info)
        
        # Check saved file
        soprano_file = temp_path / f"{original_file.stem}-Soprano.musicxml"
        if soprano_file.exists():
            soprano_from_file = converter.parse(str(soprano_file))
            print(f"\n=== SAVED FILE CRESCENDOS ===")
            file_crescendos = []
            for part in soprano_from_file.parts:
                for i, spanner in enumerate(part.getElementsByClass('Spanner')):
                    if 'Crescendo' in str(type(spanner)):
                        crescendo_info = {
                            'index': i,
                            'type': str(type(spanner)),
                            'repr': str(spanner)
                        }
                        print(f"  {len(file_crescendos)}: {crescendo_info['repr']}")
                        file_crescendos.append(crescendo_info)
            
            print(f"\n=== COMPARISON ===")
            print(f"Original: {len(original_crescendos)} crescendos")
            print(f"Memory:   {len(memory_crescendos)} crescendos")
            print(f"File:     {len(file_crescendos)} crescendos")
            
            if len(memory_crescendos) > len(file_crescendos):
                print(f"\n❌ LOST DURING EXPORT:")
                print(f"Lost {len(memory_crescendos) - len(file_crescendos)} crescendo(s) during export")
                
                # Try to identify which ones were lost
                memory_reprs = [c['repr'] for c in memory_crescendos]
                file_reprs = [c['repr'] for c in file_crescendos]
                
                for i, memory_repr in enumerate(memory_reprs):
                    if memory_repr not in file_reprs:
                        print(f"  - LOST: {memory_repr}")
                    else:
                        print(f"  - KEPT: {memory_repr}")

if __name__ == "__main__":
    analyze_crescendo_details()