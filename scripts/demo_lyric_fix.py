#!/usr/bin/env python3
"""
Demo script showing the lyric distribution fix for measure 29.

This script demonstrates how the new time-window matching algorithm
fixes the issue where "far" lyrics were dropped from other voices
due to different note durations.
"""

import tempfile
from pathlib import Path
from music21 import converter
from satb_splitter.main import split_satb_voices


def demo_measure_29_fix():
    """Demonstrate the measure 29 'far' lyric fix."""
    print("=== Measure 29 Lyric Distribution Fix Demo ===\n")
    
    score_path = Path("Crossing The Bar.musicxml")
    if not score_path.exists():
        print("❌ Sample score file not found")
        return
    
    print("🎵 Processing 'Crossing The Bar' with new lyric distribution algorithm...")
    
    # Process the score
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        voices = split_satb_voices(str(score_path), str(temp_path))
        
        print(f"✅ Successfully processed into {len(voices)} voices\n")
        
        # Analyze measure 29 specifically
        print("📊 MEASURE 29 ANALYSIS:")
        print("======================")
        
        for voice_name in ['Soprano', 'Alto', 'Tenor', 'Bass']:
            if voice_name in voices:
                voice_score = voices[voice_name]
                
                # Find measure 29 and extract lyrics with timing info
                measure_29_lyrics = []
                for part in voice_score.parts:
                    for measure in part.getElementsByClass('Measure'):
                        if hasattr(measure, 'number') and measure.number == 29:
                            for note in measure.flatten().notes:
                                if hasattr(note, 'lyrics') and note.lyrics:
                                    for lyric in note.lyrics:
                                        text = lyric.text if hasattr(lyric, 'text') else str(lyric)
                                        if text.strip():  # Only non-empty lyrics
                                            measure_29_lyrics.append({
                                                'text': text,
                                                'offset': note.offset,
                                                'duration': note.duration.quarterLength
                                            })
                
                print(f"\n{voice_name}:")
                if measure_29_lyrics:
                    for lyric_info in measure_29_lyrics:
                        duration_desc = get_duration_description(lyric_info['duration'])
                        print(f"  • '{lyric_info['text']}' at beat {lyric_info['offset'] + 1} ({duration_desc})")
                else:
                    print("  • No lyrics found")
        
        # Check if the fix worked
        print("\n" + "="*50)
        print("🎯 FIX VALIDATION:")
        
        voices_with_far = []
        for voice_name in ['Soprano', 'Alto', 'Tenor', 'Bass']:
            if voice_name in voices:
                voice_score = voices[voice_name]
                for part in voice_score.parts:
                    for measure in part.getElementsByClass('Measure'):
                        if hasattr(measure, 'number') and measure.number == 29:
                            for note in measure.flatten().notes:
                                if hasattr(note, 'lyrics') and note.lyrics:
                                    for lyric in note.lyrics:
                                        text = lyric.text if hasattr(lyric, 'text') else str(lyric)
                                        if 'far' in text.lower():
                                            voices_with_far.append(voice_name)
                                            break
        
        if len(voices_with_far) > 1:
            print(f"✅ SUCCESS: 'far' lyric found in {len(voices_with_far)} voices: {', '.join(voices_with_far)}")
            print("   The time-window matching algorithm successfully distributed the lyric!")
        else:
            print(f"❌ ISSUE: 'far' lyric only found in: {voices_with_far}")
        
        print("\n" + "="*50)
        print("📋 ALGORITHM DETAILS:")
        print("• Uses time-window matching instead of exact duration matching")
        print("• Finds notes that START during the source note's duration")
        print("• Respects slurs (only places lyrics on slur starts)")
        print("• Uses deterministic precedence: longest duration → earliest timing")
        print("• Maintains musical phrasing and readability")


def get_duration_description(quarter_length):
    """Convert quarter length to readable duration description."""
    if quarter_length >= 4.0:
        return "whole note"
    elif quarter_length >= 3.0:
        return "dotted half note"
    elif quarter_length >= 2.0:
        return "half note"
    elif quarter_length >= 1.5:
        return "dotted quarter note"
    elif quarter_length >= 1.0:
        return "quarter note"
    elif quarter_length >= 0.75:
        return "dotted eighth note"
    elif quarter_length >= 0.5:
        return "eighth note"
    elif quarter_length >= 0.25:
        return "sixteenth note"
    else:
        return f"{quarter_length} quarter note"


if __name__ == "__main__":
    demo_measure_29_fix()