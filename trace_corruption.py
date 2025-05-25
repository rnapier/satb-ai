#!/usr/bin/env python3
"""
Trace exactly where the corruption happens in the voice splitting process.
"""

import music21
import copy
from pathlib import Path

def trace_soprano_through_pipeline():
    """Trace Soprano voice through the entire pipeline to find where corruption occurs."""
    print("=== TRACING SOPRANO THROUGH ENTIRE PIPELINE ===")
    
    # Step 1: Load base score and extract Voice 1 from measure 29
    print("\n--- STEP 1: Extract from base score ---")
    score = music21.converter.parse('Crossing The Bar-base.musicxml')
    part_0 = score.parts[0]
    measures = list(part_0.getElementsByClass(music21.stream.Measure))
    measure_29 = measures[28]
    
    voices = list(measure_29.getElementsByClass(music21.stream.Voice))
    voice_1 = None
    for voice in voices:
        if str(voice.id) == '1':
            voice_1 = voice
            break
    
    notes = list(voice_1.getElementsByClass(music21.note.Note))
    print(f"Original Voice 1 notes: {len(notes)}")
    for i, note in enumerate(notes):
        print(f"  {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    
    # Step 2: Simulate voice splitting (create soprano measure and copy notes)
    print("\n--- STEP 2: Voice splitting simulation ---")
    soprano_measure = music21.stream.Measure(number=29)
    
    for note in notes:
        note_copy = copy.deepcopy(note)
        soprano_measure.append(note_copy)
    
    soprano_notes_after_split = list(soprano_measure.getElementsByClass(music21.note.Note))
    print(f"Soprano notes after splitting: {len(soprano_notes_after_split)}")
    for i, note in enumerate(soprano_notes_after_split):
        print(f"  {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    
    # Step 3: Create a complete soprano part and score (like the voice splitter does)
    print("\n--- STEP 3: Create complete soprano part ---")
    soprano_part = music21.stream.Part()
    soprano_part.partName = "Soprano"
    soprano_part.insert(0, music21.clef.TrebleClef())
    
    # Add the measure to the part
    soprano_part.append(soprano_measure)
    
    # Create soprano score
    soprano_score = music21.stream.Score()
    soprano_score.append(soprano_part)
    
    # Check notes after adding to part
    part_measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
    part_measure_29 = part_measures[0]  # Should be the only measure
    soprano_notes_in_part = list(part_measure_29.getElementsByClass(music21.note.Note))
    print(f"Soprano notes in part: {len(soprano_notes_in_part)}")
    for i, note in enumerate(soprano_notes_in_part):
        print(f"  {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    
    # Step 4: Simulate unification process
    print("\n--- STEP 4: Simulate unification process ---")
    
    # Create a minimal voices_dict for unification
    voices_dict = {'Soprano': soprano_part}
    
    # Import and run the unification functions
    from satb_splitter.unification import extract_dynamics_from_part, extract_lyrics_from_part
    
    soprano_dynamics = extract_dynamics_from_part(soprano_part)
    soprano_lyrics = extract_lyrics_from_part(soprano_part)
    
    print(f"Dynamics found: {len(soprano_dynamics)}")
    print(f"Lyrics found: {len(soprano_lyrics)}")
    
    # Check notes after unification extraction
    soprano_notes_after_unification = list(part_measure_29.getElementsByClass(music21.note.Note))
    print(f"Soprano notes after unification: {len(soprano_notes_after_unification)}")
    for i, note in enumerate(soprano_notes_after_unification):
        print(f"  {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    
    # Step 5: Simulate spanner processing
    print("\n--- STEP 5: Simulate spanner processing ---")
    
    # Create empty spanner assignments
    spanner_assignments = {'Soprano': []}
    
    # Import spanner functions
    from satb_splitter.spanner_builder import rebuild_spanners_in_parts, validate_spanners_in_parts
    
    # Create a score dict for spanner processing
    voices_score_dict = {'Soprano': soprano_score}
    
    # Run spanner rebuilding
    rebuild_spanners_in_parts(voices_score_dict, spanner_assignments)
    
    # Check notes after spanner processing
    soprano_notes_after_spanners = list(part_measure_29.getElementsByClass(music21.note.Note))
    print(f"Soprano notes after spanners: {len(soprano_notes_after_spanners)}")
    for i, note in enumerate(soprano_notes_after_spanners):
        print(f"  {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    
    # Step 6: Write to file and read back
    print("\n--- STEP 6: Write to file and read back ---")
    
    # Write the soprano score to a temporary file
    temp_file = "temp_soprano_test.musicxml"
    soprano_score.write('musicxml', fp=temp_file)
    
    # Read it back
    reloaded_score = music21.converter.parse(temp_file)
    reloaded_part = reloaded_score.parts[0]
    reloaded_measures = list(reloaded_part.getElementsByClass(music21.stream.Measure))
    
    if reloaded_measures:
        reloaded_measure = reloaded_measures[0]
        reloaded_notes = list(reloaded_measure.getElementsByClass(music21.note.Note))
        reloaded_rests = list(reloaded_measure.getElementsByClass(music21.note.Rest))
        
        print(f"Reloaded notes: {len(reloaded_notes)}")
        for i, note in enumerate(reloaded_notes):
            print(f"  {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
        
        print(f"Reloaded rests: {len(reloaded_rests)}")
        for i, rest in enumerate(reloaded_rests):
            print(f"  {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    # Clean up
    Path(temp_file).unlink(missing_ok=True)
    
    # Step 7: Compare with actual output
    print("\n--- STEP 7: Compare with actual output ---")
    actual_soprano = music21.converter.parse('Crossing The Bar_voices/Crossing The Bar-Soprano.musicxml')
    actual_part = actual_soprano.parts[0]
    actual_measures = list(actual_part.getElementsByClass(music21.stream.Measure))
    actual_measure_29 = actual_measures[28]
    
    actual_notes = list(actual_measure_29.getElementsByClass(music21.note.Note))
    actual_rests = list(actual_measure_29.getElementsByClass(music21.note.Rest))
    
    print(f"Actual output notes: {len(actual_notes)}")
    for i, note in enumerate(actual_notes):
        print(f"  {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    
    print(f"Actual output rests: {len(actual_rests)}")
    for i, rest in enumerate(actual_rests):
        print(f"  {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")

def check_measure_creation_process():
    """Check if the issue is in how measures are created and numbered."""
    print("\n=== CHECKING MEASURE CREATION PROCESS ===")
    
    # Load the base score
    score = music21.converter.parse('Crossing The Bar-base.musicxml')
    first_part_measures = list(score.parts[0].getElementsByClass(music21.stream.Measure))
    total_measures = len(first_part_measures)
    
    print(f"Total measures in base score: {total_measures}")
    
    # Simulate the measure creation process from voice_splitter.py
    soprano_measures = []
    for measure_num in range(1, total_measures + 1):
        soprano_measures.append(music21.stream.Measure(number=measure_num))
    
    print(f"Created {len(soprano_measures)} soprano measures")
    
    # Check measure 29 specifically
    measure_29_index = 28  # 0-based
    if measure_29_index < len(soprano_measures):
        soprano_measure_29 = soprano_measures[measure_29_index]
        print(f"Soprano measure 29: number={soprano_measure_29.number}, offset={soprano_measure_29.offset}")
        
        # Check the corresponding original measure
        original_measure_29 = first_part_measures[measure_29_index]
        print(f"Original measure 29: number={original_measure_29.number}, offset={original_measure_29.offset}")

def main():
    trace_soprano_through_pipeline()
    check_measure_creation_process()

if __name__ == "__main__":
    main()