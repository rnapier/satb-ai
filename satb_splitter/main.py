#!/usr/bin/env python3
"""
satb-split: A tool to split closed-score SATB MuseScore files into separate parts.
"""

import argparse
import sys
from pathlib import Path


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
    print("satb-split is ready! (Phase 0 complete)")


if __name__ == '__main__':
    main()
