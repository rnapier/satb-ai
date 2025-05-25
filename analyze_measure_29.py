#!/usr/bin/env python3
"""
Analyze measure 29 in all voice parts and compare to the base musicxml.
"""

import music21
from pathlib import Path

def analyze_measure(part, measure_number, part_name):
    """Analyze a specific measure in a part."""
    print(f"\n=== {part_name} - Measure {measure_number} ===")
    
    measures = list(part.getElementsByClass(music21.stream.Measure))
    if measure_number > len(measures):
        print(f"ERROR: Measure {measure_number} not found (only {len(measures)} measures)")
        return None
    
    measure = measures[measure_number - 1]  # Convert to 0-based index
    print(f"Measure number: {measure.number}")
    print(f"Offset: {measure.offset}")
    
    # Get all notes and rests
    notes = list(measure.getElementsByClass(music21.note.Note))
    rests = list(measure.getElementsByClass(music21.note.Rest))
    chords = list(measure.getElementsByClass(music21.chord.Chord))
    
    print(f"Notes: {len(notes)}")
    print(f"Rests: {len(rests)}")
    print(f"Chords: {len(chords)}")
    
    # Analyze notes
    if notes:
        print("Notes details:")
        for i, note in enumerate(notes):
            print(f"  Note {i+1}: {note.pitch.name}{note.pitch.octave} (duration: {note.duration.quarterLength}, offset: {note.offset})")
    
    # Analyze chords
    if chords:
        print("Chord details:")
        for i, chord in enumerate(chords):
            pitches = [f"{p.name}{p.octave}" for p in chord.pitches]
            print(f"  Chord {i+1}: {pitches} (duration: {chord.duration.quarterLength}, offset: {chord.offset})")
    
    # Analyze rests
    if rests:
        print("Rest details:")
        for i, rest in enumerate(rests):
            print(f"  Rest {i+1}: duration {rest.duration.quarterLength}, offset: {rest.offset}")
    
    # Get dynamics
    dynamics = list(measure.getElementsByClass(music21.dynamics.Dynamic))
    if dynamics:
        print("Dynamics:")
        for dyn in dynamics:
            print(f"  {dyn.value} at offset {dyn.offset}")
    
    # Get expressions
    expressions = list(measure.getElementsByClass(music21.expressions.TextExpression))
    if expressions:
        print("Expressions:")
        for expr in expressions:
            print(f"  '{expr.content}' at offset {expr.offset}")
    
    return {
        'measure_number': measure.number,
        'offset': measure.offset,
        'notes': notes,
        'rests': rests,
        'chords': chords,
        'dynamics': dynamics,
        'expressions': expressions
    }

def analyze_base_score(file_path, measure_number):
    """Analyze the base score to see all parts in the specified measure."""
    print(f"\n{'='*60}")
    print(f"ANALYZING BASE SCORE: {file_path}")
    print(f"{'='*60}")
    
    score = music21.converter.parse(file_path)
    
    print(f"Total parts in base score: {len(score.parts)}")
    
    base_results = {}
    for i, part in enumerate(score.parts):
        part_name = part.partName or f"Part {i+1}"
        print(f"\n--- Base Part {i+1}: {part_name} ---")
        
        # Analyze the measure
        result = analyze_measure(part, measure_number, f"Base {part_name}")
        base_results[part_name] = result
        
        # Also look at voices within this part
        measures = list(part.getElementsByClass(music21.stream.Measure))
        if measure_number <= len(measures):
            measure = measures[measure_number - 1]
            voices = list(measure.getElementsByClass(music21.stream.Voice))
            if voices:
                print(f"  Voices in this measure: {len(voices)}")
                for j, voice in enumerate(voices):
                    voice_id = voice.id or f"Voice {j+1}"
                    print(f"    Voice {voice_id}:")
                    voice_notes = list(voice.getElementsByClass(music21.note.Note))
                    voice_rests = list(voice.getElementsByClass(music21.note.Rest))
                    voice_chords = list(voice.getElementsByClass(music21.chord.Chord))
                    print(f"      Notes: {len(voice_notes)}, Rests: {len(voice_rests)}, Chords: {len(voice_chords)}")
                    
                    if voice_notes:
                        for k, note in enumerate(voice_notes):
                            print(f"        Note {k+1}: {note.pitch.name}{note.pitch.octave} (duration: {note.duration.quarterLength}, offset: {note.offset})")
                    
                    if voice_chords:
                        for k, chord in enumerate(voice_chords):
                            pitches = [f"{p.name}{p.octave}" for p in chord.pitches]
                            print(f"        Chord {k+1}: {pitches} (duration: {chord.duration.quarterLength}, offset: {chord.offset})")
                    
                    if voice_rests:
                        for k, rest in enumerate(voice_rests):
                            print(f"        Rest {k+1}: duration {rest.duration.quarterLength}, offset: {rest.offset}")
    
    return base_results

