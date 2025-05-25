#!/usr/bin/env python3
"""
Detailed validation test to ensure voice separation is working correctly.
"""

import sys
import music21
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, '.')

from satb_splitter import split_satb_voices
from satb_splitter.utils import ProcessingOptions, load_score

def analyze_voice_separation():
    """Analyze the voice separation to ensure it's working correctly."""
    print("Detailed Voice Separation Analysis")
    print("=" * 50)
    
    test_file = "Crossing The Bar.musicxml"
    if not Path(test_file).exists():
        print(f"Test file {test_file} not found")
        return False
    
    # Load original score for comparison
    original_score = load_score(test_file)
    original_parts = len(original_score.parts)
    
    print(f"Original score has {original_parts} parts")
    
    # Analyze original score structure
    for i, part in enumerate(original_score.parts):
        notes = part.flatten().notes
        measures = part.getElementsByClass(music21.stream.Measure)
        voices = set()
        
        for measure in measures:
            for voice in measure.voices:
                voices.add(voice.id)
        
        print(f"  Part {i}: {len(notes)} notes, {len(measures)} measures, {len(voices)} voices")
    
    print()
    
    # Process with voice splitter
    options = ProcessingOptions()
    voice_scores = split_satb_voices(test_file, options=options)
    
    print("Voice separation results:")
    total_separated_notes = 0
    
    for voice_name, score in voice_scores.items():
        parts = len(score.parts)
        notes = score.flatten().notes
        measures = score.parts[0].getElementsByClass(music21.stream.Measure) if score.parts else []
        
        print(f"  {voice_name}: {len(notes)} notes, {parts} part(s), {len(measures)} measures")
        total_separated_notes += len(notes)
        
        # Verify single part
        if parts != 1:
            print(f"    ⚠️  Expected 1 part, got {parts}")
        
        # Check for reasonable note count
        if len(notes) == 0:
            print(f"    ❌ No notes found!")
        elif len(notes) < 50:
            print(f"    ⚠️  Very few notes ({len(notes)})")
        else:
            print(f"    ✅ Good note count")
    
    print()
    
    # Calculate original total notes
    original_total_notes = sum(len(part.flatten().notes) for part in original_score.parts)
    
    print(f"Original total notes: {original_total_notes}")
    print(f"Separated total notes: {total_separated_notes}")
    
    # The separated total should be equal to original (no notes lost or duplicated)
    if total_separated_notes == original_total_notes:
        print("✅ Note count matches - no notes lost or duplicated")
    else:
        print(f"⚠️  Note count mismatch - difference: {total_separated_notes - original_total_notes}")
    
    print()
    
    # Verify voice isolation by checking pitch ranges
    print("Pitch range analysis:")
    voice_ranges = {}
    
    for voice_name, score in voice_scores.items():
        notes = score.flatten().notes
        if notes:
            pitches = []
            for note in notes:
                if hasattr(note, 'pitch'):
                    pitches.append(note.pitch.ps)
                elif hasattr(note, 'pitches'):  # Chord
                    pitches.extend([p.ps for p in note.pitches])
            
            if pitches:
                min_pitch = min(pitches)
                max_pitch = max(pitches)
                avg_pitch = sum(pitches) / len(pitches)
                voice_ranges[voice_name] = {
                    'min': min_pitch,
                    'max': max_pitch,
                    'avg': avg_pitch,
                    'count': len(pitches)
                }
                
                print(f"  {voice_name}: avg={avg_pitch:.1f}, range={min_pitch:.1f}-{max_pitch:.1f}, {len(pitches)} pitches")
    
    # Verify expected voice ordering (Soprano highest, Bass lowest)
    if len(voice_ranges) == 4:
        avg_pitches = [(name, data['avg']) for name, data in voice_ranges.items()]
        avg_pitches.sort(key=lambda x: x[1], reverse=True)
        
        expected_order = ['Soprano', 'Alto', 'Tenor', 'Bass']
        actual_order = [name for name, _ in avg_pitches]
        
        print(f"\nExpected pitch order: {expected_order}")
        print(f"Actual pitch order:   {actual_order}")
        
        if actual_order == expected_order:
            print("✅ Voice pitch ranges are in correct order")
        else:
            print("⚠️  Voice pitch ranges may not be correctly separated")
    
    return True

def main():
    """Run the detailed validation."""
    try:
        analyze_voice_separation()
        print("\n🎉 Voice separation analysis complete!")
        return 0
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())