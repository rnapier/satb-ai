"""
Deterministic Voice Identifier for SATB Voice Separation.

Uses clear, predictable rules based on MuseScore → MusicXML conversion patterns
instead of heuristic analysis.
"""

import music21
from .utils import VoiceMapping, VoiceLocation
from .exceptions import InvalidScoreError


class DeterministicVoiceIdentifier:
    """
    Deterministic voice identifier using clear positional rules.
    
    Implements the rule for MuseScore → MusicXML conversion:
    - Soprano: Part 0, Voice 1
    - Alto: Part 0, Voice 2
    - Tenor: Part 1, Voice 5  
    - Bass: Part 1, Voice 6
    """
    
    def __init__(self, score: music21.stream.Score):
        """
        Initialize the deterministic voice identifier.
        
        Args:
            score: The music21 score to analyze
        """
        self.score = score
    
    def analyze_score(self) -> VoiceMapping:
        """
        Apply strict hard-coded voice mapping.
        
        Returns:
            VoiceMapping with hard-coded assignments
        """
        print("🎯 Using hard-coded voice identification")
        
        # Verify score structure matches expectations
        if len(self.score.parts) != 2:
            raise InvalidScoreError(f"Expected 2 parts for SATB, found {len(self.score.parts)}")
        
        # Apply hard-coded mapping rules
        voice_mapping = self._apply_deterministic_rules()
        
        # Basic validation
        self._validate_mapping(voice_mapping)
        
        return voice_mapping
    
    def _apply_deterministic_rules(self) -> VoiceMapping:
        """Apply hard-coded voice mapping rules without fallback."""
        
        # Hard-coded voice structure for SATB
        expected_mapping = {
            'soprano': {'part_index': 0, 'voice_id': '1'},
            'alto': {'part_index': 0, 'voice_id': '2'},
            'tenor': {'part_index': 1, 'voice_id': '5'},
            'bass': {'part_index': 1, 'voice_id': '6'}
        }
        
        # Verify expected voices exist in score
        self._verify_voice_structure(expected_mapping)
        
        # Create voice locations with hard-coded mapping
        voice_locations = {}
        
        for voice_name, expected in expected_mapping.items():
            part_idx = expected['part_index']
            voice_id = expected['voice_id']
            
            # Determine clef type for this voice
            clef_type = self._determine_clef_type(voice_name, part_idx)
            
            print(f"{voice_name.title()}: Part {part_idx}, Voice {voice_id}")
            
            voice_locations[voice_name] = VoiceLocation(
                part_index=part_idx,
                voice_id=voice_id,
                clef_type=clef_type
            )
        
        return VoiceMapping(
            soprano=voice_locations['soprano'],
            alto=voice_locations['alto'],
            tenor=voice_locations['tenor'],
            bass=voice_locations['bass']
        )
    
    def _verify_voice_structure(self, expected_mapping: dict) -> None:
        """
        Verify that expected voice structure exists in score.
        
        Args:
            expected_mapping: Dictionary of expected voice mappings
            
        Raises:
            InvalidScoreError: If expected voices are not found
        """
        # Extract actual voices present in each part
        part_voices = {}
        for part_idx, part in enumerate(self.score.parts):
            voices_found = set()
            
            for measure in part.getElementsByClass('Measure'):
                if measure.voices:
                    for voice in measure.voices:
                        voice_id = voice.id or str(len(voices_found) + 1)
                        voices_found.add(voice_id)
                else:
                    # No explicit voices - treat as single voice
                    voices_found.add('1')
            
            part_voices[part_idx] = sorted(voices_found)
        
        # Verify each expected voice exists
        for voice_name, expected in expected_mapping.items():
            part_idx = expected['part_index']
            voice_id = expected['voice_id']
            
            if part_idx not in part_voices:
                raise InvalidScoreError(
                    f"Part {part_idx} not found in score. "
                    f"Required SATB structure: Part 0 (voices 1,2), Part 1 (voices 5,6)"
                )
            
            if voice_id not in part_voices[part_idx]:
                available_voices = ', '.join(part_voices[part_idx]) if part_voices[part_idx] else 'none'
                raise InvalidScoreError(
                    f"Expected voice '{voice_id}' not found in part {part_idx} for {voice_name}. "
                    f"Available voices: {available_voices}. "
                    f"Required SATB structure: Part 0 (voices 1,2), Part 1 (voices 5,6)"
                )
    
    def _validate_mapping(self, voice_mapping: VoiceMapping) -> None:
        """Validate that the voice mapping has no duplicate assignments."""
        
        # Check for duplicate assignments
        assignments = []
        for voice_name in ['soprano', 'alto', 'tenor', 'bass']:
            location = getattr(voice_mapping, voice_name)
            key = (location.part_index, location.voice_id)
            if key in assignments:
                raise InvalidScoreError(f"Duplicate assignment detected for part {key[0]}, voice {key[1]}")
            assignments.append(key)
        
        print("Voice mapping validation complete")
    
    def _determine_clef_type(self, voice_name: str, part_index: int) -> str:
        """Determine the clef type for a voice based on standard SATB conventions."""
        
        # Standard clef assignments for SATB
        if voice_name in ['soprano', 'alto']:
            return 'treble'
        else:  # tenor, bass
            return 'bass'


# Compatibility function to replace the heuristic identifier
def VoiceIdentifier(score: music21.stream.Score) -> DeterministicVoiceIdentifier:
    """
    Compatibility wrapper for deterministic voice identification.
    
    Args:
        score: Music21 score to analyze
        
    Returns:
        DeterministicVoiceIdentifier instance
    """
    return DeterministicVoiceIdentifier(score)