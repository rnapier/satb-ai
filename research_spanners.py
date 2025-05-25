#!/usr/bin/env python3
"""
Research script to understand music21 spanner handling.
This script analyzes the "Crossing The Bar.musicxml" file to understand
how spanners are represented and accessed in music21.
"""

import music21
from pathlib import Path

def analyze_spanners_in_score(file_path):
    """Analyze all spanners in a music21 score."""
    print(f"=== Analyzing Spanners in {file_path} ===")
    
    # Load the score
    score = music21.converter.parse(str(file_path))
    
    print(f"Score type: {type(score)}")
    print(f"Number of parts: {len(score.parts)}")
    
    # Method 1: Look for spanners at score level
    print("\n--- Score-level Spanners ---")
    score_spanners = score.getElementsByClass(music21.spanner.Spanner)
    print(f"Score-level spanners found: {len(score_spanners)}")
    for i, spanner in enumerate(score_spanners):
        print(f"  {i+1}. {type(spanner).__name__}: {spanner}")
    
    # Method 2: Look for spanners in each part
    print("\n--- Part-level Spanners ---")
    for part_idx, part in enumerate(score.parts):
        print(f"\nPart {part_idx + 1} ({part.partName}):")
        part_spanners = part.getElementsByClass(music21.spanner.Spanner)
        print(f"  Part spanners: {len(part_spanners)}")
        for spanner in part_spanners:
            print(f"    {type(spanner).__name__}: {spanner}")
    
    # Method 3: Look for specific spanner types
    print("\n--- Specific Spanner Types ---")
    
    # Slurs - check both score and part level
    slurs_score = score.getElementsByClass(music21.spanner.Slur)
    print(f"Score-level slurs found: {len(slurs_score)}")
    
    # Check part-level slurs
    slurs_parts = []
    for part in score.parts:
        part_slurs = part.getElementsByClass(music21.spanner.Slur)
        slurs_parts.extend(part_slurs)
    print(f"Part-level slurs found: {len(slurs_parts)}")
    
    for slur in slurs_parts[:5]:  # Show first 5
        print(f"  Slur: {slur}")
    
    # Ties - check tie.Tie only (spanner.Tie doesn't exist)
    ties1 = score.getElementsByClass(music21.tie.Tie)
    print(f"music21.tie.Tie found: {len(ties1)}")
    for tie in ties1[:5]:  # Show first 5
        print(f"  Tie: {tie}")
    
    # Dynamic wedges - check multiple classes
    wedges1 = score.getElementsByClass(music21.dynamics.DynamicWedge)
    crescendos = score.getElementsByClass(music21.dynamics.Crescendo)
    diminuendos = score.getElementsByClass(music21.dynamics.Diminuendo)
    print(f"DynamicWedge found: {len(wedges1)}")
    print(f"Crescendo found: {len(crescendos)}")
    print(f"Diminuendo found: {len(diminuendos)}")
    
    all_wedges = list(wedges1) + list(crescendos) + list(diminuendos)
    for wedge in all_wedges[:5]:  # Show first 5
        print(f"  Wedge: {type(wedge).__name__} - {wedge}")
    
    # Method 4: Look in measures for spanners
    print("\n--- Measure-level Analysis ---")
    total_measures = 0
    measures_with_spanners = 0
    
    for part in score.parts:
        measures = part.getElementsByClass(music21.stream.Measure)
        total_measures += len(measures)
        
        for measure in measures:
            measure_spanners = measure.getElementsByClass(music21.spanner.Spanner)
            if measure_spanners:
                measures_with_spanners += 1
                print(f"  Measure {measure.number}: {len(measure_spanners)} spanners")
                for spanner in measure_spanners:
                    print(f"    {type(spanner).__name__}")
    
    print(f"Total measures: {total_measures}")
    print(f"Measures with spanners: {measures_with_spanners}")
    
    # Method 5: Look for tied notes and analyze spanner details
    print("\n--- Tied Notes Analysis ---")
    tied_notes = []
    for part in score.parts:
        for measure in part.getElementsByClass(music21.stream.Measure):
            for note in measure.getElementsByClass(music21.note.Note):
                if hasattr(note, 'tie') and note.tie:
                    tied_notes.append((part.partName, measure.number, note))
    
    print(f"Notes with ties: {len(tied_notes)}")
    for part_name, measure_num, note in tied_notes[:10]:  # Show first 10
        print(f"  {part_name}, Measure {measure_num}: {note.pitch} - {note.tie}")
    
    # Method 5b: Detailed spanner analysis
    print("\n--- Detailed Spanner Analysis ---")
    for part_idx, part in enumerate(score.parts):
        part_spanners = part.getElementsByClass(music21.spanner.Spanner)
        if part_spanners:
            print(f"\nPart {part_idx + 1} detailed spanners:")
            for spanner in part_spanners:
                print(f"  {type(spanner).__name__}:")
                print(f"    Spanned elements: {len(spanner.getSpannedElements())}")
                for elem in spanner.getSpannedElements():
                    if hasattr(elem, 'pitch'):
                        print(f"      Note: {elem.pitch} at offset {elem.offset}")
                    else:
                        print(f"      Element: {type(elem).__name__} at offset {elem.offset}")
    
    # Method 6: Look for notations (slurs, ties in XML)
    print("\n--- Notations Analysis ---")
    notation_count = 0
    slur_notations = 0
    tie_notations = 0
    
    for part in score.parts:
        for measure in part.getElementsByClass(music21.stream.Measure):
            for note in measure.getElementsByClass(music21.note.Note):
                if hasattr(note, 'notations') and note.notations:
                    notation_count += 1
                    # This might not work as expected - need to investigate
                    print(f"  Note with notations: {note.pitch}")

def main():
    """Main research function."""
    test_file = Path("Crossing The Bar.musicxml")
    
    if not test_file.exists():
        print(f"Error: Test file '{test_file}' not found")
        return
    
    try:
        analyze_spanners_in_score(test_file)
    except Exception as e:
        print(f"Error analyzing spanners: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()