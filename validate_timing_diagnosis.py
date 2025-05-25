#!/usr/bin/env python3
"""
Validate the timing diagnosis by adding detailed logging to the voice splitting process.
"""

import music21
import copy
from pathlib import Path

def trace_soprano_extraction():
    """Trace exactly what happens during Soprano extraction in measure 29."""
    print("=== TRACING SOPRANO EXTRACTION FOR MEASURE 29 ===")
    
    # Load the base score
    score = music21.converter.parse('Crossing The Bar-base.musicxml')
    
    # Get Part 0 (should contain Soprano voice)
    part_0 = score.parts[0]
    measures = list(part_0.getElementsByClass(music21.stream.Measure))
    measure_29 = measures[28]  # 0-based index
    
    print(f"Original measure 29 offset: {measure_29.offset}")
    print(f"Original measure 29 number: {measure_29.number}")
    
    # Get Voice 1 (should be Soprano)
    voices = list(measure_29.getElementsByClass(music21.stream.Voice))
    voice_1 = None
    for voice in voices:
        if str(voice.id) == '1':
            voice_1 = voice
            break
    
    if voice_1 is None:
        print("ERROR: Voice 1 not found!")
        return
    
    print(f"\nVoice 1 content:")
    notes = list(voice_1.getElementsByClass(music21.note.Note))
    rests = list(voice_1.getElementsByClass(music21.note.Rest))
    
    print(f"Notes in Voice 1: {len(notes)}")
    for i, note in enumerate(notes):
        print(f"  Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    
    print(f"Rests in Voice 1: {len(rests)}")
    for i, rest in enumerate(rests):
        print(f"  Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    # Now simulate what the voice splitter does
    print(f"\n=== SIMULATING VOICE SPLITTER PROCESS ===")
    
    # Create a new measure for Soprano (like the splitter does)
    soprano_measure = music21.stream.Measure(number=29)
    
    print(f"Created soprano measure with number: {soprano_measure.number}")
    print(f"Soprano measure offset: {soprano_measure.offset}")
    
    # Copy notes and rests (like the splitter does)
    print(f"\nCopying notes and rests to soprano measure...")
    for note in notes:
        note_copy = copy.deepcopy(note)
        soprano_measure.append(note_copy)
        print(f"  Copied note: {note_copy.pitch.name}{note_copy.pitch.octave} dur={note_copy.duration.quarterLength} offset={note_copy.offset}")
    
    for rest in rests:
        rest_copy = copy.deepcopy(rest)
        soprano_measure.append(rest_copy)
        print(f"  Copied rest: dur={rest_copy.duration.quarterLength} offset={rest_copy.offset}")
    
    # Check what's in the soprano measure now
    print(f"\n=== SOPRANO MEASURE AFTER COPYING ===")
    soprano_notes = list(soprano_measure.getElementsByClass(music21.note.Note))
    soprano_rests = list(soprano_measure.getElementsByClass(music21.note.Rest))
    
    print(f"Soprano measure notes: {len(soprano_notes)}")
    for i, note in enumerate(soprano_notes):
        print(f"  Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    
    print(f"Soprano measure rests: {len(soprano_rests)}")
    for i, rest in enumerate(soprano_rests):
        print(f"  Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    # Check measure properties
    print(f"\nSoprano measure properties:")
    print(f"  Number: {soprano_measure.number}")
    print(f"  Offset: {soprano_measure.offset}")
    print(f"  Duration: {soprano_measure.duration.quarterLength}")
    
    # Compare with actual output
    print(f"\n=== COMPARING WITH ACTUAL SOPRANO OUTPUT ===")
    soprano_score = music21.converter.parse('Crossing The Bar_voices/Crossing The Bar-Soprano.musicxml')
    actual_part = soprano_score.parts[0]
    actual_measures = list(actual_part.getElementsByClass(music21.stream.Measure))
    actual_measure_29 = actual_measures[28]
    
    print(f"Actual soprano measure 29:")
    print(f"  Number: {actual_measure_29.number}")
    print(f"  Offset: {actual_measure_29.offset}")
    
    actual_notes = list(actual_measure_29.getElementsByClass(music21.note.Note))
    actual_rests = list(actual_measure_29.getElementsByClass(music21.note.Rest))
    
    print(f"  Notes: {len(actual_notes)}")
    for i, note in enumerate(actual_notes):
        print(f"    Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
    
    print(f"  Rests: {len(actual_rests)}")
    for i, rest in enumerate(actual_rests):
        print(f"    Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")

def check_measure_offset_calculation():
    """Check how measure offsets are being calculated."""
    print(f"\n=== CHECKING MEASURE OFFSET CALCULATION ===")
    
    # Check the base score measure offsets
    score = music21.converter.parse('Crossing The Bar-base.musicxml')
    
    for part_idx, part in enumerate(score.parts):
        print(f"\nPart {part_idx} measure offsets:")
        measures = list(part.getElementsByClass(music21.stream.Measure))
        
        for i, measure in enumerate(measures[25:32]):  # Measures around 29
            measure_num = i + 26
            print(f"  Measure {measure_num}: offset={measure.offset}, number={measure.number}")

def main():
    trace_soprano_extraction()
    check_measure_offset_calculation()

if __name__ == "__main__":
    main()