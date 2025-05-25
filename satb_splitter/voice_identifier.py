"""
Voice identification module for detecting SATB voice locations in scores.
"""

from typing import Dict, List, Optional, Tuple
import music21
from .utils import VoiceMapping, VoiceLocation, PartInfo, ProcessingOptions
from .exceptions import VoiceDetectionError


class VoiceIdentifier:
    """Identifies SATB voice locations in a score."""
    
    def __init__(self, score: music21.stream.Score, options: ProcessingOptions):
        """Initialize with score and processing options."""
        self.score = score
        self.options = options
        self.analysis_cache = {}
        
    def analyze_score(self) -> VoiceMapping:
        """
        Analyze score to identify voice locations.
        
        Returns:
            VoiceMapping with detected voice locations
            
        Raises:
            VoiceDetectionError: If voices cannot be detected
        """
        # If manual mapping is provided, use it
        if self.options.manual_voice_mapping:
            if self.options.manual_voice_mapping.validate():
                return self.options.manual_voice_mapping
            else:
                raise VoiceDetectionError("Manual voice mapping is invalid")
        
        # Try automatic detection
        if self.options.auto_detect_voices:
            try:
                return self._detect_voices_automatically()
            except Exception as e:
                if not self.options.fallback_to_defaults:
                    raise VoiceDetectionError(f"Automatic voice detection failed: {e}")
        
        # Fall back to default assumptions
        if self.options.fallback_to_defaults:
            return self._create_default_mapping()
        
        raise VoiceDetectionError("Could not detect voices and no fallback enabled")
    
    def _detect_voices_automatically(self) -> VoiceMapping:
        """Detect voices using pattern recognition and analysis."""
        part_info = self.detect_part_structure()
        
        # Analyze different common patterns
        patterns = [
            self._detect_closed_score_pattern(part_info),
            self._detect_open_score_pattern(part_info),
            self._detect_piano_reduction_pattern(part_info)
        ]
        
        # Choose the pattern with highest confidence
        best_pattern = max(patterns, key=lambda p: p.confidence if p else 0)
        
        if best_pattern and best_pattern.confidence > 0.6:
            return best_pattern
        
        raise VoiceDetectionError("No reliable voice pattern detected")
    
    def detect_part_structure(self) -> List[PartInfo]:
        """
        Analyze the part structure of the score.
        
        Returns:
            List of PartInfo objects describing each part
        """
        part_infos = []
        
        for i, part in enumerate(self.score.parts):
            # Get part name
            part_name = getattr(part, 'partName', None)
            if not part_name and hasattr(part, 'instrumentName'):
                part_name = part.instrumentName
            
            # Analyze clef
            clef = self._get_predominant_clef(part)
            
            # Count voices
            voice_count = self._count_voices_in_part(part)
            
            # Analyze pitch range
            pitch_range = self._analyze_pitch_range(part)
            
            # Count notes
            note_count = len(part.flatten().notes)
            
            part_info = PartInfo(
                index=i,
                name=part_name,
                clef=clef,
                voice_count=voice_count,
                pitch_range=pitch_range,
                note_count=note_count
            )
            part_infos.append(part_info)
        
        return part_infos
    
    def _detect_closed_score_pattern(self, part_info: List[PartInfo]) -> Optional[VoiceMapping]:
        """Detect closed score pattern (SA on treble staff, TB on bass staff)."""
        if len(part_info) != 2:
            return None
        
        treble_part = None
        bass_part = None
        
        for part in part_info:
            if 'treble' in part.clef.lower():
                treble_part = part
            elif 'bass' in part.clef.lower():
                bass_part = part
        
        if not (treble_part and bass_part):
            return None
        
        # Check if both parts have 2 voices
        if treble_part.voice_count >= 2 and bass_part.voice_count >= 2:
            return VoiceMapping(
                soprano=VoiceLocation(treble_part.index, '1', 'treble', 0.9),
                alto=VoiceLocation(treble_part.index, '2', 'treble', 0.9),
                tenor=VoiceLocation(bass_part.index, '1', 'bass', 0.9),
                bass=VoiceLocation(bass_part.index, '2', 'bass', 0.9),
                confidence=0.9
            )
        
        return None
    
    def _detect_open_score_pattern(self, part_info: List[PartInfo]) -> Optional[VoiceMapping]:
        """Detect open score pattern (each voice on separate staff)."""
        if len(part_info) != 4:
            return None
        
        # Sort parts by pitch range (highest to lowest)
        sorted_parts = sorted(part_info, key=lambda p: self._get_average_pitch(p), reverse=True)
        
        return VoiceMapping(
            soprano=VoiceLocation(sorted_parts[0].index, '1', sorted_parts[0].clef, 0.8),
            alto=VoiceLocation(sorted_parts[1].index, '1', sorted_parts[1].clef, 0.8),
            tenor=VoiceLocation(sorted_parts[2].index, '1', sorted_parts[2].clef, 0.8),
            bass=VoiceLocation(sorted_parts[3].index, '1', sorted_parts[3].clef, 0.8),
            confidence=0.8
        )
    
    def _detect_piano_reduction_pattern(self, part_info: List[PartInfo]) -> Optional[VoiceMapping]:
        """Detect piano reduction pattern (all voices on one staff)."""
        if len(part_info) != 1:
            return None
        
        part = part_info[0]
        if part.voice_count >= 4:
            return VoiceMapping(
                soprano=VoiceLocation(0, '1', part.clef, 0.7),
                alto=VoiceLocation(0, '2', part.clef, 0.7),
                tenor=VoiceLocation(0, '3', part.clef, 0.7),
                bass=VoiceLocation(0, '4', part.clef, 0.7),
                confidence=0.7
            )
        
        return None
    
    def _create_default_mapping(self) -> VoiceMapping:
        """Create default voice mapping based on common assumptions."""
        part_count = len(self.score.parts)
        
        if part_count == 2:
            # Assume closed score: SA on part 0, TB on part 1
            return VoiceMapping(
                soprano=VoiceLocation(0, '1', 'treble', 0.5),
                alto=VoiceLocation(0, '2', 'treble', 0.5),
                tenor=VoiceLocation(1, '1', 'bass', 0.5),
                bass=VoiceLocation(1, '2', 'bass', 0.5),
                confidence=0.5
            )
        elif part_count == 4:
            # Assume open score: each voice on separate part
            return VoiceMapping(
                soprano=VoiceLocation(0, '1', 'treble', 0.5),
                alto=VoiceLocation(1, '1', 'treble', 0.5),
                tenor=VoiceLocation(2, '1', 'bass', 0.5),
                bass=VoiceLocation(3, '1', 'bass', 0.5),
                confidence=0.5
            )
        elif part_count == 1:
            # Assume piano reduction: all voices on one part
            return VoiceMapping(
                soprano=VoiceLocation(0, '1', 'treble', 0.5),
                alto=VoiceLocation(0, '2', 'treble', 0.5),
                tenor=VoiceLocation(0, '3', 'treble', 0.5),
                bass=VoiceLocation(0, '4', 'treble', 0.5),
                confidence=0.5
            )
        else:
            raise VoiceDetectionError(f"Unsupported part count: {part_count}")
    
    def _get_predominant_clef(self, part: music21.stream.Part) -> str:
        """Get the predominant clef used in a part."""
        clefs = part.flatten().getElementsByClass(music21.clef.Clef)
        if clefs:
            # Return the first clef found
            clef = clefs[0]
            if isinstance(clef, music21.clef.TrebleClef):
                return 'treble'
            elif isinstance(clef, music21.clef.BassClef):
                return 'bass'
            elif isinstance(clef, music21.clef.AltoClef):
                return 'alto'
            else:
                return str(clef)
        return 'treble'  # Default assumption
    
    def _count_voices_in_part(self, part: music21.stream.Part) -> int:
        """Count the number of voices in a part."""
        voice_ids = set()
        
        for measure in part.getElementsByClass(music21.stream.Measure):
            for voice in measure.voices:
                voice_ids.add(voice.id)
        
        # If no explicit voices, assume single voice
        return max(1, len(voice_ids))
    
    def _analyze_pitch_range(self, part: music21.stream.Part) -> Tuple[str, str]:
        """Analyze the pitch range of a part."""
        notes = part.flatten().notes
        if not notes:
            return ('C4', 'C4')
        
        pitches = []
        for note in notes:
            if hasattr(note, 'pitch'):
                pitches.append(note.pitch)
            elif hasattr(note, 'pitches'):  # Chord
                pitches.extend(note.pitches)
        
        if not pitches:
            return ('C4', 'C4')
        
        lowest = min(pitches, key=lambda p: p.ps)
        highest = max(pitches, key=lambda p: p.ps)
        
        return (str(lowest), str(highest))
    
    def _get_average_pitch(self, part_info: PartInfo) -> float:
        """Get average pitch for a part (for sorting)."""
        try:
            low_pitch = music21.pitch.Pitch(part_info.pitch_range[0])
            high_pitch = music21.pitch.Pitch(part_info.pitch_range[1])
            return (low_pitch.ps + high_pitch.ps) / 2
        except:
            return 60.0  # Default to middle C
    
    def get_detection_confidence(self) -> float:
        """
        Get confidence level of voice detection (0.0 to 1.0).
        
        Returns:
            Confidence score for the detection
        """
        try:
            mapping = self.analyze_score()
            return mapping.confidence
        except:
            return 0.0
    
    def suggest_manual_mapping(self) -> List[VoiceMapping]:
        """
        Suggest possible manual voice mappings.
        
        Returns:
            List of possible voice mappings for user selection
        """
        suggestions = []
        part_info = self.detect_part_structure()
        
        # Try all detection patterns
        patterns = [
            self._detect_closed_score_pattern(part_info),
            self._detect_open_score_pattern(part_info),
            self._detect_piano_reduction_pattern(part_info)
        ]
        
        for pattern in patterns:
            if pattern:
                suggestions.append(pattern)
        
        # Add default mapping as fallback
        try:
            default = self._create_default_mapping()
            suggestions.append(default)
        except:
            pass
        
        return suggestions