"""
SATB Voice Splitter - Main entry point for splitting closed-score SATB files into individual voice parts.
"""

import sys
from pathlib import Path

from .voice_splitter import split_satb_voices


def save_voice_parts(voices_dict, output_dir, original_filename):
    """Save split voice parts as separate MusicXML files."""
    try:
        import music21
    except ImportError:
        print("Error: music21 library not found. Please install with: uv add music21", file=sys.stderr)
        sys.exit(1)
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print(f"\n=== Saving Voice Parts to {output_dir} ===")
    base_name = Path(original_filename).stem
    
    for voice_name, voice_score in voices_dict.items():
        # Create output filename
        filename = f"{base_name}-{voice_name}.musicxml"
        filepath = output_path / filename
        
        # Set part title within the score
        if voice_score.parts:
            voice_score.parts[0].partName = f"{base_name} ({voice_name})"
        
        # Update the score's title metadata with proper format: "<original> (<Part>)"
        # Ensure metadata exists
        if not voice_score.metadata:
            voice_score.metadata = music21.metadata.Metadata()
        
        # Set title to override any temporary filenames from .mscz conversion
        new_title = f"{base_name} ({voice_name})"
        voice_score.metadata.title = new_title
        
        # Clear movementName if it contains temporary filename
        if hasattr(voice_score.metadata, 'movementName') and voice_score.metadata.movementName:
            # Check if movementName looks like a temporary file
            movement_name = str(voice_score.metadata.movementName)
            if movement_name.startswith('tmp') and movement_name.endswith('.musicxml'):
                voice_score.metadata.movementName = None
        
        # Also set score-level title if it exists
        if hasattr(voice_score, 'title'):
            voice_score.title = new_title
        
        # Write to file (voice_score is already a complete Score object)
        voice_score.write('musicxml', fp=str(filepath))
        print(f"  {voice_name}: {filepath}")
    
    print("Voice separation complete!")


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
    
    # Split the voices
    try:
        voices = split_satb_voices(input_file)
        
        # Create output directory
        output_dir = f"{input_path.stem}_voices"
        
        # Save the voice parts
        save_voice_parts(voices, output_dir, input_path.name)
        
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
