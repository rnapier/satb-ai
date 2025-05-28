#!/usr/bin/env python3
"""
Even simpler fix: Copy slurs based on which notes are actually present in the extracted voice.
"""

import music21
import copy
import tempfile
from pathlib import Path

def extract_alto_voice_simple():
    """Extract just the Alto voice notes and find relevant slurs."""
    print("🔧 SIMPLE ALTO EXTRACTION WITH SLUR COPYING")
    print("=" * 50)
    
    # Load original
    original_score = music21.converter.parse("Crossing The Bar.musicxml")
    
    # Create Alto score
    alto_score = music21.stream.Score()
    alto_part = music21.stream.Part()
    alto_score.append(alto_part)
    
    # Extract Alto notes (voice 2) - manually for measure 29 test
    print("🔄 Extracting Alto notes from measure 29...")
    
    for measure in original_score.parts[0].getElementsByClass('Measure'):
        if hasattr(measure, 'number') and measure.number == 29:
            print(f"  Processing measure {measure.number}...")
            
            alto_measure = music21.stream.Measure(number=29)
            
            # From the original MusicXML analysis, we know Alto has E4, F4, G4 in measure 29
            # Let's extract these specific notes
            all_notes = list(measure.flatten().notes)
            print(f"    All notes in measure: {[(n.pitch.name + str(n.pitch.octave)) for n in all_notes]}")
            
            # Find the E4, F4, G4 sequence (Alto voice 2)
            alto_notes = []
            for note in all_notes:
                pitch_str = note.pitch.name + str(note.pitch.octave)
                if pitch_str in ['E4', 'F4', 'G4']:
                    alto_notes.append(note)
                    print(f"      Found Alto note: {pitch_str}")
            
            # Add notes to alto measure
            for note in alto_notes:
                alto_measure.append(copy.deepcopy(note))
            
            alto_part.append(alto_measure)
            break
    
    # Now find slurs that involve E4→F4 (the specific slur we want)
    print(f"\n🔄 Finding relevant slurs...")
    
    for spanner in original_score.parts[0].flatten().getElementsByClass('Spanner'):
        if hasattr(spanner, 'classes') and 'Slur' in spanner.classes:
            try:
                spanned = spanner.getSpannedElements()
                if len(spanned) >= 2:
                    start_pitch = spanned[0].pitch.name + str(spanned[0].pitch.octave)
                    end_pitch = spanned[-1].pitch.name + str(spanned[-1].pitch.octave)
                    
                    # Check if this is the E4→F4 slur
                    if start_pitch == 'E4' and end_pitch == 'F4':
                        print(f"  ✅ Found E4→F4 slur!")
                        
                        # Find the corresponding notes in our alto measure
                        alto_notes = list(alto_part.flatten().notes)
                        e4_note = None
                        f4_note = None
                        
                        for note in alto_notes:
                            pitch_str = note.pitch.name + str(note.pitch.octave)
                            if pitch_str == 'E4':
                                e4_note = note
                            elif pitch_str == 'F4':
                                f4_note = note
                        
                        if e4_note and f4_note:
                            # Create new slur
                            new_slur = music21.spanner.Slur()
                            new_slur.addSpannedElements([e4_note, f4_note])
                            alto_part.append(new_slur)
                            print(f"    ✅ Added E4→F4 slur to Alto part!")
                        else:
                            print(f"    ❌ Could not find E4 or F4 notes in Alto part")
                    
                    else:
                        print(f"    Other slur: {start_pitch} → {end_pitch}")
            except Exception as e:
                print(f"    ❌ Slur error: {e}")
    
    # Test export
    print(f"\n🔄 Testing export...")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "simple_alto.musicxml"
        alto_score.write('musicxml', fp=str(temp_path))
        
        # Check file content
        with open(temp_path, 'r') as f:
            content = f.read()
            print(f"  File size: {len(content)} chars")
            
            # Look for measure 29
            if 'number="29"' in content:
                measure_29_start = content.find('number="29"')
                measure_29_end = content.find('</measure>', measure_29_start) + 10
                measure_29_content = content[measure_29_start:measure_29_end]
                
                slur_count = measure_29_content.count('<slur')
                print(f"  Slur tags in exported measure 29: {slur_count}")
                
                if slur_count > 0:
                    print(f"  ✅ SUCCESS! Slurs are in exported file!")
                    
                    # Show the actual slur markup
                    lines = measure_29_content.split('\n')
                    for i, line in enumerate(lines):
                        if '<slur' in line:
                            print(f"    Line {i}: {line.strip()}")
                    
                    print(f"\n📋 Full measure 29 content:")
                    print(measure_29_content)
                else:
                    print(f"  ❌ Still no slurs in exported file")
                    print(f"\n📋 Measure 29 content (no slurs):")
                    print(measure_29_content)
            else:
                print(f"  ❌ No measure 29 found in exported file")

if __name__ == "__main__":
    extract_alto_voice_simple()