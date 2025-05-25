#!/usr/bin/env python3
"""
Diagnostic script to investigate syllabic marking issues in SATB voice splitting.
"""

import music21
import sys
from pathlib import Path

def analyze_syllabic_in_original(file_path):
    """Analyze syllabic information in the original MusicXML file."""
    print("=== Analyzing Syllabic Information in Original File ===")
    
    score = music21.converter.parse(str(file_path))
    
    syllabic_notes = []
    
    for part_idx, part in enumerate(score.parts):
        print(f"\nPart {part_idx + 1}: {part.partName}")
        
        for measure_idx, measure in enumerate(part.getElementsByClass(music21.stream.Measure)):
            # Check both measure-level notes and voice-level notes
            all_notes = list(measure.getElementsByClass(music21.note.Note))
            
            # Also check notes in voices
            for voice in measure.getElementsByClass(music21.stream.Voice):
                all_notes.extend(list(voice.getElementsByClass(music21.note.Note)))
            
            for note in all_notes:
                if hasattr(note, 'lyrics') and note.lyrics:
                    for lyric in note.lyrics:
                        syllabic_info = {
                            'part_idx': part_idx,
                            'part_name': part.partName,
                            'measure': measure_idx + 1,
                            'offset': note.offset,
                            'text': lyric.text if hasattr(lyric, 'text') else str(lyric),
                            'syllabic': lyric.syllabic if hasattr(lyric, 'syllabic') else 'unknown',
                            'note_object': note,
                            'lyric_object': lyric
                        }
                        syllabic_notes.append(syllabic_info)
                        
                        print(f"  Measure {measure_idx + 1}, offset {note.offset}: '{syllabic_info['text']}' - syllabic: {syllabic_info['syllabic']}")
                
                # Also check the simple lyric property
                elif hasattr(note, 'lyric') and note.lyric:
                    print(f"  Measure {measure_idx + 1}, offset {note.offset}: '{note.lyric}' - syllabic: SIMPLE_LYRIC_PROPERTY")
    
    print(f"\nTotal notes with syllabic information: {len(syllabic_notes)}")
    return syllabic_notes

def analyze_syllabic_after_splitting(voices_dict):
    """Analyze syllabic information after voice splitting."""
    print("\n=== Analyzing Syllabic Information After Voice Splitting ===")
    
    for voice_name, voice_score in voices_dict.items():
        print(f"\n{voice_name}:")
        part = voice_score.parts[0]
        
        syllabic_count = 0
        
        for measure_idx, measure in enumerate(part.getElementsByClass(music21.stream.Measure)):
            for note in measure.getElementsByClass(music21.note.Note):
                if hasattr(note, 'lyrics') and note.lyrics:
                    for lyric in note.lyrics:
                        syllabic_count += 1
                        syllabic = lyric.syllabic if hasattr(lyric, 'syllabic') else 'unknown'
                        text = lyric.text if hasattr(lyric, 'text') else str(lyric)
                        print(f"  Measure {measure_idx + 1}, offset {note.offset}: '{text}' - syllabic: {syllabic}")
                
                elif hasattr(note, 'lyric') and note.lyric:
                    syllabic_count += 1
                    print(f"  Measure {measure_idx + 1}, offset {note.offset}: '{note.lyric}' - syllabic: SIMPLE_LYRIC_PROPERTY")
        
        print(f"  Total syllabic notes in {voice_name}: {syllabic_count}")

def test_music21_lyric_structure():
    """Test how music21 handles lyric and syllabic information."""
    print("\n=== Testing Music21 Lyric Structure ===")
    
    # Create a test note with lyrics
    note = music21.note.Note('C4')
    
    # Test different ways of adding lyrics
    print("Testing lyric assignment methods:")
    
    # Method 1: Simple lyric property
    note.lyric = "test"
    print(f"1. note.lyric = 'test' -> lyric: {note.lyric}")
    print(f"   hasattr(note, 'lyrics'): {hasattr(note, 'lyrics')}")
    if hasattr(note, 'lyrics'):
        print(f"   note.lyrics: {note.lyrics}")
    
    # Method 2: Adding lyric object
    lyric_obj = music21.note.Lyric(text="begin-test", syllabic="begin")
    note.lyrics.append(lyric_obj)
    print(f"2. Added Lyric object with syllabic='begin'")
    print(f"   note.lyrics: {note.lyrics}")
    for i, lyric in enumerate(note.lyrics):
        print(f"   lyrics[{i}]: text='{lyric.text}', syllabic='{lyric.syllabic}'")

def main():
    """Main diagnostic function."""
    file_path = "Crossing The Bar.musicxml"
    
    if not Path(file_path).exists():
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    
    # Test music21 lyric structure first
    test_music21_lyric_structure()
    
    # Analyze original file
    original_syllabics = analyze_syllabic_in_original(file_path)
    
    # Run voice splitting
    print("\n=== Running Voice Splitting ===")
    sys.path.append('.')
    from satb_splitter.voice_splitter import split_satb_voices
    
    try:
        voices_dict = split_satb_voices(file_path)
        
        # Analyze after splitting
        analyze_syllabic_after_splitting(voices_dict)
        
        # Compare results
        print("\n=== Comparison Summary ===")
        print(f"Original file had {len(original_syllabics)} notes with syllabic information")
        
        # Count syllabics in split voices
        total_split_syllabics = 0
        for voice_name, voice_score in voices_dict.items():
            part = voice_score.parts[0]
            for measure in part.getElementsByClass(music21.stream.Measure):
                for note in measure.getElementsByClass(music21.note.Note):
                    if (hasattr(note, 'lyrics') and note.lyrics) or (hasattr(note, 'lyric') and note.lyric):
                        total_split_syllabics += 1
        
        print(f"Split voices have {total_split_syllabics} notes with lyric information")
        
        if len(original_syllabics) > 0:
            # Show examples of syllabic types in original
            syllabic_types = {}
            for syl in original_syllabics:
                syl_type = syl['syllabic']
                if syl_type not in syllabic_types:
                    syllabic_types[syl_type] = []
                syllabic_types[syl_type].append(syl)
            
            print(f"\nSyllabic types found in original:")
            for syl_type, examples in syllabic_types.items():
                print(f"  {syl_type}: {len(examples)} examples")
                if examples:
                    example = examples[0]
                    print(f"    Example: '{example['text']}' in measure {example['measure']}")
        
    except Exception as e:
        print(f"Error during voice splitting: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()