"""
Main entry point for SATB voice splitting with copy-and-remove architecture.
"""

import sys
from pathlib import Path
from typing import Dict, Optional
import music21
from .utils import save_voice_scores
from .score_processor import ScoreProcessor
from .converter import convert_mscz_to_musicxml, check_mscore_available
from .exceptions import ProcessingError, InvalidScoreError


def split_satb_voices(input_file: str,
                     output_dir: Optional[str] = None) -> Dict[str, music21.stream.Score]:
    """
    Split SATB score into individual voice parts using copy-and-remove approach.
    
    Args:
        input_file: Path to input .mscz or .musicxml file
        output_dir: Directory for output files (optional)
        
    Returns:
        Dictionary mapping voice names to Score objects
        
    Raises:
        InvalidScoreError: If input score is not valid SATB
        ProcessingError: If processing fails
    """
    
    # Handle file conversion if needed
    working_file = input_file
    if input_file.lower().endswith('.mscz'):
        # Convert .mscz to .musicxml
        working_file = convert_mscz_to_musicxml(input_file)
    
    # Process the score
    processor = ScoreProcessor()
    result = processor.process_satb_score(working_file)
    
    if not result.success:
        error_msg = "Processing failed"
        if result.errors:
            error_msg += f": {result.errors[0]}"
        raise ProcessingError(error_msg)
    
    # Save output files if output directory is specified
    if output_dir:
        input_path = Path(input_file)
        base_name = input_path.stem
        save_voice_scores(result.voice_scores, output_dir, base_name)
    
    return result.voice_scores


def main():
    """Main entry point for the satb-split command."""
    if len(sys.argv) != 2:
        print("Usage: satb-split <input_file>")
        print("  Supported formats: .mscz, .musicxml")
        sys.exit(1)
    
    input_file = sys.argv[1]
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    # Check if MuseScore is available for .mscz files
    if input_file.lower().endswith('.mscz'):
        if not check_mscore_available():
            print("Error: MuseScore command line tool not found.")
            print("Please install MuseScore and ensure 'mscore' or 'musescore' is in your PATH.")
            sys.exit(1)
    
    # Split the voices
    try:
        print(f"Processing {input_file} with copy-and-remove architecture...")
        
        voices = split_satb_voices(input_file)
        
        # Create output directory
        output_dir = f"{input_path.stem}_voices"
        
        # Save the voice parts
        save_voice_scores(voices, output_dir, input_path.stem)
        
        print(f"\nProcessing completed successfully!")
        print(f"Voice parts saved to: {output_dir}/")
        
    except Exception as e:
        print(f"Error processing file: {e}")
        if hasattr(e, '__cause__') and e.__cause__:
            print(f"Caused by: {e.__cause__}")
        sys.exit(1)


if __name__ == "__main__":
    main()