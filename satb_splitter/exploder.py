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
            
            # Get basic score statistics using documented ms3 API
            try:
                # Try to get measures count from notes data
                notes_df = self.score.mscx.notes()
                if notes_df is not None and not notes_df.empty:
                    max_measure = notes_df['mc'].max() if 'mc' in notes_df.columns else None
                    if max_measure is not None:
                        score_info['measures'] = int(max_measure)
            except Exception:
                # If we can't get measure count, that's okay
                pass
            
            return score_info
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse MuseScore file: {e}")
    
    def get_score_metadata(self) -> Dict[str, Any]:
        """Get detailed metadata from the parsed score."""
        if not self.score:
            raise RuntimeError("Score not parsed yet. Call parse_score() first.")
        
        metadata = {}
        
        # Get metadata using the documented API
        try:
            score_metadata = self.score.mscx.metadata
            for key, value in score_metadata.items():
                if value:
                    metadata[key] = value
        except Exception:
            # If metadata access fails, continue without it
            pass
        
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
            
            # Extract dynamics and lyrics from events data
            events_df = mscx.events()
            if events_df is not None and not events_df.empty:
                self._extract_dynamics_from_events(events_df, voices)
                self._extract_lyrics_from_events(events_df, voices)
            
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
    
    def _extract_dynamics_from_events(self, events_df, voices: Dict[str, Dict[str, Any]]):
        """Extract dynamics from events data and assign to SATB voices."""
        # Filter for dynamics events
        dynamics_events = events_df[events_df['type'] == 'Dynamic'] if 'type' in events_df.columns else events_df
        
        for _, event in dynamics_events.iterrows():
            staff = event.get('staff')
            voice = event.get('voice')
            
            voice_name = self._map_staff_voice_to_part(staff, voice)
            if voice_name:
                dynamic_data = {
                    'measure': event.get('mc'),
                    'beat': event.get('mc_onset'),
                    'marking': event.get('text'),
                    'staff': staff,
                    'voice': voice
                }
                voices[voice_name]['dynamics'].append(dynamic_data)
    
    def _extract_lyrics_from_events(self, events_df, voices: Dict[str, Dict[str, Any]]):
        """Extract lyrics from events data and assign to SATB voices."""
        # Filter for lyrics events
        lyrics_events = events_df[events_df['type'] == 'Lyrics'] if 'type' in events_df.columns else events_df
        
        for _, event in lyrics_events.iterrows():
            staff = event.get('staff')
            voice = event.get('voice')
            
            voice_name = self._map_staff_voice_to_part(staff, voice)
            if voice_name:
                lyric_data = {
                    'measure': event.get('mc'),
                    'beat': event.get('mc_onset'),
                    'text': event.get('text'),
                    'verse': event.get('verse'),
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
