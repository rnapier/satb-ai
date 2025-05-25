"""
Utility classes and functions for SATB splitting.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
import music21


@dataclass
class VoiceLocation:
    """Location of a voice in the score."""
    part_index: int
    voice_id: str
    clef_type: str
    confidence: float = 1.0


@dataclass
class VoiceMapping:
    """Complete mapping of SATB voices."""
    soprano: VoiceLocation
    alto: VoiceLocation
    tenor: VoiceLocation
    bass: VoiceLocation
    confidence: float = 1.0
    
    def validate(self) -> bool:
        """Validate that mapping is consistent."""
        # Check for duplicate locations
        locations = [
            (self.soprano.part_index, self.soprano.voice_id),
            (self.alto.part_index, self.alto.voice_id),
            (self.tenor.part_index, self.tenor.voice_id),
            (self.bass.part_index, self.bass.voice_id)
        ]
        return len(set(locations)) == 4
    


@dataclass
class PartInfo:
    """Information about a part in the score."""
    index: int
    name: Optional[str]
    clef: str
    voice_count: int
    pitch_range: Tuple[str, str]  # (lowest, highest)
    note_count: int


@dataclass
class ProcessingContext:
    """Context information for processing operations."""
    original_score: music21.stream.Score
    voice_mapping: VoiceMapping
    
    def get_voice_location(self, voice_name: str) -> VoiceLocation:
        """Get location for specific voice."""
        voice_name_lower = voice_name.lower()
        if voice_name_lower == 'soprano':
            return self.voice_mapping.soprano
        elif voice_name_lower == 'alto':
            return self.voice_mapping.alto
        elif voice_name_lower == 'tenor':
            return self.voice_mapping.tenor
        elif voice_name_lower == 'bass':
            return self.voice_mapping.bass
        else:
            raise ValueError(f"Unknown voice name: {voice_name}")
    
    def get_all_voices(self) -> List[str]:
        """Get list of all voice names."""
        return ['Soprano', 'Alto', 'Tenor', 'Bass']


@dataclass
class ValidationResult:
    """Result of validation operation."""
    valid: bool
    warnings: List[str]
    errors: List[str]
    details: Dict[str, Any]


@dataclass
class RemovalResult:
    """Result of voice removal operation."""
    success: bool
    voices_removed: List[str]
    elements_preserved: int
    elements_removed: int
    warnings: List[str]
    errors: List[str]


@dataclass
class SimplificationResult:
    """Result of staff simplification operation."""
    success: bool
    original_staff_count: int
    final_staff_count: int
    clef_assigned: str
    elements_merged: int
    warnings: List[str]
    errors: List[str]


@dataclass
class UnificationResult:
    """Result of complete unification process."""
    success: bool
    rules_applied: List[str]
    dynamics_unified: int
    lyrics_unified: int
    spanners_unified: int
    warnings: List[str]
    errors: List[str]
    processing_time: float


@dataclass
class ProcessingResult:
    """Complete result of SATB processing."""
    success: bool
    voice_scores: Dict[str, music21.stream.Score]
    voice_mapping: VoiceMapping
    processing_steps: List[str]
    statistics: Dict[str, Any]
    warnings: List[str]
    errors: List[str]
    processing_time: float


def load_score(file_path: str) -> music21.stream.Score:
    """
    Load score from file with proper error handling.
    
    Args:
        file_path: Path to score file
        
    Returns:
        Loaded score object
        
    Raises:
        InvalidScoreError: If file cannot be loaded or is invalid
    """
    from .exceptions import InvalidScoreError
    
    try:
        score = music21.converter.parse(file_path)
        if not isinstance(score, music21.stream.Score):
            raise InvalidScoreError(f"File does not contain a valid score: {file_path}")
        return score
    except Exception as e:
        raise InvalidScoreError(f"Failed to load score from {file_path}: {e}")


def save_voice_scores(voice_scores: Dict[str, music21.stream.Score], 
                     output_dir: str,
                     base_name: str) -> List[str]:
    """
    Save voice scores to files.
    
    Args:
        voice_scores: Dictionary of voice scores
        output_dir: Output directory
        base_name: Base name for output files
        
    Returns:
        List of created file paths
    """
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    created_files = []
    
    for voice_name, voice_score in voice_scores.items():
        # Create output filename
        filename = f"{base_name}-{voice_name}.musicxml"
        filepath = output_path / filename
        
        # Set part title within the score
        if voice_score.parts:
            voice_score.parts[0].partName = f"{base_name} ({voice_name})"
        
        # Update the score's title metadata
        if not voice_score.metadata:
            voice_score.metadata = music21.metadata.Metadata()
        
        new_title = f"{base_name} ({voice_name})"
        voice_score.metadata.title = new_title
        
        # Clear movementName if it contains filename with extension
        if hasattr(voice_score.metadata, 'movementName') and voice_score.metadata.movementName:
            movement_name = str(voice_score.metadata.movementName)
            if movement_name.endswith('.musicxml'):
                voice_score.metadata.movementName = None
        
        # Write to file
        voice_score.write('musicxml', fp=str(filepath))
        created_files.append(str(filepath))
    
    return created_files