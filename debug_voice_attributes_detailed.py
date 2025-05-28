#!/usr/bin/env python3
"""
Detailed debugging of voice attributes in the MusicXML file.
"""

import music21

def debug_voice_attributes_detailed():
    """Debug voice attributes more thoroughly."""
    print("🔍 DETAILED VOICE ATTRIBUTE DEBUGGING")
    print("=" * 60)
    
    score = music21.converter.parse("Crossing The Bar.musicxml")
    
    print(f"Score has {len(score.parts)} parts")
    
    for part_idx, part in enumerate(score.parts):
        print(f"\n📋 Part {part_idx}:")
        
        # Check multiple measures to see voice pattern
        for measure_num in [1, 2, 29, 30]:
            print(f"\n  Measure {measure_num}:")
            
            measure = None
            for m in part.getElementsByClass('Measure'):
                if hasattr(m, 'number') and m.number == measure_num:
                    measure = m
                    break
            
            if not measure:
                print(f"    ❌ Measure {measure_num} not found")
                continue
            
            # Check all elements in the measure, not just flattened
            print(f"    Direct measure elements:")
            for i, element in enumerate(measure):
                voice_attr = getattr(element, 'voice', 'no voice attr')
                element_type = type(element).__name__
                
                if hasattr(element, 'pitch'):
                    pitch = element.pitch.name + str(element.pitch.octave)
                    print(f"      {i}: {element_type} {pitch}, voice={voice_attr}")
                elif hasattr(element, 'isRest') and element.isRest:
                    print(f"      {i}: {element_type} REST, voice={voice_attr}")
                else:
                    print(f"      {i}: {element_type}, voice={voice_attr}")
            
            # Also check flattened for comparison
            print(f"    Flattened notes:")
            flattened_notes = list(measure.flatten().notes)
            for i, note in enumerate(flattened_notes):
                voice_attr = getattr(note, 'voice', 'no voice attr')
                if hasattr(note, 'pitch'):
                    pitch = note.pitch.name + str(note.pitch.octave)
                    print(f"      {i}: {pitch}, voice={voice_attr}")
                else:
                    print(f"      {i}: REST, voice={voice_attr}")
            
            # Check Voice stream objects in the measure
            print(f"    Voice stream objects:")
            voice_streams = measure.getElementsByClass('Voice')
            if voice_streams:
                for i, voice_stream in enumerate(voice_streams):
                    voice_id = getattr(voice_stream, 'id', f'voice_{i}')
                    voice_notes = list(voice_stream.notes)
                    print(f"      Voice stream {i} (id={voice_id}): {len(voice_notes)} notes")
                    for note in voice_notes[:3]:  # Show first 3
                        if hasattr(note, 'pitch'):
                            pitch = note.pitch.name + str(note.pitch.octave)
                            print(f"        {pitch}")
                        else:
                            print(f"        REST")
            else:
                print(f"      No Voice stream objects found")
            
            if measure_num == 1:  # Only check first measure for detail
                break

if __name__ == "__main__":
    debug_voice_attributes_detailed()