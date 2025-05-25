#!/usr/bin/env python3
"""
Analyze measure 4 timing issue where eighth rest appears at beat 4.5 instead of beat 3 in Soprano part.
"""

import music21
from satb_splitter.voice_splitter import split_satb_voices

def analyze_measure_4_timing():
    """Analyze the timing issue in measure 4."""
    print("=== Analyzing Measure 4 Timing Issue ===")
    
    # Load original score
    print("\n1. Loading original MusicXML file...")
    original_score = music21.converter.parse("Crossing The Bar.musicxml")
    
    # Analyze original measure 4
    print("\n2. Analyzing original measure 4 structure...")
    first_part = original_score.parts[0]  # Treble clef part
    measures = list(first_part.getElementsByClass(music21.stream.Measure))
    measure_4 = measures[3]  # 0-indexed, so measure 4 is index 3
    
    print(f"Measure 4 number: {measure_4.number}")
    print(f"Measure 4 duration: {measure_4.duration.quarterLength}")
    
    # Get voices in measure 4
    voices = list(measure_4.getElementsByClass(music21.stream.Voice))
    print(f"Found {len(voices)} voices in measure 4")
    
    for voice in voices:
        voice_id = str(voice.id) if voice.id else 'unknown'
        print(f"\n--- Voice {voice_id} (Soprano if voice 1) ---")
        
        # Get all elements in this voice with their offsets
        elements = []
        for element in voice.getElementsByClass([music21.note.Note, music21.note.Rest]):
            elements.append((element.offset, element))
        
        # Sort by offset
        elements.sort(key=lambda x: x[0])
        
        cumulative_offset = 0.0
        for offset, element in elements:
            if isinstance(element, music21.note.Note):
                print(f"  Offset {offset}: Note {element.pitch} (duration: {element.duration.quarterLength})")
            else:
                print(f"  Offset {offset}: Rest (duration: {element.duration.quarterLength})")
            
            # Calculate beat position (assuming 4/4 time)
            beat = offset + 1  # Convert 0-based offset to 1-based beat
            print(f"    Beat position: {beat}")
            
            cumulative_offset += element.duration.quarterLength
    
    # Now analyze the split voices
    print("\n3. Analyzing split voices...")
    split_result = split_satb_voices("Crossing The Bar.musicxml")
    
    soprano_score = split_result['Soprano']
    soprano_part = soprano_score.parts[0]
    soprano_measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
    soprano_measure_4 = soprano_measures[3]
    
    print(f"\nSoprano measure 4 analysis:")
    print(f"Measure number: {soprano_measure_4.number}")
    print(f"Measure duration: {soprano_measure_4.duration.quarterLength}")
    
    # Get all elements in soprano measure 4
    elements = []
    for element in soprano_measure_4.getElementsByClass([music21.note.Note, music21.note.Rest]):
        elements.append((element.offset, element))
    
    # Sort by offset
    elements.sort(key=lambda x: x[0])
    
    print("\nSoprano measure 4 elements:")
    for offset, element in elements:
        if isinstance(element, music21.note.Note):
            print(f"  Offset {offset}: Note {element.pitch} (duration: {element.duration.quarterLength})")
        else:
            print(f"  Offset {offset}: Rest (duration: {element.duration.quarterLength})")
        
        # Calculate beat position (assuming 4/4 time)
        beat = offset + 1  # Convert 0-based offset to 1-based beat
        print(f"    Beat position: {beat}")
        
        # Check if this is the problematic eighth rest
        if isinstance(element, music21.note.Rest) and element.duration.quarterLength == 0.5:
            if beat == 4.5:
                print(f"    *** PROBLEM FOUND: Eighth rest at beat {beat} (should be at beat 3) ***")
            elif beat == 3.0:
                print(f"    *** CORRECT: Eighth rest at beat {beat} ***")
    
    # Compare original vs split timing
    print("\n4. Comparing original vs split timing...")
    
    # Get original voice 1 elements
    original_voice_1 = None
    for voice in voices:
        if str(voice.id) == '1':
            original_voice_1 = voice
            break
    
    if original_voice_1:
        print("\nOriginal Voice 1 (should become Soprano):")
        orig_elements = []
        for element in original_voice_1.getElementsByClass([music21.note.Note, music21.note.Rest]):
            orig_elements.append((element.offset, element))
        orig_elements.sort(key=lambda x: x[0])
        
        for offset, element in orig_elements:
            beat = offset + 1
            if isinstance(element, music21.note.Note):
                print(f"  Beat {beat}: Note {element.pitch} (duration: {element.duration.quarterLength})")
            else:
                print(f"  Beat {beat}: Rest (duration: {element.duration.quarterLength})")
    
    print("\nSplit Soprano:")
    for offset, element in elements:
        beat = offset + 1
        if isinstance(element, music21.note.Note):
            print(f"  Beat {beat}: Note {element.pitch} (duration: {element.duration.quarterLength})")
        else:
            print(f"  Beat {beat}: Rest (duration: {element.duration.quarterLength})")

if __name__ == "__main__":
    analyze_measure_4_timing()