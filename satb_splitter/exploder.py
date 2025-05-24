"""
MSCZ file parsing and voice separation functionality.
"""

import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional

import ms3


class MSCZParser:
    """Parser for MuseScore .mscz files using ms3 library."""
    
    def __init__(self, input_file: Path):
        """Initialize parser with input file path."""
        self.input_file = input_file
        self.score: Optional[ms3.Score] = None
        self.temp_dir: Optional[Path] = None
    
    def validate_file(self) -> bool:
        """Validate that the input file is a valid .mscz file."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"File not found: {self.input_file}")
        
        if not self.input_file.suffix.lower() == '.mscz':
            raise ValueError(f"Expected .mscz file, got {self.input_file.suffix}")
        
        # Check if it's a valid ZIP file (mscz files are ZIP archives)
        try:
            with zipfile.ZipFile(self.input_file, 'r') as zf:
                # Check for typical MuseScore files
                files = zf.namelist()
                if not any(f.endswith('.mscx') for f in files):
                    raise ValueError("No .mscx file found in archive - not a valid MuseScore file")
            return True
        except zipfile.BadZipFile:
            raise ValueError("Invalid ZIP archive - not a valid .mscz file")
    
    def parse_score(self) -> Dict[str, Any]:
        """Parse the MSCZ file and extract score information."""
        self.validate_file()
        
        print(f"Parsing MuseScore file: {self.input_file}")
        
        try:
            # Load the score using ms3
            self.score = ms3.Score(self.input_file)
            
            # Extract basic score information
            score_info = {
                'title': getattr(self.score, 'title', 'Unknown Title'),
                'composer': getattr(self.score, 'composer', 'Unknown Composer'),
                'filename': self.input_file.name,
                'path': str(self.input_file),
            }
            
            # Get basic score statistics
            if hasattr(self.score, 'mscx'):
                mscx = self.score.mscx
                if hasattr(mscx, 'get_measures'):
                    measures = mscx.get_measures()
                    score_info['measures'] = len(measures) if measures is not None else 0
                
                # Try to get parts information
                if hasattr(mscx, 'get_parts'):
                    parts = mscx.get_parts()
                    if parts is not None:
                        score_info['parts'] = len(parts)
                        score_info['part_names'] = [getattr(part, 'name', f'Part {i+1}') 
                                                   for i, part in enumerate(parts)]
            
            return score_info
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse MuseScore file: {e}")
    
    def get_score_metadata(self) -> Dict[str, Any]:
        """Get detailed metadata from the parsed score."""
        if not self.score:
            raise RuntimeError("Score not parsed yet. Call parse_score() first.")
        
        metadata = {}
        
        # Basic metadata
        for attr in ['title', 'composer', 'lyricist', 'copyright', 'creation_date']:
            if hasattr(self.score, attr):
                value = getattr(self.score, attr)
                if value:
                    metadata[attr] = value
        
        # Score structure information
        if hasattr(self.score, 'mscx'):
            mscx = self.score.mscx
            
            # Get time signatures, key signatures, etc.
            if hasattr(mscx, 'get_time_signatures'):
                ts = mscx.get_time_signatures()
                if ts is not None and not ts.empty:
                    metadata['time_signatures'] = ts.to_dict('records')
            
            if hasattr(mscx, 'get_key_signatures'):
                ks = mscx.get_key_signatures()
                if ks is not None and not ks.empty:
                    metadata['key_signatures'] = ks.to_dict('records')
        
        return metadata
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)
