#!/usr/bin/env python3
"""
satb-split: A tool to split closed-score SATB MuseScore files into separate parts using music21.
"""

import argparse
import sys
from pathlib import Path

try:
    import music21
except ImportError:
    print("Error: music21 library not found. Please install with: uv add music21", file=sys.stderr)
    sys.exit(1)


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
        version='satb-split 0.2.0 (music21-based)'
    )
    
    args = parser.parse_args()
    
    # Basic validation
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    if input_path.suffix.lower() not in ['.mscz', '.musicxml']:
        print(f"Error: Input file must be a .mscz or .musicxml file, got '{input_path.suffix}'", file=sys.stderr)
        sys.exit(1)
    
    print(f"Processing: {args.input_file}")
    print(f"Using music21 version: {music21.VERSION_STR}")
    
    try:
        # Phase 0: Basic music21 parsing
        print("\n=== Phase 0: Loading score with music21 ===")
        score = music21.converter.parse(str(input_path))
        
        print(f"Score loaded successfully!")
        print(f"Score type: {type(score)}")
        
        # Get basic metadata
        metadata = score.metadata
        if metadata:
            print(f"\n=== Score Metadata ===")
            if metadata.title:
                print(f"Title: {metadata.title}")
            if metadata.composer:
                print(f"Composer: {metadata.composer}")
            if metadata.lyricist:
                print(f"Lyricist: {metadata.lyricist}")
        
        # Get basic score information
        print(f"\n=== Score Structure ===")
        print(f"Parts: {len(score.parts)}")
        
        for i, part in enumerate(score.parts):
            print(f"  Part {i+1}: {part.partName if part.partName else 'Unnamed'}")
            
            # Count voices in this part
            voices = {}
            for element in part.recurse().notes:
                voice_id = getattr(element, 'voice', 'default')
                if voice_id not in voices:
                    voices[voice_id] = 0
                voices[voice_id] += 1
            
            print(f"    Voices: {list(voices.keys())}")
            print(f"    Notes by voice: {voices}")
        
        # Count measures
        measures = list(score.parts[0].getElementsByClass('Measure'))
        print(f"Measures: {len(measures)}")
        
        print("\nPhase 0 complete: Successfully loaded and analyzed MuseScore file with music21!")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
