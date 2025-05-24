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
            
            # Extract basic score information using proper ms3 API
            title, composer = self._extract_metadata()
            
            score_info = {
                'title': title,
                'composer': composer,
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
    
    def extract_satb_voices(self) -> Dict[str, Dict[str, Any]]:
        """Extract notes, dynamics, and lyrics for each SATB voice."""
        if not self.score:
            raise RuntimeError("Score not parsed yet. Call parse_score() first.")
        
        print("Extracting SATB voice data...")
        
        # Initialize voice data structure
        voices = {
            'soprano': {'notes': [], 'dynamics': [], 'lyrics': []},
            'alto': {'notes': [], 'dynamics': [], 'lyrics': []},
            'tenor': {'notes': [], 'dynamics': [], 'lyrics': []},
            'bass': {'notes': [], 'dynamics': [], 'lyrics': []}
        }
        
        try:
            mscx = self.score.mscx
            
            # Extract notes data using public API
            notes_df = mscx.notes()
            if notes_df is not None and not notes_df.empty:
                self._extract_notes_by_voice(notes_df, voices)
            
            # For now, skip dynamics and lyrics until we find the correct API
            # TODO: Research correct ms3 API for dynamics and lyrics extraction
            
            # Print summary
            for voice_name, voice_data in voices.items():
                print(f"{voice_name.title()}: {len(voice_data['notes'])} notes, "
                      f"{len(voice_data['dynamics'])} dynamics, "
                      f"{len(voice_data['lyrics'])} lyrics")
            
            return voices
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract voice data: {e}")
    
    def _extract_notes_by_voice(self, notes_df, voices: Dict[str, Dict[str, Any]]):
        """Extract notes and assign to SATB voices based on staff and voice."""
        for _, note in notes_df.iterrows():
            staff = note.get('staff')
            voice = note.get('voice')
            
            # Map staff/voice to SATB parts
            voice_name = self._map_staff_voice_to_part(staff, voice)
            if voice_name:
                note_data = {
                    'measure': note.get('mc'),
                    'beat': note.get('mc_onset'),
                    'pitch': note.get('midi'),
                    'duration': note.get('duration_qb'),
                    'staff': staff,
                    'voice': voice
                }
                voices[voice_name]['notes'].append(note_data)
    
    def _extract_dynamics_by_voice(self, dynamics_df, voices: Dict[str, Dict[str, Any]]):
        """Extract dynamics and assign to SATB voices."""
        for _, dynamic in dynamics_df.iterrows():
            staff = dynamic.get('staff')
            voice = dynamic.get('voice')
            
            voice_name = self._map_staff_voice_to_part(staff, voice)
            if voice_name:
                dynamic_data = {
                    'measure': dynamic.get('mc'),
                    'beat': dynamic.get('mc_onset'),
                    'marking': dynamic.get('text'),
                    'staff': staff,
                    'voice': voice
                }
                voices[voice_name]['dynamics'].append(dynamic_data)
    
    def _extract_lyrics_by_voice(self, lyrics_df, voices: Dict[str, Dict[str, Any]]):
        """Extract lyrics and assign to SATB voices."""
        for _, lyric in lyrics_df.iterrows():
            staff = lyric.get('staff')
            voice = lyric.get('voice')
            
            voice_name = self._map_staff_voice_to_part(staff, voice)
            if voice_name:
                lyric_data = {
                    'measure': lyric.get('mc'),
                    'beat': lyric.get('mc_onset'),
                    'text': lyric.get('text'),
                    'verse': lyric.get('verse'),
                    'staff': staff,
                    'voice': voice
                }
                voices[voice_name]['lyrics'].append(lyric_data)
    
    def _map_staff_voice_to_part(self, staff: Optional[int], voice: Optional[int]) -> Optional[str]:
        """Map staff and voice numbers to SATB part names."""
        if staff is None or voice is None:
            return None
        
        # Standard SATB mapping for closed score:
        # Staff 1, Voice 1 → Soprano
        # Staff 1, Voice 2 → Alto  
        # Staff 2, Voice 1 → Tenor
        # Staff 2, Voice 2 → Bass
        mapping = {
            (1, 1): 'soprano',
            (1, 2): 'alto',
            (2, 1): 'tenor',
            (2, 2): 'bass'
        }
        
        return mapping.get((staff, voice))

    def _extract_metadata(self) -> tuple[str, str]:
        """Extract title and composer using ms3 public API."""
        metadata = self.score.mscx.metadata
        title = metadata.get('workTitle') or metadata.get('title')
        composer = metadata.get('composer')
        
        return title or 'Unknown Title', composer or 'Unknown Composer'
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)
