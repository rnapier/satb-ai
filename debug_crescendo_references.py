#!/usr/bin/env python3
"""
Debug script to analyze spanner note references in detail.
"""

from music21 import converter
from pathlib import Path
from satb_splitter.main import split_satb_voices
import tempfile

def analyze_spanner_note_references():
    """Analyze the specific note references in spanners."""
    
    original_file = Path("Crossing The Bar.musicxml")
    
    print("=== ANALYZING SPANNER NOTE REFERENCES ===")
    
    # Load original score
    original_score = converter.parse(str(original_file))
    
    # Get the problematic crescendo from the original
    target_crescendo = None
    for part in original_score.parts:
        for spanner in part.getElementsByClass('Spanner'):
            if 'Crescendo' in str(type(spanner)) and '<music21.note.Note G><music21.note.Note E>' in str(spanner):
                target_crescendo = spanner
                print(f"\nFound target crescendo: {spanner}")
                break
        if target_crescendo:
            break
    
    if target_crescendo:
        print(f"\n=== ANALYZING TARGET CRESCENDO ===")
        print(f"Crescendo: {target_crescendo}")
        print(f"Type: {type(target_crescendo)}")
        
        # Check what notes it references
        if hasattr(target_crescendo, 'noteStart'):
            print(f"Note start: {target_crescendo.noteStart}")
            print(f"Note start pitch: {getattr(target_crescendo.noteStart, 'pitch', 'No pitch')}")
            print(f"Note start measure: {getattr(target_crescendo.noteStart.activeSite, 'number', 'No measure') if hasattr(target_crescendo.noteStart, 'activeSite') else 'No activeSite'}")
        
        if hasattr(target_crescendo, 'noteEnd'):
            print(f"Note end: {target_crescendo.noteEnd}")
            print(f"Note end pitch: {getattr(target_crescendo.noteEnd, 'pitch', 'No pitch')}")
            print(f"Note end measure: {getattr(target_crescendo.noteEnd.activeSite, 'number', 'No measure') if hasattr(target_crescendo.noteEnd, 'activeSite') else 'No activeSite'}")
        
        # Check spanned elements
        if hasattr(target_crescendo, 'getSpannedElements'):
            try:
                spanned = target_crescendo.getSpannedElements()
                print(f"Spanned elements: {spanned}")
                for elem in spanned:
                    if hasattr(elem, 'pitch'):
                        print(f"  - {elem} (pitch: {elem.pitch})")
            except Exception as e:
                print(f"Could not get spanned elements: {e}")
    
    # Now process with voice separation and check if the notes still exist
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        voices = split_satb_voices(str(original_file), str(temp_path))
        
        soprano_score = voices.get('Soprano')
        if soprano_score and target_crescendo:
            print(f"\n=== CHECKING SOPRANO PART FOR REFERENCED NOTES ===")
            
            # Check if the referenced notes exist in soprano
            soprano_notes = []
            for part in soprano_score.parts:
                for measure in part.getElementsByClass('Measure'):
                    for note in measure.getElementsByClass('Note'):
                        soprano_notes.append({
                            'note': note,
                            'pitch': note.pitch.name + str(note.pitch.octave),
                            'measure': measure.number,
                            'offset': note.offset
                        })
            
            print(f"Found {len(soprano_notes)} notes in soprano part")
            
            # Check if target notes exist
            try:
                if hasattr(target_crescendo, 'getSpannedElements'):
                    spanned = target_crescendo.getSpannedElements()
                    for i, elem in enumerate(spanned):
                        if hasattr(elem, 'pitch'):
                            target_pitch = elem.pitch.name + str(elem.pitch.octave)
                            matching_notes = [n for n in soprano_notes if n['pitch'] == target_pitch]
                            print(f"\nSpanned element {i}: {elem}")
                            print(f"Target pitch: {target_pitch}")
                            print(f"Matching notes in soprano: {len(matching_notes)}")
                            for match in matching_notes[:3]:  # Show first 3 matches
                                print(f"  - Measure {match['measure']}, offset {match['offset']}")
                            
                            # Check if the original note object still exists in soprano
                            original_note_exists = False
                            for part in soprano_score.parts:
                                for measure in part.getElementsByClass('Measure'):
                                    for note in measure.getElementsByClass('Note'):
                                        if note is elem:  # Same object reference
                                            original_note_exists = True
                                            print(f"  ✅ Original note object still exists!")
                                            break
                            if not original_note_exists:
                                print(f"  ❌ Original note object no longer exists (object reference broken)")
            except Exception as e:
                print(f"Error analyzing spanned elements: {e}")

if __name__ == "__main__":
    analyze_spanner_note_references()