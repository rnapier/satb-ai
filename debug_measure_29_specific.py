#!/usr/bin/env python3
"""
Debug script to specifically check measure 29 slur preservation.
"""

import music21
from satb_splitter.main import split_satb_voices
import os
import shutil

def check_measure_29_slurs():
    """Check specifically for slurs in measure 29."""
    print("🔍 CHECKING MEASURE 29 SLURS SPECIFICALLY")
    print("=" * 50)
    
    # Remove old output and generate fresh
    if os.path.exists('Crossing The Bar_voices'):
        shutil.rmtree('Crossing The Bar_voices')
    
    voices = split_satb_voices('Crossing The Bar.musicxml', 'Crossing The Bar_voices')
    
    # Check each voice's measure 29
    for voice_name, voice_score in voices.items():
        print(f"\n📋 {voice_name} Measure 29:")
        
        for part in voice_score.parts:
            for measure in part.getElementsByClass('Measure'):
                if hasattr(measure, 'number') and measure.number == 29:
                    notes = list(measure.flatten().notes)
                    print(f"  Notes: {[(n.pitch.name + str(n.pitch.octave)) for n in notes]}")
                    
                    # Check for slur notations on notes
                    for i, note in enumerate(notes):
                        has_slur = False
                        if hasattr(note, 'notations') and note.notations:
                            for notation in note.notations:
                                if hasattr(notation, 'classes') and 'Slur' in notation.classes:
                                    print(f"    Note {i} ({note.pitch.name}{note.pitch.octave}) has slur {notation.type}")
                                    has_slur = True
                        
                        if not has_slur:
                            print(f"    Note {i} ({note.pitch.name}{note.pitch.octave}) has NO slur")
    
    # Also check the files directly
    print(f"\n📄 Checking exported files for measure 29 slurs...")
    
    for voice_name in ['Soprano', 'Alto', 'Tenor', 'Bass']:
        filename = f"Crossing The Bar_voices/Crossing The Bar-{voice_name}.musicxml"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                content = f.read()
                
                # Find measure 29
                if 'number="29"' in content:
                    start = content.find('number="29"')
                    end = content.find('</measure>', start) + 10
                    measure_content = content[start:end]
                    
                    slur_count = measure_content.count('<slur')
                    print(f"  {voice_name}: {slur_count} slur tags in measure 29")
                    
                    if slur_count > 0:
                        # Show the slur tags
                        lines = measure_content.split('\n')
                        for line_num, line in enumerate(lines):
                            if '<slur' in line:
                                print(f"    Line {line_num}: {line.strip()}")

if __name__ == "__main__":
    check_measure_29_slurs()