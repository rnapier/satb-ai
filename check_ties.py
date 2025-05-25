#!/usr/bin/env python3
"""
Check for ties in note attributes since they weren't found as spanners.
"""

import music21
from pathlib import Path

def check_ties_in_notes(file_path):
    """Check for ties as note attributes."""
    print(f"=== Checking Ties in {file_path} ===")
    
    score = music21.converter.parse(str(file_path))
    
    tied_notes = []
    for part_idx, part in enumerate(score.parts):
        print(f"\nPart {part_idx + 1} ({part.partName}):")
        for measure in part.getElementsByClass(music21.stream.Measure):
            for voice in measure.getElementsByClass(music21.stream.Voice):
                voice_id = str(voice.id) if voice.id else 'unknown'
                for note in voice.getElementsByClass(music21.note.Note):
                    if hasattr(note, 'tie') and note.tie is not None:
                        tied_notes.append((part.partName, voice_id, measure.number, note))
                        print(f"  Voice {voice_id}, Measure {measure.number}: {note.pitch} - tie: {note.tie.type}")
    
    print(f"\nTotal tied notes found: {len(tied_notes)}")
    return tied_notes

def main():
    test_file = Path("Crossing The Bar.musicxml")
    if test_file.exists():
        check_ties_in_notes(test_file)
    else:
        print(f"Test file not found: {test_file}")

if __name__ == "__main__":
    main()