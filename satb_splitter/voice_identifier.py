"""
Deterministic Voice Identifier for SATB Voice Separation.

Uses clear, predictable rules based on MuseScore → MusicXML conversion patterns
instead of heuristic analysis.
"""

import music21
from .utils import VoiceMapping, VoiceLocation


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
        Analyze score using deterministic positional rules.
        
        Returns:
            VoiceMapping with deterministic assignments
        """
        print("🎯 Using deterministic voice identification")
        
        # Verify score structure matches expectations
        if len(self.score.parts) != 2:
            raise ValueError(f"Expected 2 parts for SATB, found {len(self.score.parts)}")
        
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
            print(f"Part {part_idx}: voices {part_voices[part_idx]}")
        
        # Apply deterministic mapping rules
        voice_mapping = self._apply_deterministic_rules(part_voices)
        
        # Validate the mapping
        self._validate_mapping(voice_mapping)
        
        return voice_mapping
    
    def _apply_deterministic_rules(self, part_voices: dict) -> VoiceMapping:
        """Apply the deterministic voice mapping rules."""
        
        # Expected voice structure after MuseScore → MusicXML conversion
        expected_mapping = {
            'soprano': {'part_index': 0, 'voice_id': '1'},
            'alto': {'part_index': 0, 'voice_id': '2'},
            'tenor': {'part_index': 1, 'voice_id': '5'},
            'bass': {'part_index': 1, 'voice_id': '6'}
        }
        
        # Create voice locations
        voice_locations = {}
        
        for voice_name, expected in expected_mapping.items():
            part_idx = expected['part_index']
            voice_id = expected['voice_id']
            
            # Check if expected voice exists
            if part_idx in part_voices and voice_id in part_voices[part_idx]:
                confidence = 1.0  # Deterministic = 100% confidence
                status = "✅"
            else:
                # Try fallback strategies
                confidence, voice_id = self._find_fallback_voice(
                    voice_name, part_idx, voice_id, part_voices)
                status = "🔄" if confidence > 0 else "❌"
            
            # Determine clef type for this voice
            clef_type = self._determine_clef_type(voice_name, part_idx)
            
            print(f"{voice_name.title()}: Part {part_idx}, Voice {voice_id} (confidence: {confidence:.1f}) {status}")
            
            voice_locations[voice_name] = VoiceLocation(
                part_index=part_idx,
                voice_id=voice_id,
                clef_type=clef_type,
                confidence=confidence
            )
        
        return VoiceMapping(
            soprano=voice_locations['soprano'],
            alto=voice_locations['alto'],
            tenor=voice_locations['tenor'],
            bass=voice_locations['bass']
        )
    
    def _find_fallback_voice(self, voice_name: str, part_idx: int, 
                           expected_voice_id: str, part_voices: dict) -> tuple:
        """
        Find fallback voice when expected voice doesn't exist.
        
        Returns:
            (confidence, voice_id) tuple
        """
        if part_idx not in part_voices:
            return (0.0, expected_voice_id)
        
        available_voices = part_voices[part_idx]
        
        if not available_voices:
            return (0.0, expected_voice_id)
        
        # Strategy 1: If only one voice available, use it
        if len(available_voices) == 1:
            print(f"  Fallback: {voice_name} using only available voice {available_voices[0]}")
            return (0.8, available_voices[0])
        
        # Strategy 2: Use positional fallback within part
        voice_position_map = {
            'soprano': 0,  # First voice in part
            'alto': 1,     # Second voice in part
            'tenor': 0,    # First voice in part
            'bass': 1      # Second voice in part
        }
        
        if voice_name in voice_position_map:
            position = voice_position_map[voice_name]
            if position < len(available_voices):
                fallback_voice = available_voices[position]
                print(f"  Fallback: {voice_name} using positional voice {fallback_voice}")
                return (0.6, fallback_voice)
        
        # Strategy 3: Use first available voice
        fallback_voice = available_voices[0]
        print(f"  Fallback: {voice_name} using first available voice {fallback_voice}")
        return (0.4, fallback_voice)
    
    def _validate_mapping(self, voice_mapping: VoiceMapping) -> None:
        """Validate that the voice mapping is reasonable."""
        
        # Check that all voices have reasonable confidence
        min_confidence = min([
            voice_mapping.soprano.confidence,
            voice_mapping.alto.confidence,
            voice_mapping.tenor.confidence,
            voice_mapping.bass.confidence
        ])
        
        if min_confidence < 0.4:
            print("⚠️  Warning: Some voice assignments have low confidence")
        
        # Check for duplicate assignments
        assignments = []
        for voice_name in ['soprano', 'alto', 'tenor', 'bass']:
            location = getattr(voice_mapping, voice_name)
            key = (location.part_index, location.voice_id)
            if key in assignments:
                print(f"⚠️  Warning: Duplicate assignment detected for {key}")
            assignments.append(key)
        
        print(f"Voice mapping validation complete")
    
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