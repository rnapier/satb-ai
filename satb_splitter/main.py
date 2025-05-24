#!/usr/bin/env python3
"""
satb-split: A tool to split closed-score SATB MuseScore files into separate parts.
"""

import argparse
import sys
from pathlib import Path

from .exploder import MSCZParser


def main():
    """Main entry point for the satb-split command."""
    parser = argparse.ArgumentParser(
        prog='satb-split',
        description='Split a closed-score SATB MuseScore file into separate parts with audio exports'
    )
    
    parser.add_argument(
        'input_file',
        help='Input MuseScore (.mscz) file with closed-score SATB layout'
    )
    
    # Basic version info
    parser.add_argument(
        '--version',
        action='version',
        version='satb-split 0.1.0'
    )
    
    args = parser.parse_args()
    
    # Basic validation
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    if not input_path.suffix.lower() == '.mscz':
        print(f"Error: Input file must be a .mscz file, got '{input_path.suffix}'", file=sys.stderr)
        sys.exit(1)
    
    print(f"Processing: {args.input_file}")
    
    try:
        # Phase 1: Parse the MSCZ file
        parser = MSCZParser(input_path)
        score_info = parser.parse_score()
        
        print("\n=== Score Information ===")
        print(f"Title: {score_info.get('title', 'Unknown')}")
        print(f"Composer: {score_info.get('composer', 'Unknown')}")
        print(f"Filename: {score_info['filename']}")
        if 'measures' in score_info:
            print(f"Measures: {score_info['measures']}")
        if 'parts' in score_info:
            print(f"Parts: {score_info['parts']}")
            if 'part_names' in score_info:
                print(f"Part names: {', '.join(score_info['part_names'])}")
        
        # Get additional metadata
        try:
            metadata = parser.get_score_metadata()
            if metadata:
                print("\n=== Additional Metadata ===")
                for key, value in metadata.items():
                    if key not in ['time_signatures', 'key_signatures']:
                        print(f"{key.replace('_', ' ').title()}: {value}")
        except Exception as e:
            print(f"Note: Could not retrieve extended metadata: {e}")
        
        print("\nPhase 1 complete: Successfully parsed MuseScore file!")
        
        # Phase 2: Extract SATB voice data
        try:
            voices = parser.extract_satb_voices()
            
            print("\n=== SATB Voice Data ===")
            for voice_name, voice_data in voices.items():
                notes = voice_data['notes']
                dynamics = voice_data['dynamics'] 
                lyrics = voice_data['lyrics']
                
                print(f"\n{voice_name.upper()}:")
                print(f"  Notes: {len(notes)}")
                if notes:
                    print(f"    First note: measure {notes[0].get('measure', '?')}, "
                          f"pitch {notes[0].get('pitch', '?')}, "
                          f"duration {notes[0].get('duration', '?')}")
                
                print(f"  Dynamics: {len(dynamics)}")
                if dynamics:
                    first_dynamic = dynamics[0]
                    print(f"    First dynamic: measure {first_dynamic.get('measure', '?')}, "
                          f"marking '{first_dynamic.get('marking', '?')}'")
                
                print(f"  Lyrics: {len(lyrics)}")
                if lyrics:
                    first_lyric = lyrics[0]
                    print(f"    First lyric: measure {first_lyric.get('measure', '?')}, "
                          f"text '{first_lyric.get('text', '?')}'")
            
            print("\nPhase 2 complete: Successfully extracted SATB voice data!")
            
        except Exception as e:
            print(f"Warning: Could not extract voice data: {e}")
        
        # Cleanup
        parser.cleanup()
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
