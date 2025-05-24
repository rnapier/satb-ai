"""
MuseScore file conversion utilities for satb-split.
"""

import subprocess
import tempfile
from pathlib import Path


def check_mscore_available():
    """Check if MuseScore command line tool is available."""
    try:
        result = subprocess.run(['mscore', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Try alternative command names
        for cmd in ['mscore3', 'musescore', 'musescore3']:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return cmd
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        return False


def convert_mscz_to_musicxml(mscz_path):
    """Convert .mscz file to .musicxml using MuseScore command line tool.
    
    Args:
        mscz_path: Path to the .mscz file
        
    Returns:
        Path to the converted .musicxml file
    """
    mscore_cmd = check_mscore_available()
    if not mscore_cmd:
        raise RuntimeError("MuseScore command line tool not found. Please install MuseScore to process .mscz files.")
    
    print(f"Converting {mscz_path} to MusicXML using MuseScore...")
    
    # Create temporary file for the conversion
    with tempfile.NamedTemporaryFile(suffix='.musicxml', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Convert using MuseScore command line
        if mscore_cmd == True:
            mscore_cmd = 'mscore'
            
        cmd = [mscore_cmd, str(mscz_path), '-o', temp_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise RuntimeError(f"MuseScore conversion failed: {result.stderr}")
        
        print(f"Conversion successful: {temp_path}")
        return Path(temp_path)
        
    except subprocess.TimeoutExpired:
        # Clean up on timeout
        Path(temp_path).unlink(missing_ok=True)
        raise RuntimeError("MuseScore conversion timed out")
    except Exception as e:
        # Clean up on error
        Path(temp_path).unlink(missing_ok=True)
        raise
