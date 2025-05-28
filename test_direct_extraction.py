#!/usr/bin/env python3
"""
Test script for the new direct extraction architecture.
"""

from satb_splitter.direct_voice_extractor import extract_voices_directly
import tempfile
from pathlib import Path


def test_direct_extraction():
    """Test the direct extraction approach."""
    print("🧪 TESTING DIRECT EXTRACTION APPROACH")
    print("=" * 50)
    
    # Extract voices using new approach
    print("🔄 Extracting voices with direct approach...")
    voice_scores = extract_voices_directly("Crossing The Bar.musicxml")
    
    print(f"✅ Extracted {len(voice_scores)} voices: {list(voice_scores.keys())}")
    
    # Test each voice for measure 29 slurs
    for voice_name, voice_score in voice_scores.items():
        print(f"\n📋 Testing {voice_name}:")
        
        if not voice_score.parts:
            print(f"  ❌ No parts in {voice_name}")
            continue
            
        voice_part = voice_score.parts[0]
        
        # Check measure 29
        measure_29 = None
        for measure in voice_part.getElementsByClass('Measure'):
            if hasattr(measure, 'number') and measure.number == 29:
                measure_29 = measure
                break
        
        if not measure_29:
            print(f"  ❌ No measure 29 in {voice_name}")
            continue
        
        # Check notes in measure 29
        notes = list(measure_29.flatten().notes)
        print(f"  Notes in M29: {[(n.pitch.name + str(n.pitch.octave)) for n in notes]}")
        
        # Check for slur notations on notes
        slur_notations = 0
        for note in notes:
            if hasattr(note, 'notations') and note.notations:
                for notation in note.notations:
                    if hasattr(notation, 'classes') and 'Slur' in notation.classes:
                        print(f"    ✅ Note {note.pitch.name}{note.pitch.octave} has slur notation")
                        slur_notations += 1
        
        # Check for part-level slurs
        part_slurs = list(voice_part.flatten().getElementsByClass('Spanner'))
        slur_spanners = [s for s in part_slurs if hasattr(s, 'classes') and 'Slur' in s.classes]
        
        print(f"  Part-level slurs: {len(slur_spanners)}")
        
        for slur in slur_spanners:
            try:
                spanned = slur.getSpannedElements()
                if len(spanned) >= 2:
                    start_pitch = spanned[0].pitch.name + str(spanned[0].pitch.octave)
                    end_pitch = spanned[-1].pitch.name + str(spanned[-1].pitch.octave)
                    
                    # Check if affects measure 29
                    affects_29 = False
                    for element in spanned:
                        if hasattr(element, 'activeSite') and element.activeSite:
                            if hasattr(element.activeSite, 'number') and element.activeSite.number == 29:
                                affects_29 = True
                                break
                    
                    if affects_29:
                        print(f"    ✅ Slur affecting M29: {start_pitch} → {end_pitch}")
            except:
                pass
        
        # Test export to MusicXML
        print(f"  Testing MusicXML export...")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / f"direct_{voice_name}.musicxml"
            voice_score.write('musicxml', fp=str(temp_path))
            
            # Check exported file for measure 29 slurs
            with open(temp_path, 'r') as f:
                content = f.read()
                
                if 'number="29"' in content:
                    measure_29_start = content.find('number="29"')
                    measure_29_end = content.find('</measure>', measure_29_start) + 10
                    measure_29_content = content[measure_29_start:measure_29_end]
                    
                    slur_count = measure_29_content.count('<slur')
                    print(f"    Exported M29 slur tags: {slur_count}")
                    
                    if slur_count > 0:
                        print(f"    ✅ SUCCESS! Slurs exported to MusicXML")
                    else:
                        print(f"    ❌ No slurs in exported M29")
                else:
                    print(f"    ❌ No measure 29 in exported file")


if __name__ == "__main__":
    test_direct_extraction()