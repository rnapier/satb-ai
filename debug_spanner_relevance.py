#!/usr/bin/env python3
"""
Debug script to understand why spanner relevance detection is failing.
"""

from music21 import converter
from pathlib import Path
from satb_splitter.main import split_satb_voices
from satb_splitter.spanner_processor import SpannerProcessor
import tempfile

def debug_spanner_relevance():
    """Debug why all spanners are being marked as irrelevant."""
    
    original_file = Path("Crossing The Bar.musicxml")
    
    if not original_file.exists():
        print("❌ Sample score file not found")
        return
    
    print("=== DEBUGGING SPANNER RELEVANCE DETECTION ===")
    
    # Load original score
    original_score = converter.parse(str(original_file))
    
    # Process to get voice scores
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        voices = split_satb_voices(str(original_file), str(temp_path))
        
        # Extract spanners
        spanner_processor = SpannerProcessor()
        original_spanners = spanner_processor.extract_all_spanners_from_score(original_score)
        
        print(f"\nExtracted {len(original_spanners)} spanners:")
        for i, spanner in enumerate(original_spanners[:5]):  # Show first 5
            print(f"  {i}: {spanner}")
        
        # Analyze voice notes
        voice_notes = {}
        for voice_name, voice_score in voices.items():
            notes = []
            for part in voice_score.parts:
                for measure in part.getElementsByClass('Measure'):
                    for note in measure.flatten().notes:
                        notes.append(note)
            voice_notes[voice_name] = notes
            print(f"\n{voice_name}: {len(notes)} notes")
            if notes:
                print(f"  First note: {notes[0]} (pitch: {getattr(notes[0], 'pitch', 'No pitch')})")
        
        # Analyze first spanner in detail
        if original_spanners:
            print(f"\n=== ANALYZING FIRST SPANNER ===")
            first_spanner = original_spanners[0]
            print(f"Spanner: {first_spanner}")
            
            # Get spanner note references
            spanner_notes = []
            try:
                if hasattr(first_spanner, 'getSpannedElements'):
                    spanned_elements = first_spanner.getSpannedElements()
                    for element in spanned_elements:
                        if hasattr(element, 'pitch'):
                            spanner_notes.append(element)
                print(f"Spanner references {len(spanner_notes)} notes:")
                for note in spanner_notes:
                    print(f"  - {note} (pitch: {note.pitch})")
            except Exception as e:
                print(f"Error getting spanned elements: {e}")
            
            # Check for matches in each voice
            for voice_name, notes in voice_notes.items():
                matches = 0
                note_set = set(notes)
                for spanner_note in spanner_notes:
                    if spanner_note in note_set:
                        matches += 1
                        print(f"  Found exact match in {voice_name}: {spanner_note}")
                    else:
                        # Check for pitch matches
                        pitch_matches = []
                        for voice_note in notes:
                            if (hasattr(voice_note, 'pitch') and hasattr(spanner_note, 'pitch')):
                                if (voice_note.pitch.name == spanner_note.pitch.name and 
                                    voice_note.pitch.octave == spanner_note.pitch.octave):
                                    pitch_matches.append(voice_note)
                        
                        if pitch_matches:
                            print(f"  Found {len(pitch_matches)} pitch matches in {voice_name} for {spanner_note.pitch}")
                        else:
                            print(f"  No matches in {voice_name} for {spanner_note.pitch}")
                
                coverage = matches / len(spanner_notes) if spanner_notes else 0
                print(f"  {voice_name} coverage: {coverage:.2f} ({matches}/{len(spanner_notes)})")

if __name__ == "__main__":
    debug_spanner_relevance()