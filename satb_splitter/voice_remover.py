"""
Voice removal module for surgically removing unwanted voices from score copies.
"""

from typing import List, Set
import music21
from .utils import VoiceLocation, ProcessingContext, RemovalResult
from .exceptions import VoiceRemovalError


class VoiceRemover:
    """Removes unwanted voices from score copies."""
    
    def __init__(self, context: ProcessingContext):
        """Initialize with processing context."""
        self.context = context
        
    def remove_voices_except(self, score: music21.stream.Score, 
                           keep_voice: VoiceLocation) -> RemovalResult:
        """
        Remove all voices except the specified one.
        
        Args:
            score: Score to modify (modified in place)
            keep_voice: Voice to preserve
            
        Returns:
            RemovalResult with statistics and status
            
        Raises:
            VoiceRemovalError: If removal fails
        """
        try:
            voices_removed = []
            elements_preserved = 0
            elements_removed = 0
            warnings = []
            errors = []
            
            # Collect parts to remove
            parts_to_remove = []
            
            # Process each part
            for part_idx, part in enumerate(score.parts):
                if part_idx == keep_voice.part_index:
                    # This is the part containing our target voice
                    result = self._remove_other_voices_from_part(part, keep_voice.voice_id)
                    voices_removed.extend(result['voices_removed'])
                    elements_preserved += result['elements_preserved']
                    elements_removed += result['elements_removed']
                    warnings.extend(result['warnings'])
                else:
                    # Mark this entire part for removal
                    note_count = len(part.flatten().notes)
                    elements_removed += note_count
                    voices_removed.append(f"Part {part_idx}")
                    parts_to_remove.append(part)
            
            # Actually remove the unwanted parts
            for part in parts_to_remove:
                score.remove(part)
            
            # Remove any remaining empty parts
            self._remove_empty_parts(score)
            
            # Clean up empty measures
            self._clean_empty_measures(score)
            
            return RemovalResult(
                success=True,
                voices_removed=voices_removed,
                elements_preserved=elements_preserved,
                elements_removed=elements_removed,
                warnings=warnings,
                errors=errors
            )
            
        except Exception as e:
            raise VoiceRemovalError(f"Voice removal failed: {e}")
    
    def _remove_other_voices_from_part(self, part: music21.stream.Part, 
                                     keep_voice_id: str) -> dict:
        """Remove all voices except the specified one from a part."""
        voices_removed = []
        elements_preserved = 0
        elements_removed = 0
        warnings = []
        
        for measure in part.getElementsByClass(music21.stream.Measure):
            # Get all voices in this measure
            voices = list(measure.voices)
            
            if not voices:
                # No explicit voices, check if this measure has the content we want
                # For measures without explicit voices, we keep everything if it's the right part
                elements_preserved += len(measure.notes)
                continue
            
            # Find the voice to keep (standardize on string voice IDs per music21 convention)
            target_voice = None
            keep_voice_id_str = str(keep_voice_id)
            
            # First try to find by voice ID
            for voice in voices:
                if str(voice.id) == keep_voice_id_str:
                    target_voice = voice
                    break
            
            # If not found and keep_voice_id is numeric, try index-based access as fallback
            if target_voice is None and keep_voice_id_str.isdigit():
                voice_index = int(keep_voice_id_str) - 1  # Convert to 0-based index
                if 0 <= voice_index < len(voices):
                    target_voice = voices[voice_index]
                    warnings.append(f"Voice ID {keep_voice_id_str} not found in measure {measure.number}, using index-based fallback")
                else:
                    warnings.append(f"Target voice {keep_voice_id_str} not found in measure {measure.number}")
                    continue
            elif target_voice is None:
                warnings.append(f"Target voice {keep_voice_id_str} not found in measure {measure.number}")
                continue
            
            # Remove all other voices
            voices_to_remove = []
            for voice in voices:
                if voice != target_voice:
                    voices_to_remove.append(voice)
                    voices_removed.append(f"Voice {voice.id}")
                    elements_removed += len(voice.notes)
                else:
                    elements_preserved += len(voice.notes)
            
            # Use music21's proper voice management instead of direct manipulation
            for voice in voices_to_remove:
                # Properly handle voice relationships and activeSite connections
                if voice.activeSite == measure:
                    # Use music21's voice management to safely remove
                    voice.activeSite = None
                measure.remove(voice)
            
            # If we have a target voice, move its contents to the measure level
            # using music21's proper element management
            if target_voice:
                self._flatten_voice_to_measure(measure, target_voice)
        
        return {
            'voices_removed': voices_removed,
            'elements_preserved': elements_preserved,
            'elements_removed': elements_removed,
            'warnings': warnings
        }
    
    def _flatten_voice_to_measure(self, measure: music21.stream.Measure,
                                voice: music21.stream.Voice):
        """Move voice contents to measure level using music21's proper element management."""
        # Use music21's proper element management for moving contents
        elements_to_move = []
        
        # Collect elements with their offsets, preserving music21 relationships
        # Use voice.elements to get all elements, or specify a class filter
        for element in voice.elements:
            if hasattr(element, 'offset') and element.offset is not None:
                elements_to_move.append((element.offset, element))
        
        # Remove the voice container properly
        if voice.activeSite == measure:
            voice.activeSite = None
        measure.remove(voice)
        
        # Add elements to measure using music21's insert method
        for offset, element in elements_to_move:
            # Clear the element's previous activeSite relationship
            if hasattr(element, 'activeSite'):
                element.activeSite = None
            measure.insert(offset, element)
    
    def _remove_empty_parts(self, score: music21.stream.Score):
        """Remove parts that have no musical content."""
        parts_to_remove = []
        
        for part in score.parts:
            if self._is_part_empty(part):
                parts_to_remove.append(part)
        
        for part in parts_to_remove:
            score.remove(part)
    
    def _is_part_empty(self, part: music21.stream.Part) -> bool:
        """Check if a part is empty of musical content."""
        # Check for notes, rests, or other musical elements
        notes = part.flatten().notes
        return len(notes) == 0
    
    def _clean_empty_measures(self, score: music21.stream.Score):
        """Clean up measures that become empty after voice removal."""
        for part in score.parts:
            measures_to_process = []
            
            for measure in part.getElementsByClass(music21.stream.Measure):
                if self._is_measure_empty(measure):
                    measures_to_process.append(measure)
            
            # Add rests to empty measures to maintain timing
            for measure in measures_to_process:
                self._fill_empty_measure_with_rest(measure)
    
    def _is_measure_empty(self, measure: music21.stream.Measure) -> bool:
        """Check if a measure is empty of musical content."""
        # Check for notes or rests
        notes_and_rests = measure.notesAndRests
        return len(notes_and_rests) == 0
    
    def _fill_empty_measure_with_rest(self, measure: music21.stream.Measure):
        """Fill an empty measure with an appropriate rest."""
        # Get the time signature to determine rest duration
        time_sig = measure.timeSignature
        if not time_sig:
            # Look for time signature in the score
            time_sig = measure.getContextByClass(music21.meter.TimeSignature)
        
        if time_sig:
            # Create a rest for the full measure
            rest_duration = time_sig.numerator / time_sig.denominator * 4  # Convert to quarter note units
            rest = music21.note.Rest(quarterLength=rest_duration)
            measure.insert(0, rest)
        else:
            # Default to whole rest
            rest = music21.note.Rest(quarterLength=4.0)
            measure.insert(0, rest)
    