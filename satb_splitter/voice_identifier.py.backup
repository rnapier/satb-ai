"""
Voice identification module for detecting SATB voice locations in scores.
"""

from typing import Dict, List, Optional, Tuple
import music21
from .utils import VoiceMapping, VoiceLocation, PartInfo
from .exceptions import VoiceDetectionError


class VoiceIdentifier:
    """Identifies SATB voice locations in a score."""
    
    def __init__(self, score: music21.stream.Score):
        """Initialize with score."""
        self.score = score
        
    def analyze_score(self) -> VoiceMapping:
        """
        Analyze score to identify voice locations.
        
        Returns:
            VoiceMapping with detected voice locations
            
        Raises:
            VoiceDetectionError: If voices cannot be detected
        """
        # Try automatic detection
        try:
            return self._detect_voices_automatically()
        except (AttributeError, ValueError, TypeError) as e:
            # Fall back to default mapping
            pass
        except music21.exceptions21.Music21Exception as e:
            # Fall back to default mapping
            pass
        except KeyError as e:
            # Fall back to default mapping
            pass
        except Exception as e:
            # Log unexpected exceptions for debugging
            import logging
            logging.error(f"Unexpected error in voice detection: {type(e).__name__}: {e}")
            # Fall back to default mapping
        
        # Fall back to default assumptions
        return self._create_default_mapping()
    
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
            
            # Count notes (cache flattened view for efficiency)
            flattened_part = part.flatten()
            note_count = len(flattened_part.notes)
            
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
    
    def _get_predominant_clef(self, score: music21.stream.Score, part_index: int) -> music21.clef.Clef:
        """Get the predominant clef for a part using proper music21 type checking."""
        import music21
        
        if part_index >= len(score.parts):
            return music21.clef.TrebleClef()  # Default fallback
        
        part = score.parts[part_index]
        clefs = part.flat.getElementsByClass(music21.clef.Clef)
        
        if not clefs:
            return music21.clef.TrebleClef()  # Default fallback
        
        # Count occurrences of each clef type
        clef_counts = {}
        for clef in clefs:
            clef_type = type(clef)
            clef_counts[clef_type] = clef_counts.get(clef_type, 0) + 1
        
        # Return the most common clef type
        if clef_counts:
            predominant_clef_type = max(clef_counts, key=clef_counts.get)
            return predominant_clef_type()
        
        return music21.clef.TrebleClef()  # Default fallback
    
    def _is_treble_clef(self, clef: music21.clef.Clef) -> bool:
        """Check if clef is a treble clef using proper type checking."""
        import music21
        return isinstance(clef, (music21.clef.TrebleClef, music21.clef.Treble8vbClef, music21.clef.Treble8vaClef))
    
    def _is_bass_clef(self, clef: music21.clef.Clef) -> bool:
        """Check if clef is a bass clef using proper type checking."""
        import music21
        return isinstance(clef, (music21.clef.BassClef, music21.clef.Bass8vbClef, music21.clef.Bass8vaClef))
    
    def _detect_closed_score_pattern(self, part_info: List[PartInfo]) -> Optional[VoiceMapping]:
        """Detect closed score pattern (SA on treble staff, TB on bass staff)."""
        if len(part_info) != 2:
            return None
        
        treble_part = None
        bass_part = None
        
        for part in part_info:
            # Get the predominant clef for this part using proper music21 type checking
            clef = self._get_predominant_clef(self.score, part.index)
            if self._is_treble_clef(clef):
                treble_part = part
            elif self._is_bass_clef(clef):
                bass_part = part
        
        if not (treble_part and bass_part):
            return None
        
        # Check if both parts have 2 voices
        if treble_part.voice_count >= 2 and bass_part.voice_count >= 2:
            # Calculate confidence based on musical analysis instead of hard-coded values
            soprano_confidence = self._calculate_voice_confidence(treble_part, '1', 'soprano')
            alto_confidence = self._calculate_voice_confidence(treble_part, '2', 'alto')
            tenor_confidence = self._calculate_voice_confidence(bass_part, '1', 'tenor')
            bass_confidence = self._calculate_voice_confidence(bass_part, '2', 'bass')
            
            # Overall confidence is the average of individual voice confidences
            overall_confidence = (soprano_confidence + alto_confidence +
                                tenor_confidence + bass_confidence) / 4.0
            
            return VoiceMapping(
                soprano=VoiceLocation(treble_part.index, '1', 'treble', soprano_confidence),
                alto=VoiceLocation(treble_part.index, '2', 'treble', alto_confidence),
                tenor=VoiceLocation(bass_part.index, '1', 'bass', tenor_confidence),
                bass=VoiceLocation(bass_part.index, '2', 'bass', bass_confidence),
                confidence=overall_confidence
            )
        
        return None
    
    def _calculate_voice_confidence(self, part_info: 'PartInfo', voice_id: str,
                                  expected_voice_type: str) -> float:
        """
        Calculate confidence score based on musical analysis.
        
        Args:
            part_info: Information about the part
            voice_id: Voice ID within the part
            expected_voice_type: Expected voice type (soprano, alto, tenor, bass)
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence_factors = []
        
        try:
            # Factor 1: Pitch range analysis
            pitch_confidence = self._analyze_pitch_range_confidence(part_info, expected_voice_type)
            confidence_factors.append(('pitch_range', pitch_confidence, 0.4))
            
            # Factor 2: Clef appropriateness
            clef_confidence = self._analyze_clef_confidence(part_info, expected_voice_type)
            confidence_factors.append(('clef', clef_confidence, 0.3))
            
            # Factor 3: Note density and rhythm complexity
            density_confidence = self._analyze_note_density_confidence(part_info, expected_voice_type)
            confidence_factors.append(('note_density', density_confidence, 0.2))
            
            # Factor 4: Part name analysis
            name_confidence = self._analyze_part_name_confidence(part_info, expected_voice_type)
            confidence_factors.append(('part_name', name_confidence, 0.1))
            
            # Calculate weighted average
            total_weight = sum(weight for _, _, weight in confidence_factors)
            weighted_sum = sum(score * weight for _, score, weight in confidence_factors)
            
            final_confidence = weighted_sum / total_weight if total_weight > 0 else 0.5
            
            # Ensure confidence is within valid range
            return max(0.0, min(1.0, final_confidence))
            
        except Exception:
            # If analysis fails, return moderate confidence
            return 0.6
    
    def _analyze_pitch_range_confidence(self, part_info: 'PartInfo', voice_type: str) -> float:
        """Analyze how well the pitch range matches expected voice type."""
        # Define expected pitch ranges (MIDI note numbers)
        expected_ranges = {
            'soprano': (60, 84),  # C4 to C6
            'alto': (55, 79),     # G3 to G5
            'tenor': (48, 72),    # C3 to C5
            'bass': (40, 64)      # E2 to E4
        }
        
        if voice_type.lower() not in expected_ranges:
            return 0.5
        
        expected_min, expected_max = expected_ranges[voice_type.lower()]
        
        # Calculate overlap with expected range
        if hasattr(part_info, 'pitch_range') and part_info.pitch_range:
            actual_min, actual_max = part_info.pitch_range
            
            # Calculate overlap percentage
            overlap_min = max(expected_min, actual_min)
            overlap_max = min(expected_max, actual_max)
            
            if overlap_max > overlap_min:
                overlap_size = overlap_max - overlap_min
                expected_size = expected_max - expected_min
                actual_size = actual_max - actual_min
                
                # Confidence based on overlap relative to expected range
                overlap_ratio = overlap_size / expected_size
                
                # Bonus for staying within expected range
                if actual_min >= expected_min - 2 and actual_max <= expected_max + 2:
                    overlap_ratio += 0.2
                
                return min(1.0, overlap_ratio)
        
        return 0.5  # Default if no pitch range info
    
    def _analyze_clef_confidence(self, part_info: 'PartInfo', voice_type: str) -> float:
        """Analyze clef appropriateness for voice type."""
        if not hasattr(part_info, 'predominant_clef') or not part_info.predominant_clef:
            return 0.5
        
        clef = part_info.predominant_clef
        voice_lower = voice_type.lower()
        
        # Expected clefs for each voice type
        if voice_lower in ['soprano', 'alto']:
            if isinstance(clef, music21.clef.TrebleClef):
                return 0.9
            elif isinstance(clef, music21.clef.AltoClef) and voice_lower == 'alto':
                return 0.8
            else:
                return 0.3
        elif voice_lower in ['tenor', 'bass']:
            if isinstance(clef, music21.clef.BassClef):
                return 0.9
            elif isinstance(clef, music21.clef.TrebleClef) and voice_lower == 'tenor':
                return 0.7  # Tenor can use treble clef 8va bassa
            else:
                return 0.3
        
        return 0.5
    
    def _analyze_note_density_confidence(self, part_info: 'PartInfo', voice_type: str) -> float:
        """Analyze note density and rhythm complexity."""
        try:
            if hasattr(part_info, 'note_count') and part_info.note_count:
                # Very basic heuristic: moderate note density suggests vocal writing
                if 10 <= part_info.note_count <= 200:
                    return 0.8
                elif part_info.note_count < 10:
                    return 0.4  # Too sparse
                else:
                    return 0.6  # Very dense, possibly instrumental
            
            return 0.6  # Default moderate confidence
            
        except Exception:
            return 0.6
    
    def _analyze_part_name_confidence(self, part_info: 'PartInfo', voice_type: str) -> float:
        """Analyze part name for voice type indicators."""
        if not hasattr(part_info, 'part_name') or not part_info.part_name:
            return 0.5
        
        part_name_lower = part_info.part_name.lower()
        voice_lower = voice_type.lower()
        
        # Direct name match
        if voice_lower in part_name_lower:
            return 0.95
        
        # Common abbreviations and synonyms
        name_mappings = {
            'soprano': ['sop', 's.', 'treble', 'descant'],
            'alto': ['alt', 'a.', 'contralto'],
            'tenor': ['ten', 't.', 'ténor'],
            'bass': ['bas', 'b.', 'basse', 'baixo']
        }
        
        if voice_lower in name_mappings:
            for variant in name_mappings[voice_lower]:
                if variant in part_name_lower:
                    return 0.85
        
        # Check for voice position indicators
        position_indicators = {
            'soprano': ['1', 'i', 'upper', 'high'],
            'alto': ['2', 'ii', 'middle'],
            'tenor': ['3', 'iii', 'lower'],
            'bass': ['4', 'iv', 'low', 'bottom']
        }
        
        if voice_lower in position_indicators:
            for indicator in position_indicators[voice_lower]:
                if indicator in part_name_lower:
                    return 0.7
        
        return 0.5  # No clear indicators
    
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
        # Use cached flattened view for performance
        flattened_part = part.flatten()
        notes = flattened_part.notes
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
    