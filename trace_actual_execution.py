#!/usr/bin/env python3
"""
Trace the actual voice splitter execution to find where corruption occurs.
"""

import music21
import copy
from pathlib import Path

def trace_actual_voice_splitter():
    """Trace the actual voice splitter execution step by step."""
    print("=== TRACING ACTUAL VOICE SPLITTER EXECUTION ===")
    
    # Import the actual voice splitter functions
    from satb_splitter.voice_splitter import split_satb_voices
    from satb_splitter.converter import convert_mscz_to_musicxml
    
    # Step 1: Convert the file (like the actual splitter does)
    print("\n--- STEP 1: File Conversion ---")
    input_path = Path('Crossing The Bar.mscz')
    temp_musicxml = convert_mscz_to_musicxml(input_path)
    print(f"Converted to: {temp_musicxml}")
    
    # Step 2: Load the score (like the actual splitter does)
    print("\n--- STEP 2: Load Score ---")
    score = music21.converter.parse(str(temp_musicxml))
    print(f"Loaded score with {len(score.parts)} parts")
    
    # Step 3: Create empty scores and parts (like the actual splitter does)
    print("\n--- STEP 3: Create Empty Structures ---")
    soprano_score = music21.stream.Score()
    soprano_part = music21.stream.Part()
    soprano_part.partName = "Soprano"
    soprano_part.insert(0, music21.clef.TrebleClef())
    
    # Step 4: Create unified measures (like the actual splitter does)
    print("\n--- STEP 4: Create Unified Measures ---")
    first_part_measures = list(score.parts[0].getElementsByClass(music21.stream.Measure))
    total_measures = len(first_part_measures)
    
    soprano_measures = []
    for measure_num in range(1, total_measures + 1):
        soprano_measures.append(music21.stream.Measure(number=measure_num))
    
    print(f"Created {len(soprano_measures)} soprano measures")
    
    # Step 5: Process Part 1 measures 28-30 (like the actual splitter does)
    print("\n--- STEP 5: Process Part 1 Measures 28-30 ---")
    part_0 = score.parts[0]
    original_measures = list(part_0.getElementsByClass(music21.stream.Measure))
    
    for measure_idx in [27, 28, 29]:  # 0-based indices for measures 28, 29, 30
        measure_num = measure_idx + 1
        print(f"\n  Processing measure {measure_num}:")
        
        original_measure = original_measures[measure_idx]
        soprano_measure = soprano_measures[measure_idx]
        
        print(f"    Original measure offset: {original_measure.offset}")
        print(f"    Soprano measure offset: {soprano_measure.offset}")
        
        # Get voices (like the actual splitter does)
        voices = list(original_measure.getElementsByClass(music21.stream.Voice))
        print(f"    Found {len(voices)} voices")
        
        # Process Voice 1 (Soprano)
        for voice in voices:
            voice_id = str(voice.id) if voice.id else 'unknown'
            if voice_id == '1':  # Soprano voice
                print(f"    Processing Voice {voice_id} (Soprano):")
                
                notes = list(voice.getElementsByClass(music21.note.Note))
                rests = list(voice.getElementsByClass(music21.note.Rest))
                
                print(f"      Original: {len(notes)} notes, {len(rests)} rests")
                for i, note in enumerate(notes):
                    print(f"        Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
                
                # Copy notes and rests (like the actual splitter does)
                for note in notes:
                    note_copy = copy.deepcopy(note)
                    soprano_measure.append(note_copy)
                for rest in rests:
                    rest_copy = copy.deepcopy(rest)
                    soprano_measure.append(rest_copy)
                
                # Check what's in soprano measure after copying
                soprano_notes = list(soprano_measure.getElementsByClass(music21.note.Note))
                soprano_rests = list(soprano_measure.getElementsByClass(music21.note.Rest))
                
                print(f"      After copying: {len(soprano_notes)} notes, {len(soprano_rests)} rests")
                for i, note in enumerate(soprano_notes):
                    print(f"        Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
                for i, rest in enumerate(soprano_rests):
                    print(f"        Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    # Step 6: Add measures to soprano part (like the actual splitter does)
    print("\n--- STEP 6: Add Measures to Soprano Part ---")
    for i, measure in enumerate(soprano_measures):
        soprano_part.append(measure)
        if 28 <= measure.number <= 30:
            print(f"  Added measure {measure.number}: offset={measure.offset}")
    
    # Check measures in the part
    part_measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
    print(f"\nSoprano part now has {len(part_measures)} measures")
    for measure in part_measures[27:30]:  # Measures 28-30
        print(f"  Measure {measure.number}: offset={measure.offset}")
        notes = list(measure.getElementsByClass(music21.note.Note))
        rests = list(measure.getElementsByClass(music21.note.Rest))
        print(f"    {len(notes)} notes, {len(rests)} rests")
        for i, note in enumerate(notes):
            print(f"      Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
        for i, rest in enumerate(rests):
            print(f"      Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    # Step 7: Add part to score (like the actual splitter does)
    print("\n--- STEP 7: Add Part to Score ---")
    soprano_score.append(soprano_part)
    
    # Step 8: Apply unification (like the actual splitter does)
    print("\n--- STEP 8: Apply Unification ---")
    from satb_splitter.unification import extract_dynamics_from_part, extract_lyrics_from_part, copy_dynamics_to_parts
    
    # Create voices_dict for unification (need all 4 voices for unification to work)
    # Create dummy parts for the other voices
    alto_part = music21.stream.Part()
    tenor_part = music21.stream.Part()
    bass_part = music21.stream.Part()
    
    voices_dict = {
        'Soprano': soprano_part,
        'Alto': alto_part,
        'Tenor': tenor_part,
        'Bass': bass_part
    }
    
    # Extract dynamics from soprano (this is where the issue might be)
    print("  Extracting dynamics from Soprano...")
    soprano_dynamics = extract_dynamics_from_part(soprano_part)
    print(f"    Found {len(soprano_dynamics)} dynamics")
    
    # Check soprano part before dynamics processing
    print("  Soprano part BEFORE dynamics processing:")
    part_measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
    for measure in part_measures[27:30]:  # Measures 28-30
        print(f"    Measure {measure.number}: offset={measure.offset}")
        notes = list(measure.getElementsByClass(music21.note.Note))
        rests = list(measure.getElementsByClass(music21.note.Rest))
        print(f"      {len(notes)} notes, {len(rests)} rests")
        for i, note in enumerate(notes):
            print(f"        Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    
    # Apply dynamics unification (this might be where corruption happens)
    if soprano_dynamics:
        print("  Applying dynamics unification...")
        copy_dynamics_to_parts(soprano_dynamics, ['Alto', 'Tenor', 'Bass'], voices_dict)
    
    # Check soprano part after dynamics processing
    print("  Soprano part AFTER dynamics processing:")
    part_measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
    for measure in part_measures[27:30]:  # Measures 28-30
        print(f"    Measure {measure.number}: offset={measure.offset}")
        notes = list(measure.getElementsByClass(music21.note.Note))
        rests = list(measure.getElementsByClass(music21.note.Rest))
        dynamics = list(measure.getElementsByClass(music21.dynamics.Dynamic))
        print(f"      {len(notes)} notes, {len(rests)} rests, {len(dynamics)} dynamics")
        for i, note in enumerate(notes):
            print(f"        Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
        for i, rest in enumerate(rests):
            print(f"        Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    # Check measures after unification
    print("\nAfter unification:")
    part_measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
    for measure in part_measures[27:30]:  # Measures 28-30
        print(f"  Measure {measure.number}: offset={measure.offset}")
        notes = list(measure.getElementsByClass(music21.note.Note))
        rests = list(measure.getElementsByClass(music21.note.Rest))
        dynamics = list(measure.getElementsByClass(music21.dynamics.Dynamic))
        print(f"    {len(notes)} notes, {len(rests)} rests, {len(dynamics)} dynamics")
        for i, note in enumerate(notes):
            print(f"      Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
        for i, rest in enumerate(rests):
            print(f"      Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
        for i, dyn in enumerate(dynamics):
            print(f"      Dynamic {i+1}: {dyn.value} offset={dyn.offset}")
    
    # Step 9: Write to file and read back
    print("\n--- STEP 9: Write to File and Read Back ---")
    temp_file = "temp_trace_soprano.musicxml"
    soprano_score.write('musicxml', fp=temp_file)
    
    # Read it back
    reloaded_score = music21.converter.parse(temp_file)
    reloaded_part = reloaded_score.parts[0]
    reloaded_measures = list(reloaded_part.getElementsByClass(music21.stream.Measure))
    
    print("After file write/read:")
    for measure in reloaded_measures[27:30]:  # Measures 28-30
        print(f"  Measure {measure.number}: offset={measure.offset}")
        notes = list(measure.getElementsByClass(music21.note.Note))
        rests = list(measure.getElementsByClass(music21.note.Rest))
        dynamics = list(measure.getElementsByClass(music21.dynamics.Dynamic))
        print(f"    {len(notes)} notes, {len(rests)} rests, {len(dynamics)} dynamics")
        for i, note in enumerate(notes):
            print(f"      Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
        for i, rest in enumerate(rests):
            print(f"      Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
        for i, dyn in enumerate(dynamics):
            print(f"      Dynamic {i+1}: {dyn.value} offset={dyn.offset}")
    
    # Clean up
    temp_musicxml.unlink()
    Path(temp_file).unlink(missing_ok=True)

def main():
    trace_actual_voice_splitter()

if __name__ == "__main__":
    main()