def analyze_voice_parts(voice_dir, measure_number):
    """Analyze all voice parts for the specified measure."""
    print(f"\n{'='*60}")
    print(f"ANALYZING VOICE PARTS: {voice_dir}")
    print(f"{'='*60}")
    
    voice_files = {
        'Soprano': 'Crossing The Bar-Soprano.musicxml',
        'Alto': 'Crossing The Bar-Alto.musicxml', 
        'Tenor': 'Crossing The Bar-Tenor.musicxml',
        'Bass': 'Crossing The Bar-Bass.musicxml'
    }
    
    voice_results = {}
    
    for voice_name, filename in voice_files.items():
        filepath = Path(voice_dir) / filename
        if not filepath.exists():
            print(f"ERROR: {filepath} not found")
            continue
            
        print(f"\n--- {voice_name} Voice Part ---")
        score = music21.converter.parse(str(filepath))
        
        if not score.parts:
            print(f"ERROR: No parts found in {filename}")
            continue
            
        part = score.parts[0]  # Voice parts should have only one part
        result = analyze_measure(part, measure_number, voice_name)
        voice_results[voice_name] = result
    
    return voice_results

def compare_results(base_results, voice_results, measure_number):
    """Compare the base results with voice part results."""
    print(f"\n{'='*60}")
    print(f"COMPARISON ANALYSIS - MEASURE {measure_number}")
    print(f"{'='*60}")
    
    # Expected mapping based on typical SATB layout
    expected_mapping = {
        'Soprano': 'Part 1 Voice 1',
        'Alto': 'Part 1 Voice 2', 
        'Tenor': 'Part 2 Voice 1',
        'Bass': 'Part 2 Voice 2'
    }
    
    print("\nExpected voice mapping:")
    for voice, expected in expected_mapping.items():
        print(f"  {voice} should match {expected} from base score")
    
    print(f"\nDetailed comparison:")
    
    for voice_name, voice_result in voice_results.items():
        print(f"\n--- {voice_name} Analysis ---")
        
        if voice_result is None:
            print(f"ERROR: No data for {voice_name}")
            continue
            
        voice_notes = voice_result['notes']
        voice_chords = voice_result['chords']
        voice_rests = voice_result['rests']
        
        print(f"Voice part has: {len(voice_notes)} notes, {len(voice_chords)} chords, {len(voice_rests)} rests")
        
        # Compare with base score
        print(f"Base score analysis:")
        for part_name, base_result in base_results.items():
            if base_result is None:
                continue
            base_notes = base_result['notes']
            base_chords = base_result['chords']
            base_rests = base_result['rests']
            print(f"  {part_name}: {len(base_notes)} notes, {len(base_chords)} chords, {len(base_rests)} rests")
        
        # Check if voice part is empty when it shouldn't be
        total_voice_elements = len(voice_notes) + len(voice_chords) + len(voice_rests)
        if total_voice_elements == 0:
            print(f"⚠️  WARNING: {voice_name} appears to be empty!")
        
        # Check for obvious issues
        if len(voice_notes) == 0 and len(voice_chords) == 0 and len(voice_rests) > 0:
            print(f"⚠️  WARNING: {voice_name} has only rests - possible extraction issue")
        
        if len(voice_notes) > 10:  # Arbitrary threshold
            print(f"⚠️  WARNING: {voice_name} has unusually many notes ({len(voice_notes)}) - possible duplication")

def main():
    measure_number = 29
    
    # Analyze base score
    base_results = analyze_base_score('Crossing The Bar-base.musicxml', measure_number)
    
    # Analyze voice parts
    voice_results = analyze_voice_parts('Crossing The Bar_voices', measure_number)
    
    # Compare results
    compare_results(base_results, voice_results, measure_number)

if __name__ == "__main__":
    main()