#!/usr/bin/env python3
"""
Simple fix: Copy spanners when extracting voices and update their references.
"""

import music21
import copy
import tempfile
from pathlib import Path

def extract_voice_with_slurs(original_score, target_voice):
    """Extract a voice while preserving its slurs."""
    print(f"\n🔧 Extracting voice {target_voice} with slur preservation...")
    
    new_score = music21.stream.Score()
    
    for part_idx, original_part in enumerate(original_score.parts):
        print(f"  Processing part {part_idx}...")
        
        # Create new part
        new_part = music21.stream.Part()
        new_score.append(new_part)
        
        # Copy non-voice elements (metadata, etc.)
        for element in original_part:
            if not hasattr(element, 'voice') and not isinstance(element, music21.stream.Measure):
                new_part.append(copy.deepcopy(element))
        
        # Process measures and collect voice notes
        voice_notes_mapping = {}  # old_note -> new_note
        
        for measure in original_part.getElementsByClass('Measure'):
            new_measure = music21.stream.Measure(number=measure.number)
            
            # Copy measure-level elements (directions, etc.)
            for element in measure:
                if not hasattr(element, 'voice'):
                    new_measure.append(copy.deepcopy(element))
            
            # Copy notes from target voice
            for note in measure.flatten().notes:
                if hasattr(note, 'voice') and note.voice == target_voice:
                    new_note = copy.deepcopy(note)
                    new_measure.append(new_note)
                    voice_notes_mapping[note] = new_note
                    print(f"    Copied note {note.pitch.name}{note.pitch.octave} from voice {target_voice}")
            
            if len(new_measure) > 0:
                new_part.append(new_measure)
        
        # Now copy relevant spanners
        print(f"  Copying spanners for voice {target_voice}...")
        spanners_copied = 0
        
        for spanner in original_part.flatten().getElementsByClass('Spanner'):
            if hasattr(spanner, 'classes') and 'Slur' in spanner.classes:
                try:
                    # Get spanned elements
                    spanned_elements = spanner.getSpannedElements()
                    
                    # Check if all spanned elements are in our voice
                    new_spanned_elements = []
                    all_in_voice = True
                    
                    for element in spanned_elements:
                        if element in voice_notes_mapping:
                            new_spanned_elements.append(voice_notes_mapping[element])
                        else:
                            all_in_voice = False
                            break
                    
                    if all_in_voice and len(new_spanned_elements) >= 2:
                        # Create new slur with updated references
                        new_slur = music21.spanner.Slur()
                        new_slur.addSpannedElements(new_spanned_elements)
                        new_part.append(new_slur)
                        spanners_copied += 1
                        
                        start_pitch = new_spanned_elements[0].pitch.name + str(new_spanned_elements[0].pitch.octave)
                        end_pitch = new_spanned_elements[-1].pitch.name + str(new_spanned_elements[-1].pitch.octave)
                        print(f"    ✅ Copied slur: {start_pitch} → {end_pitch}")
                
                except Exception as e:
                    print(f"    ❌ Failed to copy slur: {e}")
        
        print(f"  Copied {spanners_copied} spanners for voice {target_voice}")
    
    return new_score

def test_simple_slur_fix():
    """Test the simple slur fix."""
    print("🔧 TESTING SIMPLE SLUR FIX")
    print("=" * 50)
    
    # Load original
    print("🔄 Loading original score...")
    original_score = music21.converter.parse("Crossing The Bar.musicxml")
    
    # Check original slurs
    original_spanners = list(original_score.parts[0].flatten().getElementsByClass('Spanner'))
    print(f"Original part 0 has {len(original_spanners)} spanners")
    
    # Extract Alto (voice 2) with slur preservation
    alto_score = extract_voice_with_slurs(original_score, '2')
    
    # Check Alto slurs
    alto_spanners = list(alto_score.parts[0].flatten().getElementsByClass('Spanner'))
    print(f"Alto part has {len(alto_spanners)} spanners")
    
    # Check slurs in measure 29
    print(f"\n📋 Checking measure 29 slurs in extracted Alto...")
    slurs_in_29 = 0
    
    for part in alto_score.parts:
        for measure in part.getElementsByClass('Measure'):
            if hasattr(measure, 'number') and measure.number == 29:
                notes = list(measure.flatten().notes)
                print(f"  Measure 29 notes: {[(n.pitch.name + str(n.pitch.octave)) for n in notes]}")
                
                # Check for slur notations on notes
                for note in notes:
                    if hasattr(note, 'notations') and note.notations:
                        for notation in note.notations:
                            if hasattr(notation, 'classes') and 'Slur' in notation.classes:
                                print(f"  ✅ Note {note.pitch.name}{note.pitch.octave} has slur notation")
                                slurs_in_29 += 1
    
    # Check part-level slurs
    for spanner in alto_spanners:
        if hasattr(spanner, 'classes') and 'Slur' in spanner.classes:
            try:
                spanned = spanner.getSpannedElements()
                if len(spanned) >= 2:
                    # Check if this slur affects measure 29
                    affects_29 = False
                    for element in spanned:
                        if hasattr(element, 'activeSite') and element.activeSite:
                            if hasattr(element.activeSite, 'number') and element.activeSite.number == 29:
                                affects_29 = True
                                break
                    
                    if affects_29:
                        start_pitch = spanned[0].pitch.name + str(spanned[0].pitch.octave)
                        end_pitch = spanned[-1].pitch.name + str(spanned[-1].pitch.octave)
                        print(f"  ✅ Slur affecting M29: {start_pitch} → {end_pitch}")
                        slurs_in_29 += 1
            except:
                pass
    
    print(f"\nTotal slurs affecting measure 29: {slurs_in_29}")
    
    # Test export
    print(f"\n🔄 Testing export...")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "fixed_alto.musicxml"
        alto_score.write('musicxml', fp=str(temp_path))
        
        # Check file content
        with open(temp_path, 'r') as f:
            content = f.read()
            if 'measure number="29"' in content:
                measure_29_start = content.find('measure number="29"')
                measure_29_end = content.find('</measure>', measure_29_start) + 10
                measure_29_content = content[measure_29_start:measure_29_end]
                
                slur_count = measure_29_content.count('<slur')
                print(f"  Slur tags in exported measure 29: {slur_count}")
                
                if slur_count > 0:
                    print(f"  ✅ SUCCESS! Slurs are in exported file!")
                    # Show a sample of the slur markup
                    lines = measure_29_content.split('\n')
                    for line in lines:
                        if '<slur' in line:
                            print(f"    Sample: {line.strip()}")
                            break
                else:
                    print(f"  ❌ Still no slurs in exported file")

if __name__ == "__main__":
    test_simple_slur_fix()