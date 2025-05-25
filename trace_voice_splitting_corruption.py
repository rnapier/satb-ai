#!/usr/bin/env python3
"""
Trace exactly when and where the corruption occurs during voice splitting.
"""

import music21
import copy
from pathlib import Path


def trace_voice_splitting_step_by_step():
    """Trace voice splitting step by step to find corruption point."""
    print("=== TRACING VOICE SPLITTING STEP BY STEP ===")
    
    # Step 1: Load and convert the original file
    from satb_splitter.converter import convert_mscz_to_musicxml
    
    print("\n--- STEP 1: File Conversion ---")
    input_path = Path('Crossing The Bar.mscz')
    temp_musicxml = convert_mscz_to_musicxml(input_path)
    print(f"Converted to: {temp_musicxml}")
    
    # Step 2: Load the score
    print("\n--- STEP 2: Load Score ---")
    score = music21.converter.parse(str(temp_musicxml))
    print(f"Loaded score with {len(score.parts)} parts")
    
    # Step 3: Check measure 29 in original score
    print("\n--- STEP 3: Original Score Measure 29 ---")
    part_0 = score.parts[0]
    original_measures = list(part_0.getElementsByClass(music21.stream.Measure))
    original_measure_29 = original_measures[28]  # 0-based
    
    print(f"Original measure 29:")
    print(f"  Number: {original_measure_29.number}")
    print(f"  Offset: {original_measure_29.offset}")
    
    voices = list(original_measure_29.getElementsByClass(music21.stream.Voice))
    for voice in voices:
        voice_id = str(voice.id) if voice.id else 'unknown'
        if voice_id == '1':  # Soprano voice
            print(f"  Voice 1 (Soprano):")
            notes = list(voice.getElementsByClass(music21.note.Note))
            rests = list(voice.getElementsByClass(music21.note.Rest))
            print(f"    {len(notes)} notes, {len(rests)} rests")
            for i, note in enumerate(notes):
                print(f"      Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
            for i, rest in enumerate(rests):
                print(f"      Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    # Step 4: Create soprano measures (like voice splitter does)
    print("\n--- STEP 4: Create Soprano Measures ---")
    total_measures = len(original_measures)
    soprano_measures = []
    for measure_num in range(1, total_measures + 1):
        soprano_measures.append(music21.stream.Measure(number=measure_num))
    
    soprano_measure_29 = soprano_measures[28]  # 0-based
    print(f"Created soprano measure 29: offset={soprano_measure_29.offset}")
    
    # Step 5: Copy notes from Voice 1 to soprano measure (like voice splitter does)
    print("\n--- STEP 5: Copy Notes to Soprano Measure ---")
    original_voice_1 = None
    for voice in voices:
        if str(voice.id) == '1':
            original_voice_1 = voice
            break
    
    if original_voice_1:
        notes = list(original_voice_1.getElementsByClass(music21.note.Note))
        rests = list(original_voice_1.getElementsByClass(music21.note.Rest))
        
        print(f"Copying {len(notes)} notes and {len(rests)} rests...")
        for note in notes:
            note_copy = copy.deepcopy(note)
            soprano_measure_29.append(note_copy)
            print(f"  Copied note: {note_copy.pitch.name}{note_copy.pitch.octave} dur={note_copy.duration.quarterLength} offset={note_copy.offset}")
        
        for rest in rests:
            rest_copy = copy.deepcopy(rest)
            soprano_measure_29.append(rest_copy)
            print(f"  Copied rest: dur={rest_copy.duration.quarterLength} offset={rest_copy.offset}")
    
    # Check soprano measure after copying
    print(f"\nSoprano measure 29 after copying:")
    soprano_notes = list(soprano_measure_29.getElementsByClass(music21.note.Note))
    soprano_rests = list(soprano_measure_29.getElementsByClass(music21.note.Rest))
    print(f"  {len(soprano_notes)} notes, {len(soprano_rests)} rests")
    for i, note in enumerate(soprano_notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(soprano_rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    # Step 6: Create soprano part and add measures
    print("\n--- STEP 6: Create Soprano Part ---")
    soprano_part = music21.stream.Part()
    soprano_part.partName = "Soprano"
    soprano_part.insert(0, music21.clef.TrebleClef())
    
    # Add all measures to the part
    for measure in soprano_measures:
        soprano_part.append(measure)
    
    # Check measure 29 in the part
    part_measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
    part_measure_29 = part_measures[28]  # 0-based
    
    print(f"Measure 29 in soprano part:")
    print(f"  Number: {part_measure_29.number}")
    print(f"  Offset: {part_measure_29.offset}")
    
    part_notes = list(part_measure_29.getElementsByClass(music21.note.Note))
    part_rests = list(part_measure_29.getElementsByClass(music21.note.Rest))
    print(f"  {len(part_notes)} notes, {len(part_rests)} rests")
    for i, note in enumerate(part_notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(part_rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    # Step 7: Apply unification (this might be where corruption happens)
    print("\n--- STEP 7: Apply Unification ---")
    from satb_splitter.unification import extract_dynamics_from_part, copy_dynamics_to_parts
    
    # Extract dynamics from the original part
    original_dynamics = extract_dynamics_from_part(part_0)
    print(f"Found {len(original_dynamics)} dynamics in original part")
    
    # Apply dynamics to soprano part
    voices_dict = {'Soprano': soprano_part}
    if original_dynamics:
        print("Applying dynamics to soprano part...")
        copy_dynamics_to_parts(original_dynamics, ['Soprano'], voices_dict)
    
    # Check measure 29 after unification
    print(f"\nMeasure 29 after unification:")
    final_measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
    final_measure_29 = final_measures[28]  # 0-based
    
    final_notes = list(final_measure_29.getElementsByClass(music21.note.Note))
    final_rests = list(final_measure_29.getElementsByClass(music21.note.Rest))
    final_dynamics = list(final_measure_29.getElementsByClass(music21.dynamics.Dynamic))
    
    print(f"  {len(final_notes)} notes, {len(final_rests)} rests, {len(final_dynamics)} dynamics")
    for i, note in enumerate(final_notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    for i, rest in enumerate(final_rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    for i, dyn in enumerate(final_dynamics):
        print(f"    Dynamic {i+1}: {dyn.value} offset={dyn.offset}")
    
    # Clean up
    temp_musicxml.unlink()
    
    # Return corruption status
    corruption_detected = len(final_rests) > 0 or (len(final_notes) > 0 and final_notes[0].offset != 0.0)
    return corruption_detected


def main():
    corruption_detected = trace_voice_splitting_step_by_step()
    
    print(f"\n=== FINAL RESULT ===")
    if corruption_detected:
        print("❌ CORRUPTION DETECTED during voice splitting process")
    else:
        print("✅ No corruption detected")


if __name__ == "__main__":
    main()