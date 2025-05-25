#!/usr/bin/env python3
"""
Test script for the comprehensive spanner handling fix.
"""

from music21 import converter
from pathlib import Path
from satb_splitter.main import split_satb_voices
import tempfile

def test_comprehensive_spanner_processing():
    """Test the new comprehensive spanner processing system."""
    
    original_file = Path("Crossing The Bar.musicxml")
    
    if not original_file.exists():
        print("❌ Sample score file not found")
        return
    
    print("=== TESTING COMPREHENSIVE SPANNER PROCESSING ===")
    
    # Process with new system
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        voices = split_satb_voices(str(original_file), str(temp_path))
        
        print(f"\n=== RESULTS ===")
        for voice_name in ['Soprano', 'Alto', 'Tenor', 'Bass']:
            if voice_name in voices:
                voice_score = voices[voice_name]
                
                # Count spanners in memory
                memory_spanners = []
                for part in voice_score.parts:
                    for spanner in part.getElementsByClass('Spanner'):
                        memory_spanners.append(spanner)
                
                print(f"{voice_name}: {len(memory_spanners)} spanners in memory")
                
                # Test export
                try:
                    voice_file = temp_path / f"{original_file.stem}-{voice_name}.musicxml"
                    if voice_file.exists():
                        exported_score = converter.parse(str(voice_file))
                        
                        exported_spanners = []
                        for part in exported_score.parts:
                            for spanner in part.getElementsByClass('Spanner'):
                                exported_spanners.append(spanner)
                        
                        print(f"  -> {len(exported_spanners)} spanners in exported file")
                        
                        if len(exported_spanners) > 0:
                            success_rate = (len(exported_spanners) / len(memory_spanners) * 100) if memory_spanners else 0
                            print(f"  -> Export success rate: {success_rate:.1f}%")
                        else:
                            print(f"  -> ❌ No spanners exported!")
                except Exception as e:
                    print(f"  -> Export test failed: {e}")

if __name__ == "__main__":
    test_comprehensive_spanner_processing()