#!/usr/bin/env python3
"""
Debug the voice identification process.
"""

import music21
from satb_splitter.voice_identifier import VoiceIdentifier

def debug_voice_identification():
    """Debug how the voice identifier works."""
    print("🔍 DEBUGGING VOICE IDENTIFICATION")
    print("=" * 50)
    
    score = music21.converter.parse("Crossing The Bar.musicxml")
    
    # Use the existing voice identifier
    identifier = VoiceIdentifier(score)
    voice_mapping = identifier.analyze_score()
    
    print(f"Voice mapping results:")
    print(f"  Soprano: Part {voice_mapping.soprano.part_index}, Voice {voice_mapping.soprano.voice_id}")
    print(f"  Alto: Part {voice_mapping.alto.part_index}, Voice {voice_mapping.alto.voice_id}")
    print(f"  Tenor: Part {voice_mapping.tenor.part_index}, Voice {voice_mapping.tenor.voice_id}")
    print(f"  Bass: Part {voice_mapping.bass.part_index}, Voice {voice_mapping.bass.voice_id}")
    
    # Now let's see what notes are actually in each identified voice
    print(f"\n🔍 Analyzing identified voices:")
    
    voice_configs = [
        ("Soprano", voice_mapping.soprano.part_index, voice_mapping.soprano.voice_id),
        ("Alto", voice_mapping.alto.part_index, voice_mapping.alto.voice_id),
        ("Tenor", voice_mapping.tenor.part_index, voice_mapping.tenor.voice_id),
        ("Bass", voice_mapping.bass.part_index, voice_mapping.bass.voice_id)
    ]
    
    for voice_name, part_idx, voice_id in voice_configs:
        print(f"\n📋 {voice_name} (Part {part_idx}, Voice {voice_id}):")
        
        if part_idx >= len(score.parts):
            print(f"  ❌ Part {part_idx} doesn't exist")
            continue
            
        part = score.parts[part_idx]
        
        # Look for measure 29
        measure_29 = None
        for measure in part.getElementsByClass('Measure'):
            if hasattr(measure, 'number') and measure.number == 29:
                measure_29 = measure
                break
        
        if not measure_29:
            print(f"  ❌ No measure 29 found")
            continue
        
        print(f"  Measure 29 found")
        
        # Find notes with the target voice ID
        voice_notes = []
        all_notes = []
        
        for note in measure_29.flatten().notes:
            all_notes.append(note)
            note_voice = getattr(note, 'voice', None)
            if note_voice == voice_id:
                voice_notes.append(note)
        
        print(f"    All notes in M29: {len(all_notes)}")
        print(f"    Notes with voice {voice_id}: {len(voice_notes)}")
        
        if voice_notes:
            pitches = []
            for note in voice_notes:
                if hasattr(note, 'pitch'):
                    pitches.append(note.pitch.name + str(note.pitch.octave))
                else:
                    pitches.append("REST")
            print(f"    Voice {voice_id} notes: {pitches}")
        else:
            print(f"    ❌ No notes found with voice {voice_id}")
            # Show what voices are actually present
            voices_present = set()
            for note in all_notes:
                voice = getattr(note, 'voice', 'no voice')
                voices_present.add(voice)
            print(f"    Voices actually present: {voices_present}")

if __name__ == "__main__":
    debug_voice_identification()