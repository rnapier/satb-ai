#!/usr/bin/env python3
"""
Diagnostic script to validate voice mapping assumptions.
"""

import music21
from pathlib import Path

def diagnose_voice_structure():
    """Diagnose the actual voice structure in the base score."""
    print("=== DIAGNOSING VOICE STRUCTURE ===")
    
    score = music21.converter.parse('Crossing The Bar-base.musicxml')
    
    print(f"Total parts: {len(score.parts)}")
    
    for part_idx, part in enumerate(score.parts):
        print(f"\n--- Part {part_idx}: {part.partName} ---")
        
        # Look at measure 29 specifically
        measures = list(part.getElementsByClass(music21.stream.Measure))
        if len(measures) >= 29:
            measure_29 = measures[28]  # 0-based index
            print(f"Measure 29 offset: {measure_29.offset}")
            
            voices = list(measure_29.getElementsByClass(music21.stream.Voice))
            print(f"Voices in measure 29: {len(voices)}")
            
            for voice in voices:
                voice_id = voice.id
                print(f"  Voice ID: {voice_id}")
                
                notes = list(voice.getElementsByClass(music21.note.Note))
                rests = list(voice.getElementsByClass(music21.note.Rest))
                
                print(f"    Notes: {len(notes)}, Rests: {len(rests)}")
                
                if notes:
                    print("    Note details:")
                    for i, note in enumerate(notes):
                        print(f"      {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
                
                if rests:
                    print("    Rest details:")
                    for i, rest in enumerate(rests):
                        print(f"      {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")

def diagnose_timing_issues():
    """Diagnose timing and offset calculation issues."""
    print("\n=== DIAGNOSING TIMING ISSUES ===")
    
    # Check the voice parts
    voice_files = {
        'Soprano': 'Crossing The Bar_voices/Crossing The Bar-Soprano.musicxml',
        'Alto': 'Crossing The Bar_voices/Crossing The Bar-Alto.musicxml', 
        'Tenor': 'Crossing The Bar_voices/Crossing The Bar-Tenor.musicxml',
        'Bass': 'Crossing The Bar_voices/Crossing The Bar-Bass.musicxml'
    }
    
    for voice_name, filepath in voice_files.items():
        if not Path(filepath).exists():
            continue
            
        print(f"\n--- {voice_name} Timing Analysis ---")
        score = music21.converter.parse(filepath)
        part = score.parts[0]
        
        measures = list(part.getElementsByClass(music21.stream.Measure))
        if len(measures) >= 29:
            measure_29 = measures[28]
            print(f"Measure 29 offset: {measure_29.offset}")
            print(f"Measure number: {measure_29.number}")
            
            # Check total duration of elements
            notes = list(measure_29.getElementsByClass(music21.note.Note))
            rests = list(measure_29.getElementsByClass(music21.note.Rest))
            
            total_duration = 0
            print("Element timeline:")
            all_elements = []
            
            for note in notes:
                all_elements.append(('Note', note.offset, note.duration.quarterLength, f"{note.pitch.name}{note.pitch.octave}"))
            for rest in rests:
                all_elements.append(('Rest', rest.offset, rest.duration.quarterLength, "rest"))
            
            # Sort by offset
            all_elements.sort(key=lambda x: x[1])
            
            for elem_type, offset, duration, content in all_elements:
                print(f"  {elem_type}: offset={offset}, duration={duration}, content={content}")
                if offset + duration > total_duration:
                    total_duration = offset + duration
            
            print(f"Total measure duration: {total_duration}")
            
            # Check for gaps or overlaps
            if len(all_elements) > 1:
                for i in range(len(all_elements) - 1):
                    current_end = all_elements[i][1] + all_elements[i][2]
                    next_start = all_elements[i+1][1]
                    if current_end != next_start:
                        gap = next_start - current_end
                        print(f"  ⚠️  Gap/Overlap: {gap} beats between elements {i+1} and {i+2}")

def test_voice_mapping_hypothesis():
    """Test if the voice mapping in the splitter is correct."""
    print("\n=== TESTING VOICE MAPPING HYPOTHESIS ===")
    
    # Load base score and check what the current mapping produces
    score = music21.converter.parse('Crossing The Bar-base.musicxml')
    
    # Current mapping from voice_splitter.py
    current_mapping = {
        (0, '1'): 'Soprano',  # Part 1, Voice 1 -> Soprano
        (0, '2'): 'Alto',     # Part 1, Voice 2 -> Alto
        (1, '5'): 'Tenor',    # Part 2, Voice 5 -> Tenor
        (1, '6'): 'Bass',     # Part 2, Voice 6 -> Bass
    }
    
    print("Current mapping being used:")
    for (part_idx, voice_id), target in current_mapping.items():
        print(f"  Part {part_idx}, Voice {voice_id} -> {target}")
    
    print("\nActual voice structure found:")
    for part_idx, part in enumerate(score.parts):
        measures = list(part.getElementsByClass(music21.stream.Measure))
        if len(measures) >= 29:
            measure_29 = measures[28]
            voices = list(measure_29.getElementsByClass(music21.stream.Voice))
            
            for voice in voices:
                voice_id = str(voice.id) if voice.id else 'unknown'
                notes = list(voice.getElementsByClass(music21.note.Note))
                
                key = (part_idx, voice_id)
                mapped_to = current_mapping.get(key, "UNMAPPED")
                
                print(f"  Part {part_idx}, Voice {voice_id} -> {mapped_to} ({len(notes)} notes)")
                
                if mapped_to == "UNMAPPED":
                    print(f"    ⚠️  This voice is not being mapped to any SATB part!")

def main():
    diagnose_voice_structure()
    diagnose_timing_issues()
    test_voice_mapping_hypothesis()

if __name__ == "__main__":
    main()