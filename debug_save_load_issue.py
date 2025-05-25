#!/usr/bin/env python3
"""
Debug script to test if spanners are lost during save/load process.
"""

from music21 import converter
from pathlib import Path
from satb_splitter.main import split_satb_voices
import tempfile

def test_save_load_issue():
    """Test if spanners are lost during save/load process."""
    
    original_file = Path("Crossing The Bar.musicxml")
    
    print("=== TESTING IN-MEMORY vs SAVED FILES ===")
    
    # Create temporary directory and split voices
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Get in-memory scores
        voices = split_satb_voices(str(original_file), str(temp_path))
        soprano_in_memory = voices.get('Soprano')
        
        print("=== IN-MEMORY SOPRANO SCORE ===")
        if soprano_in_memory:
            crescendos_memory = []
            for element in soprano_in_memory.recurse():
                if 'Crescendo' in str(type(element)):
                    crescendos_memory.append(element)
            print(f"Crescendos in memory: {len(crescendos_memory)}")
            
            # Check spanners at part level too
            spanners_memory = []
            for part in soprano_in_memory.parts:
                spanners = part.getElementsByClass('Spanner')
                spanners_memory.extend(spanners)
            print(f"Spanners in memory: {len(spanners_memory)}")
        
        # Load from saved file
        soprano_file = temp_path / f"{original_file.stem}-Soprano.musicxml"
        print(f"\n=== SAVED FILE: {soprano_file} ===")
        
        if soprano_file.exists():
            soprano_from_file = converter.parse(str(soprano_file))
            
            crescendos_file = []
            for element in soprano_from_file.recurse():
                if 'Crescendo' in str(type(element)):
                    crescendos_file.append(element)
            print(f"Crescendos from file: {len(crescendos_file)}")
            
            # Check spanners at part level too
            spanners_file = []
            for part in soprano_from_file.parts:
                spanners = part.getElementsByClass('Spanner')
                spanners_file.extend(spanners)
            print(f"Spanners from file: {len(spanners_file)}")
            
            # Compare
            print(f"\nCOMPARISON:")
            print(f"Memory crescendos: {len(crescendos_memory)}")
            print(f"File crescendos: {len(crescendos_file)}")
            print(f"Memory spanners: {len(spanners_memory)}")
            print(f"File spanners: {len(spanners_file)}")
            
            if len(crescendos_memory) != len(crescendos_file):
                print("❌ CRESCENDOS LOST DURING SAVE/LOAD!")
            else:
                print("✅ Crescendos preserved during save/load")
        else:
            print("Soprano file not found!")

if __name__ == "__main__":
    test_save_load_issue()