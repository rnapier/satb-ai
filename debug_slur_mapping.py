#!/usr/bin/env python3
"""
Debug slur mapping with the corrected voice extraction.
"""

import music21
from satb_splitter.direct_voice_extractor import DirectVoiceExtractor

def debug_slur_mapping():
    """Debug the slur mapping process."""
    print("🔍 DEBUGGING SLUR MAPPING")
    print("=" * 50)
    
    score = music21.converter.parse("Crossing The Bar.musicxml")
    
    # Check slurs in original score
    print("📋 Original slurs in score:")
    for part_idx, part in enumerate(score.parts):
        slurs = list(part.flatten().getElementsByClass('Spanner'))
        slur_objects = [s for s in slurs if hasattr(s, 'classes') and 'Slur' in s.classes]
        print(f"  Part {part_idx}: {len(slur_objects)} slurs")
        
        for i, slur in enumerate(slur_objects):
            try:
                spanned = slur.getSpannedElements()
                if len(spanned) >= 2:
                    start = spanned[0]
                    end = spanned[-1]
                    
                    start_pitch = start.pitch.name + str(start.pitch.octave)
                    end_pitch = end.pitch.name + str(end.pitch.octave)
                    
                    print(f"    Slur {i}: {start_pitch} → {end_pitch}")
                    
                    # Check which voice stream these notes belong to
                    start_voice = "unknown"
                    end_voice = "unknown"
                    
                    # Find the voice stream that contains these notes
                    if hasattr(start, 'activeSite') and start.activeSite:
                        if hasattr(start.activeSite, 'id'):
                            start_voice = start.activeSite.id
                    
                    if hasattr(end, 'activeSite') and end.activeSite:
                        if hasattr(end.activeSite, 'id'):
                            end_voice = end.activeSite.id
                    
                    print(f"      Start note in voice: {start_voice}")
                    print(f"      End note in voice: {end_voice}")
                    
            except Exception as e:
                print(f"    Slur {i}: Error analyzing - {e}")
    
    # Test direct extraction
    print(f"\n🔄 Testing direct extraction...")
    extractor = DirectVoiceExtractor(score)
    voice_scores = extractor.extract_all_voices()
    
    # Check if slurs are preserved
    for voice_name, voice_score in voice_scores.items():
        if voice_score.parts:
            part_slurs = list(voice_score.parts[0].flatten().getElementsByClass('Spanner'))
            slur_objects = [s for s in part_slurs if hasattr(s, 'classes') and 'Slur' in s.classes]
            print(f"  {voice_name}: {len(slur_objects)} slurs preserved")

if __name__ == "__main__":
    debug_slur_mapping()