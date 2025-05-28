#!/usr/bin/env python3
"""
Debug script to analyze spanner reference repair issues in measure 29.
"""

import tempfile
from pathlib import Path
from music21 import converter
from satb_splitter.main import split_satb_voices
from satb_splitter.spanner_processor import SpannerProcessor
from satb_splitter.utils import load_score

def debug_spanner_repair():
    """Debug the spanner reference repair process."""
    score_path = Path("Crossing The Bar.musicxml")
    if not score_path.exists():
        print("❌ Sample score file not found")
        return
    
    print("🔍 Debugging Spanner Reference Repair Process")
    print("=" * 60)
    
    # Load original score
    original_score = load_score(str(score_path))
    
    # Extract spanners 
    spanner_processor = SpannerProcessor()
    original_spanners = spanner_processor.extract_all_spanners_from_score(original_score)
    
    print(f"📊 Original score analysis:")
    print(f"   Parts: {len(original_score.parts)}")
    print(f"   Spanners: {len(original_spanners)}")
    
    # Show some example spanners
    print(f"\n🎵 Example spanners from original:")
    for i, spanner in enumerate(original_spanners[:5]):
        print(f"   {i+1}. {type(spanner).__name__}: {spanner}")
        
        # Try to get spanned elements
        try:
            if hasattr(spanner, 'getSpannedElements'):
                elements = spanner.getSpannedElements()
                print(f"      Spanned elements: {len(elements)}")
                for elem in elements[:2]:  # Show first 2
                    if hasattr(elem, 'pitch'):
                        print(f"        Note: {elem.pitch.name}{elem.pitch.octave} (id: {id(elem)})")
        except Exception as e:
            print(f"      Error getting spanned elements: {e}")
    
    # Process voices 
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        voices = split_satb_voices(str(score_path), str(temp_path))
        
        # Analyze notes in each voice for comparison
        print(f"\n🎤 Voice analysis:")
        voice_notes = {}
        for voice_name, voice_score in voices.items():
            notes = []
            for part in voice_score.parts:
                for measure in part.getElementsByClass('Measure'):
                    if hasattr(measure, 'number') and measure.number == 29:
                        for note in measure.flatten().notes:
                            notes.append(note)
                            if len(notes) <= 3:  # Show first 3 notes
                                print(f"   {voice_name} measure 29 note: {note.pitch.name}{note.pitch.octave} (id: {id(note)})")
            voice_notes[voice_name] = notes
            print(f"   {voice_name}: {len(notes)} notes in measure 29")
        
        # Test repair for a specific spanner
        print(f"\n🔧 Testing spanner repair:")
        if original_spanners:
            test_spanner = original_spanners[0]
            print(f"   Testing: {type(test_spanner).__name__}: {test_spanner}")
            
            # Test repair for each voice
            for voice_name, notes in voice_notes.items():
                if notes:
                    repairer = spanner_processor.repairer
                    success = repairer.repair_spanner_references(test_spanner, notes, "contextual")
                    print(f"   {voice_name} repair result: {'✅ Success' if success else '❌ Failed'}")

if __name__ == "__main__":
    debug_spanner_repair()