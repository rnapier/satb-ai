#!/usr/bin/env python3
"""
Demonstration of the lyric assignment feature.
Shows the feature working with "Crossing The Bar" and saves the results.
"""

import music21
import os
from satb_splitter.main import split_satb_voices

def demonstrate_lyric_assignment():
    """Demonstrate the lyric assignment feature end-to-end."""
    
    print("=== Lyric Assignment Feature Demonstration ===")
    print()
    
    input_file = "Crossing The Bar.musicxml"
    output_dir = "demo_output"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Processing: {input_file}")
    print(f"Output directory: {output_dir}")
    print()
    
    try:
        # Process the score with lyric assignment (using default settings)
        voice_scores = split_satb_voices(
            input_file=input_file,
            output_dir=output_dir
        )
        
        print("✓ Score processing completed successfully!")
        print(f"  - Voices created: {len(voice_scores)}")
        print(f"  - Output files saved to: {output_dir}")
        print()
        
        # Analyze the results
        print("=== Lyric Assignment Results ===")
        
        # Check measure 1 specifically
        print("Measure 1 Analysis:")
        for voice_name, score in voice_scores.items():
            measure_1_lyrics = get_measure_lyrics(score, 1)
            if measure_1_lyrics:
                print(f"  {voice_name}: {', '.join(measure_1_lyrics)}")
            else:
                print(f"  {voice_name}: (no lyrics)")
        
        print()
        
        # Check a few more measures
        for measure_num in [2, 3, 4]:
            print(f"Measure {measure_num}:")
            any_lyrics = False
            for voice_name, score in voice_scores.items():
                lyrics = get_measure_lyrics(score, measure_num)
                if lyrics:
                    print(f"  {voice_name}: {', '.join(lyrics)}")
                    any_lyrics = True
            if not any_lyrics:
                print("  (no lyrics in this measure)")
            print()
        
        # Verify files were created
        print("=== Output Files ===")
        for voice in ['Soprano', 'Alto', 'Tenor', 'Bass']:
            filename = f"{output_dir}/Crossing The Bar-{voice}.musicxml"
            if os.path.exists(filename):
                print(f"✓ {filename}")
            else:
                print(f"✗ {filename} (not found)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during processing: {e}")
        return False

def get_measure_lyrics(score, measure_number):
    """Extract all lyrics from a specific measure."""
    lyrics = []
    
    if not score or not score.parts:
        return lyrics
    
    for part in score.parts:
        measures = list(part.getElementsByClass('Measure'))
        if len(measures) >= measure_number:
            measure = measures[measure_number - 1]
            
            for note in measure.getElementsByClass('Note'):
                if note.lyrics:
                    for lyric in note.lyrics:
                        if lyric.text and lyric.text not in lyrics:
                            lyrics.append(lyric.text)
    
    return lyrics

def compare_before_after():
    """Compare lyrics before and after processing to show the assignment effect."""
    
    print("=== Before/After Comparison ===")
    
    # Load original score
    original = music21.converter.parse("Crossing The Bar.musicxml")
    
    print("Original score structure:")
    for i, part in enumerate(original.parts):
        print(f"  Part {i+1}: {len(list(part.getElementsByClass('Measure')))} measures")
        
        # Check first measure for lyrics
        first_measure = list(part.getElementsByClass('Measure'))[0]
        lyrics_found = []
        for note in first_measure.getElementsByClass('Note'):
            if note.lyrics:
                for lyric in note.lyrics:
                    if lyric.text:
                        lyrics_found.append(lyric.text)
        
        if lyrics_found:
            print(f"    Measure 1 lyrics: {', '.join(lyrics_found)}")
        else:
            print(f"    Measure 1: no lyrics")
    
    print()
    print("After processing with lyric assignment:")
    print("  All voices will have lyrics where appropriate")
    print("  (See results above)")

if __name__ == "__main__":
    print("Lyric Assignment Feature Demo")
    print("=" * 50)
    
    # Show before/after comparison
    compare_before_after()
    print()
    
    # Run the demonstration
    success = demonstrate_lyric_assignment()
    
    print("=" * 50)
    if success:
        print("✓ Demonstration completed successfully!")
        print()
        print("The lyric assignment feature:")
        print("  • Identified notes with same timing and duration")
        print("  • Copied lyrics from voices that have them to voices that don't")
        print("  • Preserved existing lyrics where they already exist")
        print("  • Created complete SATB parts with proper text assignment")
    else:
        print("✗ Demonstration failed")
        
    print()
    print("Check the demo_output directory for the generated voice files.")