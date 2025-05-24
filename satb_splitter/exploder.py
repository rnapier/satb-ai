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
            
            # Extract dynamics and lyrics from chords data (as suggested in docs)
            try:
                chords_df = mscx.chords()
                if chords_df is not None and not chords_df.empty:
                    self._extract_dynamics_from_chords(chords_df, voices)
                    self._extract_lyrics_from_chords(chords_df, voices)
            except Exception as e:
                # Fallback to events data
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
    
    def unify_satb_parts(self, voices: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Unify dynamics and lyrics across SATB parts according to Phase 3 rules."""
        print("\nApplying Phase 3 unification rules...")
        
        # Create a copy to avoid modifying the original
        unified_voices = {
            voice: {
                'notes': voice_data['notes'].copy(),
                'dynamics': voice_data['dynamics'].copy(),
                'lyrics': voice_data['lyrics'].copy()
            }
            for voice, voice_data in voices.items()
        }
        
        # Phase 3 Rule 1: Unify dynamics
        self._unify_dynamics(unified_voices)
        
        # Phase 3 Rule 2: Unify lyrics 
        self._unify_lyrics(unified_voices)
        
        return unified_voices
    
    def _unify_dynamics(self, voices: Dict[str, Dict[str, Any]]):
        """Apply dynamics unification rules for closed-score SATB."""
        soprano_dynamics = voices['soprano']['dynamics']
        alto_dynamics = voices['alto']['dynamics'] 
        tenor_dynamics = voices['tenor']['dynamics']
        bass_dynamics = voices['bass']['dynamics']
        
        # Check if Soprano and Tenor have the same dynamics at the same positions
        if soprano_dynamics and tenor_dynamics:
            # Create sets of (measure, beat, marking) for comparison
            soprano_set = {(d['measure'], d['beat'], d['marking']) for d in soprano_dynamics}
            tenor_set = {(d['measure'], d['beat'], d['marking']) for d in tenor_dynamics}
            
            if soprano_set == tenor_set:
                print(f"  Dynamics unification: Soprano and Tenor have matching dynamics - applying to all parts")
                # Apply Soprano dynamics to Alto and Bass
                for dynamic in soprano_dynamics:
                    # Add to Alto (staff 1, voice 2)
                    alto_dynamic = dynamic.copy()
                    alto_dynamic['staff'] = 1
                    alto_dynamic['voice'] = 2
                    voices['alto']['dynamics'].append(alto_dynamic)
                    
                    # Add to Bass (staff 2, voice 2)  
                    bass_dynamic = dynamic.copy()
                    bass_dynamic['staff'] = 2
                    bass_dynamic['voice'] = 2
                    voices['bass']['dynamics'].append(bass_dynamic)
                return
        
        # Check if only Soprano has dynamics
        if soprano_dynamics and not alto_dynamics and not tenor_dynamics and not bass_dynamics:
            print(f"  Dynamics unification: Only Soprano has dynamics - applying to all parts")
            # Apply Soprano dynamics to all other parts
            for dynamic in soprano_dynamics:
                # Add to Alto (staff 1, voice 2)
                alto_dynamic = dynamic.copy()
                alto_dynamic['staff'] = 1
                alto_dynamic['voice'] = 2
                voices['alto']['dynamics'].append(alto_dynamic)
                
                # Add to Tenor (staff 2, voice 1)
                tenor_dynamic = dynamic.copy()
                tenor_dynamic['staff'] = 2  
                tenor_dynamic['voice'] = 1
                voices['tenor']['dynamics'].append(tenor_dynamic)
                
                # Add to Bass (staff 2, voice 2)
                bass_dynamic = dynamic.copy()
                bass_dynamic['staff'] = 2
                bass_dynamic['voice'] = 2
                voices['bass']['dynamics'].append(bass_dynamic)
            return
        
        # Check if Soprano and Bass have matching dynamics
        if soprano_dynamics and bass_dynamics:
            soprano_set = {(d['measure'], d['beat'], d['marking']) for d in soprano_dynamics}
            bass_set = {(d['measure'], d['beat'], d['marking']) for d in bass_dynamics}
            
            if soprano_set == bass_set:
                print(f"  Dynamics unification: Soprano and Bass have matching dynamics - applying to all parts")
                # Apply to Alto and Tenor
                for dynamic in soprano_dynamics:
                    # Add to Alto (staff 1, voice 2)
                    alto_dynamic = dynamic.copy()
                    alto_dynamic['staff'] = 1
                    alto_dynamic['voice'] = 2
                    voices['alto']['dynamics'].append(alto_dynamic)
                    
                    # Add to Tenor (staff 2, voice 1)
                    tenor_dynamic = dynamic.copy()
                    tenor_dynamic['staff'] = 2
                    tenor_dynamic['voice'] = 1  
                    voices['tenor']['dynamics'].append(tenor_dynamic)
                return
        
        print(f"  Dynamics unification: No unification rules apply - keeping original dynamics")
    
    def _unify_lyrics(self, voices: Dict[str, Dict[str, Any]]):
        """Apply lyrics unification rules for closed-score SATB."""
        soprano_lyrics = voices['soprano']['lyrics']
        alto_lyrics = voices['alto']['lyrics']
        tenor_lyrics = voices['tenor']['lyrics'] 
        bass_lyrics = voices['bass']['lyrics']
        
        # Count lyrics per voice
        soprano_count = len(soprano_lyrics)
        alto_count = len(alto_lyrics)
        tenor_count = len(tenor_lyrics)
        bass_count = len(bass_lyrics)
        
        print(f"  Lyrics counts: Soprano={soprano_count}, Alto={alto_count}, Tenor={tenor_count}, Bass={bass_count}")
        
        # If Soprano has significantly more lyrics than others, apply Soprano lyrics to all
        if soprano_count > 0 and soprano_count >= max(alto_count, tenor_count, bass_count) * 3:
            print(f"  Lyrics unification: Soprano has majority of lyrics - applying to all parts")
            
            # Apply Soprano lyrics to all other parts
            for lyric in soprano_lyrics:
                # Add to Alto (staff 1, voice 2)
                if alto_count == 0:  # Only if Alto has no lyrics
                    alto_lyric = lyric.copy()
                    alto_lyric['staff'] = 1
                    alto_lyric['voice'] = 2
                    voices['alto']['lyrics'].append(alto_lyric)
                
                # Add to Tenor (staff 2, voice 1)
                if tenor_count == 0:  # Only if Tenor has no lyrics
                    tenor_lyric = lyric.copy()
                    tenor_lyric['staff'] = 2
                    tenor_lyric['voice'] = 1
                    voices['tenor']['lyrics'].append(tenor_lyric)
                
                # Add to Bass (staff 2, voice 2)  
                if bass_count == 0:  # Only if Bass has no lyrics
                    bass_lyric = lyric.copy()
                    bass_lyric['staff'] = 2
                    bass_lyric['voice'] = 2
                    voices['bass']['lyrics'].append(bass_lyric)
            return
        
        print(f"  Lyrics unification: Multiple parts have lyrics - keeping original distribution")
    
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
        # Filter for events that have dynamic information
        dynamics_events = events_df[events_df['Dynamic/subtype'].notna()]
        
        for _, event in dynamics_events.iterrows():
            staff = event.get('staff')
            voice = event.get('voice')
            
            voice_name = self._map_staff_voice_to_part(staff, voice)
            if voice_name:
                dynamic_data = {
                    'measure': event.get('mc'),
                    'beat': event.get('mc_onset'),
                    'marking': event.get('Dynamic/subtype'),
                    'staff': staff,
                    'voice': voice
                }
                voices[voice_name]['dynamics'].append(dynamic_data)
    
    def _extract_lyrics_from_events(self, events_df, voices: Dict[str, Dict[str, Any]]):
        """Extract lyrics from events data and assign to SATB voices."""
        # Filter for events that have lyrics information
        lyrics_events = events_df[events_df['Chord/Lyrics/text'].notna()]
        
        for _, event in lyrics_events.iterrows():
            staff = event.get('staff')
            voice = event.get('voice')
            
            voice_name = self._map_staff_voice_to_part(staff, voice)
            if voice_name:
                lyric_data = {
                    'measure': event.get('mc'),
                    'beat': event.get('mc_onset'),
                    'text': event.get('Chord/Lyrics/text'),
                    'syllabic': event.get('Chord/Lyrics/syllabic'),
                    'staff': staff,
                    'voice': voice
                }
                voices[voice_name]['lyrics'].append(lyric_data)
    
    def _extract_dynamics_from_chords(self, chords_df, voices: Dict[str, Dict[str, Any]]):
        """Extract dynamics from chords data and assign to SATB voices."""
        # Filter for chords that have non-null dynamics
        dynamics_events = chords_df[chords_df['dynamics'].notna()]
        
        for _, chord in dynamics_events.iterrows():
            staff = chord.get('staff')
            voice = chord.get('voice')
            
            voice_name = self._map_staff_voice_to_part(staff, voice)
            if voice_name:
                dynamic_marking = chord.get('dynamics')
                if dynamic_marking and str(dynamic_marking).strip() and str(dynamic_marking).lower() != 'nan':
                    dynamic_data = {
                        'measure': chord.get('mc'),
                        'beat': chord.get('mc_onset'),
                        'marking': dynamic_marking,
                        'staff': staff,
                        'voice': voice
                    }
                    voices[voice_name]['dynamics'].append(dynamic_data)
    
    def _extract_lyrics_from_chords(self, chords_df, voices: Dict[str, Dict[str, Any]]):
        """Extract lyrics from chords data and assign to SATB voices."""
        # Filter for chords that have non-null lyrics
        lyrics_events = chords_df[chords_df['lyrics_1'].notna()]
        
        for _, chord in lyrics_events.iterrows():
            staff = chord.get('staff')
            voice = chord.get('voice')
            
            voice_name = self._map_staff_voice_to_part(staff, voice)
            if voice_name:
                lyric_text = chord.get('lyrics_1')
                if lyric_text and str(lyric_text).strip() and str(lyric_text).lower() != 'nan':
                    lyric_data = {
                        'measure': chord.get('mc'),
                        'beat': chord.get('mc_onset'),
                        'text': lyric_text,
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
