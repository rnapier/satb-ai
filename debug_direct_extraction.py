#!/usr/bin/env python3
"""
Debug the direct extraction approach.
"""

import music21

def debug_voice_structure():
    """Debug the voice structure in the original score."""
    print("🔍 DEBUGGING VOICE STRUCTURE")
    print("=" * 50)
    
    score = music21.converter.parse("Crossing The Bar.musicxml")
    
    print(f"Score has {len(score.parts)} parts")
    
    for part_idx, part in enumerate(score.parts):
        print(f"\n📋 Part {part_idx}:")
        
        # Check first few measures
        measures = list(part.getElementsByClass('Measure'))
        print(f"  Has {len(measures)} measures")
        
        if len(measures) >= 29:
            measure_29 = measures[28]  # 0-based indexing
            print(f"  Measure 29 found: number = {getattr(measure_29, 'number', 'no number')}")
            
            # Check notes in measure 29
            notes = list(measure_29.flatten().notes)
            print(f"    Notes in M29: {len(notes)}")
            
            for i, note in enumerate(notes):
                voice = getattr(note, 'voice', 'no voice')
                pitch = getattr(note, 'pitch', 'no pitch')
                if hasattr(pitch, 'name') and hasattr(pitch, 'octave'):
                    pitch_str = pitch.name + str(pitch.octave)
                else:
                    pitch_str = str(pitch)
                print(f"      Note {i}: {pitch_str}, voice={voice}")
        
        # Check spanners
        spanners = list(part.flatten().getElementsByClass('Spanner'))
        slur_spanners = [s for s in spanners if hasattr(s, 'classes') and 'Slur' in s.classes]
        print(f"  Slurs in part: {len(slur_spanners)}")
        
        if slur_spanners:
            print("    Slur details:")
            for i, slur in enumerate(slur_spanners[:3]):  # Show first 3
                try:
                    spanned = slur.getSpannedElements()
                    if len(spanned) >= 2:
                        start = spanned[0]
                        end = spanned[-1]
                        start_voice = getattr(start, 'voice', 'no voice')
                        end_voice = getattr(end, 'voice', 'no voice')
                        start_pitch = getattr(start, 'pitch', 'no pitch')
                        end_pitch = getattr(end, 'pitch', 'no pitch')
                        
                        if hasattr(start_pitch, 'name'):
                            start_str = start_pitch.name + str(start_pitch.octave)
                        else:
                            start_str = str(start_pitch)
                            
                        if hasattr(end_pitch, 'name'):
                            end_str = end_pitch.name + str(end_pitch.octave)
                        else:
                            end_str = str(end_pitch)
                            
                        print(f"      Slur {i}: {start_str} (voice {start_voice}) → {end_str} (voice {end_voice})")
                except Exception as e:
                    print(f"      Slur {i}: Error analyzing - {e}")

if __name__ == "__main__":
    debug_voice_structure()