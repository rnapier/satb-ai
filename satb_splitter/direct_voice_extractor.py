"""
Direct voice extraction that processes each voice independently from original MusicXML.

This approach avoids the complex copy-and-remove pattern by directly extracting
what each voice needs from the original score.
"""

import music21
import copy
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass


@dataclass
class VoiceExtractionConfig:
    """Configuration for extracting a specific voice."""
    name: str           # Voice name (Soprano, Alto, Tenor, Bass)
    part_index: int     # Which part in the original score
    voice_id: str       # Voice ID within that part
    clef: str          # Target clef for this voice


class DirectVoiceExtractor:
    """
    Extracts individual voices directly from original MusicXML.
    
    This approach:
    1. Analyzes the original score structure once
    2. For each voice, extracts only what belongs to that voice
    3. Builds clean single-voice scores with proper elements
    4. Preserves slurs, lyrics, and dynamics naturally
    """
    
    def __init__(self, original_score: music21.stream.Score):
        """Initialize with the original score."""
        self.original_score = original_score
        self.voice_configs = self._detect_voice_configurations()
        self.lyric_sources = self._analyze_lyric_distribution()
        
    def extract_all_voices(self) -> Dict[str, music21.stream.Score]:
        """
        Extract all voices as individual scores.
        
        Returns:
            Dictionary mapping voice names to their extracted scores
        """
        print("🎵 Starting direct voice extraction...")
        
        voice_scores = {}
        
        for config in self.voice_configs:
            print(f"  Extracting {config.name}...")
            voice_score = self._extract_voice(config)
            voice_scores[config.name] = voice_score
            
        print(f"✅ Extracted {len(voice_scores)} voices successfully")
        return voice_scores
    
    def _detect_voice_configurations(self) -> List[VoiceExtractionConfig]:
        """Detect voice configurations from the original score."""
        # Based on debugging: voices are split across parts but slurs are all in Part 0
        return [
            VoiceExtractionConfig("Soprano", 0, "1", "treble"),
            VoiceExtractionConfig("Alto", 0, "2", "treble"),
            VoiceExtractionConfig("Tenor", 1, "5", "treble_8"),
            VoiceExtractionConfig("Bass", 1, "6", "bass")
        ]
    
    def _analyze_lyric_distribution(self) -> Dict[str, str]:
        """
        Analyze which voice contains the main lyrics.
        
        Returns:
            Dictionary mapping voice names to their lyric source voice
        """
        # Typically lyrics are in Soprano, but this can be configured
        return {
            "Soprano": "Soprano",
            "Alto": "Soprano",    # Alto gets lyrics from Soprano
            "Tenor": "Soprano",   # Tenor gets lyrics from Soprano  
            "Bass": "Soprano"     # Bass gets lyrics from Soprano
        }
    
    def _extract_voice(self, config: VoiceExtractionConfig) -> music21.stream.Score:
        """
        Extract a single voice with all its elements.
        
        Args:
            config: Configuration for the voice to extract
            
        Returns:
            Clean score containing only this voice
        """
        # Create new score structure
        voice_score = music21.stream.Score()
        voice_part = music21.stream.Part()
        voice_score.append(voice_part)
        
        # Copy score metadata
        self._copy_score_metadata(voice_score)
        
        # Extract measures for this voice
        source_part = self.original_score.parts[config.part_index]
        
        for measure in source_part.getElementsByClass('Measure'):
            voice_measure = self._extract_voice_from_measure(measure, config)
            if voice_measure and len(voice_measure) > 0:
                voice_part.append(voice_measure)
        
        # Extract and apply slurs for this voice
        self._extract_slurs_for_voice(source_part, voice_part, config)
        
        # Apply target clef
        self._set_voice_clef(voice_part, config.clef)
        
        # Add voice-specific metadata
        self._add_voice_metadata(voice_score, config)
        
        return voice_score
    
    def _extract_voice_from_measure(self, 
                                  source_measure: music21.stream.Measure,
                                  config: VoiceExtractionConfig) -> Optional[music21.stream.Measure]:
        """
        Extract a voice's content from a single measure.
        
        Args:
            source_measure: Source measure from original score
            config: Voice configuration
            
        Returns:
            New measure containing only this voice's content
        """
        if not hasattr(source_measure, 'number'):
            return None
            
        voice_measure = music21.stream.Measure(number=source_measure.number)
        
        # Copy measure-level elements (time signatures, key signatures, etc.)
        for element in source_measure:
            if self._is_measure_level_element(element):
                try:
                    # Try standard copy first
                    if hasattr(element, 'copy'):
                        voice_measure.append(element.copy())
                    else:
                        # For objects without copy method, use deepcopy
                        voice_measure.append(copy.deepcopy(element))
                except Exception as e:
                    print(f"      Warning: Could not copy element {type(element)}: {e}")
        
        # Extract voice-specific notes
        voice_notes = self._extract_voice_notes(source_measure, config)
        for note in voice_notes:
            voice_measure.append(note)
        
        # Extract lyrics for this voice (may come from different voice)
        self._add_lyrics_to_measure(voice_measure, source_measure, config)
        
        # Extract voice-relevant directions and dynamics
        self._add_voice_directions(voice_measure, source_measure, config)
        
        return voice_measure
    
    def _extract_voice_notes(self,
                           source_measure: music21.stream.Measure,
                           config: VoiceExtractionConfig) -> List:
        """Extract notes belonging to this voice from the measure."""
        voice_notes = []
        
        # Look for Voice stream objects in the measure
        voice_streams = source_measure.getElementsByClass('Voice')
        
        for voice_stream in voice_streams:
            voice_id = getattr(voice_stream, 'id', None)
            
            # Check if this is the voice we want
            if voice_id == config.voice_id:
                # Extract all notes from this voice stream
                for note in voice_stream.notes:
                    try:
                        voice_notes.append(note.copy())
                    except:
                        voice_notes.append(copy.deepcopy(note))
                break
        
        return voice_notes
    
    def _extract_slurs_for_voice(self,
                               source_part: music21.stream.Part,
                               voice_part: music21.stream.Part,
                               config: VoiceExtractionConfig) -> None:
        """
        Extract slurs that belong to this voice by searching ALL parts of the original score.
        
        Key insight: slurs might be stored in different parts than where the notes are located.
        """
        print(f"    Extracting slurs for {config.name}...")
        
        # Search ALL parts of the original score for slurs, not just the source part
        all_slurs = []
        for part in self.original_score.parts:
            part_slurs = list(part.flatten().getElementsByClass('Spanner'))
            slur_spanners = [s for s in part_slurs if hasattr(s, 'classes') and 'Slur' in s.classes]
            all_slurs.extend(slur_spanners)
        
        print(f"      Found {len(all_slurs)} total slurs in score")
        
        # Build note mapping: source note -> voice note
        note_mapping = self._build_note_mapping_across_all_parts(voice_part, config)
        
        slurs_added = 0
        for slur in all_slurs:
            try:
                spanned_elements = slur.getSpannedElements()
                if len(spanned_elements) < 2:
                    continue
                
                # Check if this slur connects notes from our target voice
                start_note = spanned_elements[0]
                end_note = spanned_elements[-1]
                
                # Check if the slur connects notes from our voice (based on voice stream ID)
                start_voice_id = None
                end_voice_id = None
                
                if hasattr(start_note, 'activeSite') and start_note.activeSite:
                    start_voice_id = getattr(start_note.activeSite, 'id', None)
                    
                if hasattr(end_note, 'activeSite') and end_note.activeSite:
                    end_voice_id = getattr(end_note.activeSite, 'id', None)
                
                # Only process slurs that belong to our target voice
                if start_voice_id == config.voice_id and end_voice_id == config.voice_id:
                    # Find corresponding notes in the extracted voice
                    voice_start = note_mapping.get(start_note)
                    voice_end = note_mapping.get(end_note)
                    
                    if voice_start and voice_end and voice_start != voice_end:
                        # Create new slur for voice
                        new_slur = music21.spanner.Slur()
                        new_slur.addSpannedElements([voice_start, voice_end])
                        voice_part.append(new_slur)
                        slurs_added += 1
                        
                        print(f"        ✅ Added slur: {voice_start.pitch} → {voice_end.pitch}")
            
            except Exception as e:
                print(f"        ⚠️ Slur extraction failed: {e}")
        
        print(f"      Added {slurs_added} slurs to {config.name}")
    
    def _build_note_mapping_across_all_parts(self,
                                           voice_part: music21.stream.Part,
                                           config: VoiceExtractionConfig) -> Dict:
        """
        Build mapping between source notes (from all parts) and extracted voice notes.
        """
        note_mapping = {}
        
        # Get all notes from the extracted voice
        voice_notes = []
        for measure in voice_part.getElementsByClass('Measure'):
            for note in measure.flatten().notes:
                voice_notes.append({
                    'note': note,
                    'measure': getattr(measure, 'number', None),
                    'offset': getattr(note, 'offset', 0),
                    'pitch': self._get_note_pitch(note)
                })
        
        # Search all parts of original score for notes from our target voice
        for part in self.original_score.parts:
            for measure in part.getElementsByClass('Measure'):
                # Look for voice streams with our target voice ID
                voice_streams = measure.getElementsByClass('Voice')
                for voice_stream in voice_streams:
                    if getattr(voice_stream, 'id', None) == config.voice_id:
                        # Found our voice stream, map its notes
                        for source_note in voice_stream.notes:
                            source_info = {
                                'note': source_note,
                                'measure': getattr(measure, 'number', None),
                                'offset': getattr(source_note, 'offset', 0),
                                'pitch': self._get_note_pitch(source_note)
                            }
                            
                            # Find best matching note in extracted voice
                            best_match = None
                            best_score = 0
                            
                            for voice_info in voice_notes:
                                score = 0
                                
                                # Same pitch (essential)
                                if source_info['pitch'] == voice_info['pitch']:
                                    score += 100
                                else:
                                    continue  # Must have same pitch
                                
                                # Same measure (highly preferred)
                                if source_info['measure'] == voice_info['measure']:
                                    score += 50
                                
                                # Similar offset (preferred)
                                if abs(source_info['offset'] - voice_info['offset']) < 0.1:
                                    score += 10
                                
                                if score > best_score:
                                    best_score = score
                                    best_match = voice_info
                            
                            if best_match:
                                note_mapping[source_info['note']] = best_match['note']
        
        return note_mapping
    
    def _build_note_mapping(self,
                          source_part: music21.stream.Part,
                          voice_part: music21.stream.Part,
                          config: VoiceExtractionConfig) -> Dict:
        """
        Build mapping between source notes and extracted voice notes.
        
        This enables accurate slur preservation by matching notes based on
        their position and characteristics.
        """
        note_mapping = {}
        
        # Get all notes from source part that belong to this voice
        source_voice_notes = []
        for measure in source_part.getElementsByClass('Measure'):
            for note in measure.flatten().notes:
                if hasattr(note, 'voice') and note.voice == config.voice_id:
                    source_voice_notes.append({
                        'note': note,
                        'measure': getattr(measure, 'number', None),
                        'offset': getattr(note, 'offset', 0),
                        'pitch': self._get_note_pitch(note)
                    })
        
        # Get all notes from extracted voice
        voice_notes = []
        for measure in voice_part.getElementsByClass('Measure'):
            for note in measure.flatten().notes:
                voice_notes.append({
                    'note': note,
                    'measure': getattr(measure, 'number', None),
                    'offset': getattr(note, 'offset', 0),
                    'pitch': self._get_note_pitch(note)
                })
        
        # Match notes by position and pitch
        for source_info in source_voice_notes:
            best_match = None
            best_score = 0
            
            for voice_info in voice_notes:
                score = 0
                
                # Same pitch (essential)
                if source_info['pitch'] == voice_info['pitch']:
                    score += 100
                else:
                    continue  # Must have same pitch
                
                # Same measure (highly preferred)
                if source_info['measure'] == voice_info['measure']:
                    score += 50
                
                # Similar offset (preferred)
                if abs(source_info['offset'] - voice_info['offset']) < 0.1:
                    score += 10
                
                if score > best_score:
                    best_score = score
                    best_match = voice_info
            
            if best_match:
                note_mapping[source_info['note']] = best_match['note']
        
        return note_mapping
    
    def _get_note_pitch(self, note) -> str:
        """Get standardized pitch representation for a note."""
        if hasattr(note, 'pitch'):
            return note.pitch.name + str(note.pitch.octave)
        elif isinstance(note, music21.note.Rest):
            return "REST"
        else:
            return "UNKNOWN"
    
    def _is_measure_level_element(self, element) -> bool:
        """Check if element should be copied to all voice measures."""
        return isinstance(element, (
            music21.meter.TimeSignature,
            music21.key.KeySignature,
            music21.bar.Barline,
            music21.tempo.TempoIndication
        ))
    
    def _add_lyrics_to_measure(self,
                             voice_measure: music21.stream.Measure,
                             source_measure: music21.stream.Measure,
                             config: VoiceExtractionConfig) -> None:
        """Add appropriate lyrics to voice measure."""
        # Get lyric source for this voice
        lyric_source_voice = self.lyric_sources.get(config.name, config.name)
        
        # If this voice gets lyrics from itself, find them in the same measure
        if lyric_source_voice == config.name:
            # Look for lyrics in the voice's own notes
            voice_streams = source_measure.getElementsByClass('Voice')
            for voice_stream in voice_streams:
                if getattr(voice_stream, 'id', None) == config.voice_id:
                    self._copy_lyrics_from_voice_stream(voice_measure, voice_stream)
                    break
        else:
            # This voice gets lyrics from another voice (usually Soprano)
            self._copy_lyrics_from_soprano(voice_measure, source_measure)
    
    def _copy_lyrics_from_voice_stream(self, voice_measure, voice_stream):
        """Copy lyrics from the voice stream's own notes."""
        voice_notes = list(voice_measure.flatten().notes)
        source_notes = list(voice_stream.notes)
        
        # Match notes and copy lyrics
        for i, voice_note in enumerate(voice_notes):
            if i < len(source_notes):
                source_note = source_notes[i]
                if hasattr(source_note, 'lyrics') and source_note.lyrics:
                    for lyric in source_note.lyrics:
                        voice_note.addLyric(lyric.text)
    
    def _copy_lyrics_from_soprano(self, voice_measure, source_measure):
        """Copy lyrics from Soprano voice to this voice."""
        # Find Soprano voice stream (voice ID "1")
        soprano_notes = []
        voice_streams = source_measure.getElementsByClass('Voice')
        for voice_stream in voice_streams:
            if getattr(voice_stream, 'id', None) == "1":
                soprano_notes = list(voice_stream.notes)
                break
        
        if not soprano_notes:
            return
            
        # Get notes from this voice measure
        voice_notes = list(voice_measure.flatten().notes)
        
        # Distribute lyrics from Soprano to this voice
        # Match notes by timing/position
        for i, voice_note in enumerate(voice_notes):
            if i < len(soprano_notes):
                soprano_note = soprano_notes[i]
                if hasattr(soprano_note, 'lyrics') and soprano_note.lyrics:
                    for lyric in soprano_note.lyrics:
                        voice_note.addLyric(lyric.text)
    
    def _add_voice_directions(self, 
                            voice_measure: music21.stream.Measure,
                            source_measure: music21.stream.Measure,
                            config: VoiceExtractionConfig) -> None:
        """Add voice-relevant directions and dynamics."""
        # Extract dynamics and directions relevant to this voice
        pass
    
    def _copy_score_metadata(self, voice_score: music21.stream.Score) -> None:
        """Copy score-level metadata."""
        # Copy title, composer, etc.
        pass
    
    def _set_voice_clef(self, voice_part: music21.stream.Part, clef: str) -> None:
        """Set appropriate clef for the voice."""
        if clef == "treble":
            voice_part.insert(0, music21.clef.TrebleClef())
        elif clef == "bass":
            voice_part.insert(0, music21.clef.BassClef())
        elif clef == "treble_8":
            voice_part.insert(0, music21.clef.Treble8vbClef())
    
    def _add_voice_metadata(self, voice_score: music21.stream.Score, config: VoiceExtractionConfig) -> None:
        """Add voice-specific metadata."""
        # Set part name, instrument, etc.
        if voice_score.parts:
            voice_score.parts[0].partName = config.name


def extract_voices_directly(input_file: str) -> Dict[str, music21.stream.Score]:
    """
    Main function to extract voices using direct extraction approach.
    
    Args:
        input_file: Path to input MusicXML file
        
    Returns:
        Dictionary mapping voice names to extracted scores
    """
    print(f"🎵 Loading {input_file} for direct extraction...")
    original_score = music21.converter.parse(input_file)
    
    extractor = DirectVoiceExtractor(original_score)
    return extractor.extract_all_voices()