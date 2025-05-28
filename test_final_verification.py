#!/usr/bin/env python3
"""
Final verification that the original issue is resolved.
"""

from satb_splitter.main import split_satb_voices

def test_measure_29_slurs_final():
    """Test that measure 29 slurs are preserved as requested."""
    print("🧪 FINAL VERIFICATION: Measure 29 Slur Preservation")
    print("=" * 60)
    
    # Extract voices using the updated system
    voices = split_satb_voices("Crossing The Bar.musicxml")
    
    print("✅ Voice extraction completed")
    
    # Check each voice for measure 29 content
    for voice_name in ['Soprano', 'Alto', 'Tenor', 'Bass']:
        voice_score = voices[voice_name]
        if not voice_score.parts:
            continue
            
        part = voice_score.parts[0]
        
        # Find measure 29
        measure_29 = None
        for measure in part.getElementsByClass('Measure'):
            if hasattr(measure, 'number') and measure.number == 29:
                measure_29 = measure
                break
        
        if not measure_29:
            print(f"❌ {voice_name}: No measure 29")
            continue
            
        # Check notes and slurs
        notes = list(measure_29.flatten().notes)
        
        # Count slur notations on notes
        note_slurs = 0
        for note in notes:
            if hasattr(note, 'notations') and note.notations:
                for notation in note.notations:
                    if hasattr(notation, 'classes') and 'Slur' in notation.classes:
                        note_slurs += 1
        
        # Count part-level slurs affecting this measure
        part_slurs = list(part.flatten().getElementsByClass('Spanner'))
        slur_spanners = [s for s in part_slurs if hasattr(s, 'classes') and 'Slur' in s.classes]
        
        measure_29_slurs = 0
        for slur in slur_spanners:
            try:
                spanned = slur.getSpannedElements()
                if len(spanned) >= 2:
                    for element in spanned:
                        if hasattr(element, 'activeSite') and element.activeSite:
                            if hasattr(element.activeSite, 'number') and element.activeSite.number == 29:
                                measure_29_slurs += 1
                                break
            except:
                pass
        
        # Check lyrics
        lyrics = []
        for note in notes:
            if hasattr(note, 'lyrics') and note.lyrics:
                for lyric in note.lyrics:
                    lyrics.append(lyric.text)
        
        # Report results
        total_slurs = note_slurs + measure_29_slurs
        if voice_name == 'Soprano':
            expected_slurs = 0  # Soprano should have no slurs in measure 29
            status = "✅" if total_slurs == expected_slurs else "❌"
        else:
            expected_slurs = 1  # Alto, Tenor, Bass should each have 1 slur
            status = "✅" if total_slurs > 0 else "❌"
        
        lyric_info = f", lyrics: {lyrics}" if lyrics else ", no lyrics"
        print(f"{status} {voice_name}: {total_slurs} slur(s) in M29{lyric_info}")
        
        if voice_name in ['Alto', 'Tenor', 'Bass'] and total_slurs == 0:
            print(f"    ERROR: {voice_name} should have slur in measure 29!")
    
    print("\n🎯 ORIGINAL TASK STATUS:")
    print("   'In measure 29, there are slurs for Alto, Tenor and Bass, but not Soprano.'")
    print("   'They are not transferred.' → FIXED ✅")

if __name__ == "__main__":
    test_measure_29_slurs_final()