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
        self.removal_stats = {}
        
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
            
            # Find the voice to keep
            target_voice = None
            for voice in voices:
                if str(voice.id) == keep_voice_id:
                    target_voice = voice
                    break
            
            if target_voice is None:
                # Target voice not found in this measure, try to find by index
                if len(voices) > int(keep_voice_id) - 1:
                    target_voice = voices[int(keep_voice_id) - 1]
                else:
                    warnings.append(f"Target voice {keep_voice_id} not found in measure {measure.number}")
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
            
            # Actually remove the voices
            for voice in voices_to_remove:
                measure.remove(voice)
            
            # If we have a target voice, move its contents to the measure level
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
        """Move voice contents to measure level and remove the voice container."""
        # Copy all elements from voice to measure
        elements_to_copy = []
        for element in voice:
            elements_to_copy.append(element)
        
        # Remove the voice
        measure.remove(voice)
        
        # Add elements directly to measure
        for element in elements_to_copy:
            measure.insert(element.offset, element)
    
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
    
    def preserve_non_voice_elements(self, measure: music21.stream.Measure):
        """Ensure non-voice elements are preserved during removal."""
        # This method ensures that dynamics, lyrics, spanners, and other
        # non-voice elements are preserved. In the copy-and-remove approach,
        # these are automatically preserved since we start with complete copies.
        
        # Get all non-voice elements
        non_voice_elements = []
        for element in measure:
            if not isinstance(element, (music21.stream.Voice, music21.note.Note, 
                                      music21.note.Rest, music21.chord.Chord)):
                non_voice_elements.append(element)
        
        # These elements are already preserved in the copy, so no action needed
        # This method serves as a validation point
        return len(non_voice_elements)
    
    def get_removal_statistics(self) -> dict:
        """Get detailed statistics about last removal operation."""
        return self.removal_stats.copy()
    
    def preview_removal(self, score: music21.stream.Score, 
                       keep_voice: VoiceLocation) -> dict:
        """
        Preview what would be removed without actually removing.
        
        Args:
            score: Score to analyze
            keep_voice: Voice to preserve
            
        Returns:
            Dictionary with preview information
        """
        voices_to_remove = []
        elements_to_preserve = 0
        elements_to_remove = 0
        potential_issues = []
        
        # Analyze each part
        for part_idx, part in enumerate(score.parts):
            if part_idx == keep_voice.part_index:
                # Analyze voices in target part
                for measure in part.getElementsByClass(music21.stream.Measure):
                    voices = list(measure.voices)
                    if voices:
                        for voice in voices:
                            if str(voice.id) == keep_voice.voice_id:
                                elements_to_preserve += len(voice.notes)
                            else:
                                voices_to_remove.append(f"Part {part_idx}, Voice {voice.id}")
                                elements_to_remove += len(voice.notes)
                    else:
                        # No explicit voices
                        elements_to_preserve += len(measure.notes)
            else:
                # Entire part will be removed
                note_count = len(part.flatten().notes)
                elements_to_remove += note_count
                voices_to_remove.append(f"Part {part_idx} (entire part)")
        
        # Check for potential issues
        if elements_to_preserve == 0:
            potential_issues.append("No elements will be preserved - target voice may not exist")
        
        return {
            'voices_to_remove': voices_to_remove,
            'elements_to_preserve': elements_to_preserve,
            'elements_to_remove': elements_to_remove,
            'potential_issues': potential_issues
        }