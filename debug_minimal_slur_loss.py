#!/usr/bin/env python3
"""
Minimal reproduction to identify exactly where slurs are lost during voice separation.
"""

import music21
import copy
import tempfile
from pathlib import Path

def check_slurs_in_measure_29(score, label):
    """Check for slurs in measure 29 and print details."""
    print(f"\n📋 {label}")
    slurs_found = []
    
    for part_idx, part in enumerate(score.parts):
        print(f"  Part {part_idx}:")
        
        # Check for all spanners in this part
        all_spanners = part.getElementsByClass('Spanner')
        print(f"    Total spanners in part: {len(all_spanners)}")
        
        for measure in part.getElementsByClass('Measure'):
            if hasattr(measure, 'number') and measure.number == 29:
                print(f"    Measure 29 found:")
                
                # Check notes for slur notations
                notes = list(measure.flatten().notes)
                print(f"      Notes in measure: {len(notes)}")
                
                for note in notes:
                    voice = getattr(note, 'voice', 'no-voice')
                    print(f"      Note {note.pitch.name}{note.pitch.octave} (voice {voice})")
                    
                    if hasattr(note, 'notations') and note.notations:
                        for notation in note.notations:
                            if hasattr(notation, 'classes') and 'Slur' in notation.classes:
                                slur_info = f"{note.pitch.name}{note.pitch.octave} voice {voice} has slur {notation.type}"
                                print(f"        ✅ {slur_info}")
                                slurs_found.append(slur_info)
                
                # Check for standalone slurs in this measure
                for element in measure.flatten():
                    if hasattr(element, 'classes') and 'Slur' in element.classes:
                        try:
                            spanned = element.getSpannedElements()
                            if len(spanned) >= 2:
                                start_pitch = spanned[0].pitch.name + str(spanned[0].pitch.octave)
                                end_pitch = spanned[-1].pitch.name + str(spanned[-1].pitch.octave)
                                slur_info = f"Standalone slur: {start_pitch} → {end_pitch}"
                                print(f"        ✅ {slur_info}")
                                slurs_found.append(slur_info)
                        except Exception as e:
                            slur_info = f"Standalone slur (broken references): {e}"
                            print(f"        ❌ {slur_info}")
                            slurs_found.append(slur_info)
        
        # Also check for spanners that cross measure 29
        for spanner in all_spanners:
            if hasattr(spanner, 'classes') and 'Slur' in spanner.classes:
                try:
                    spanned = spanner.getSpannedElements()
                    if len(spanned) >= 2:
                        # Check if any spanned element is in measure 29
                        in_measure_29 = False
                        for element in spanned:
                            if hasattr(element, 'measureNumber') and element.measureNumber == 29:
                                in_measure_29 = True
                                break
                            # Alternative check using activeSite
                            if hasattr(element, 'activeSite') and element.activeSite:
                                if hasattr(element.activeSite, 'number') and element.activeSite.number == 29:
                                    in_measure_29 = True
                                    break
                        
                        if in_measure_29:
                            start_pitch = spanned[0].pitch.name + str(spanned[0].pitch.octave)
                            end_pitch = spanned[-1].pitch.name + str(spanned[-1].pitch.octave)
                            slur_info = f"Part slur crossing M29: {start_pitch} → {end_pitch}"
                            print(f"    ✅ {slur_info}")
                            slurs_found.append(slur_info)
                except Exception as e:
                    slur_info = f"Part slur (broken): {e}"
                    print(f"    ❌ {slur_info}")
                    slurs_found.append(slur_info)
    
    print(f"  Total slurs found: {len(slurs_found)}")
    return slurs_found

def test_basic_music21_operations():
    """Test basic music21 operations to see where slurs are lost."""
    print("🔬 MINIMAL REPRODUCTION: Slur Loss During Voice Separation")
    print("=" * 70)
    
    # Step 1: Load original score
    print("\n🔄 Step 1: Loading original score...")
    original_score = music21.converter.parse("Crossing The Bar.musicxml")
    original_slurs = check_slurs_in_measure_29(original_score, "Original Score")
    
    # Step 2: Deep copy
    print("\n🔄 Step 2: Creating deep copy...")
    deep_copied_score = copy.deepcopy(original_score)
    deep_copy_slurs = check_slurs_in_measure_29(deep_copied_score, "Deep Copied Score")
    
    # Step 3: Extract Alto voice (voice 2) manually
    print("\n🔄 Step 3: Extracting Alto voice manually...")
    alto_score = music21.stream.Score()
    
    for part in original_score.parts:
        # Find Alto voice in original part
        alto_notes = []
        for measure in part.getElementsByClass('Measure'):
            measure_copy = music21.stream.Measure(number=measure.number)
            
            for element in measure.flatten():
                # Keep elements from voice 2 (Alto) or non-voice elements
                if hasattr(element, 'voice'):
                    if element.voice == '2':  # Alto voice
                        alto_notes.append(element)
                        measure_copy.append(element)
                elif not hasattr(element, 'voice'):
                    # Keep non-voice elements (like directions, etc.)
                    measure_copy.append(element)
            
            if len(measure_copy) > 0:
                if not alto_score.parts:
                    alto_part = music21.stream.Part()
                    alto_score.append(alto_part)
                alto_score.parts[0].append(measure_copy)
    
    alto_slurs = check_slurs_in_measure_29(alto_score, "Manually Extracted Alto")
    
    # Step 4: Test export
    print("\n🔄 Step 4: Testing export...")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "test_alto.musicxml"
        alto_score.write('musicxml', fp=str(temp_path))
        
        # Re-load exported file
        exported_alto = music21.converter.parse(str(temp_path))
        exported_slurs = check_slurs_in_measure_29(exported_alto, "Exported & Reloaded Alto")
        
        # Check actual file content
        print(f"\n📄 Checking actual file content...")
        with open(temp_path, 'r') as f:
            content = f.read()
            if 'measure number="29"' in content:
                measure_29_start = content.find('measure number="29"')
                measure_29_end = content.find('</measure>', measure_29_start) + 10
                measure_29_content = content[measure_29_start:measure_29_end]
                
                print(f"  Measure 29 content length: {len(measure_29_content)} chars")
                slur_count = measure_29_content.count('<slur')
                print(f"  Slur tags in exported measure 29: {slur_count}")
                
                if slur_count > 0:
                    print(f"  ✅ Slurs ARE in exported file!")
                else:
                    print(f"  ❌ NO slurs in exported file!")
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"  Original: {len(original_slurs)} slurs")
    print(f"  Deep Copy: {len(deep_copy_slurs)} slurs")
    print(f"  Manual Alto: {len(alto_slurs)} slurs")
    print(f"  Exported Alto: {len(exported_slurs)} slurs")

if __name__ == "__main__":
    test_basic_music21_operations()