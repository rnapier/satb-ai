"""
Staff simplification module for converting multi-staff scores to single-staff layout.
"""

from typing import List
import music21
from .utils import ProcessingContext, SimplificationResult
from .exceptions import StaffSimplificationError


class StaffSimplifier:
    """Converts multi-staff scores to single-staff layout."""
    
    def __init__(self, context: ProcessingContext):
        """Initialize with processing context."""
        self.context = context
        self.clef_mappings = self._init_clef_mappings()
    
    def _init_clef_mappings(self) -> dict:
        """Initialize clef mappings for different voice types."""
        return {
            'soprano': music21.clef.TrebleClef(),
            'alto': music21.clef.TrebleClef(),
            'tenor': music21.clef.BassClef(),  # Could also be treble clef 8va bassa
            'bass': music21.clef.BassClef()
        }
    
    def convert_to_single_staff(self, score: music21.stream.Score, 
                              voice_type: str) -> SimplificationResult:
        """
        Convert score to single staff layout.
        
        Args:
            score: Score to convert (modified in place)
            voice_type: Type of voice (Soprano, Alto, Tenor, Bass)
            
        Returns:
            SimplificationResult with conversion details
            
        Raises:
            StaffSimplificationError: If conversion fails
        """
        try:
            original_staff_count = len(score.parts)
            warnings = []
            errors = []
            elements_merged = 0
            
            if original_staff_count <= 1:
                # Already single staff, just update clef and metadata
                if score.parts:
                    self.set_appropriate_clef(score.parts[0], voice_type)
                    self.update_part_metadata(score.parts[0], voice_type)
                
                return SimplificationResult(
                    success=True,
                    original_staff_count=original_staff_count,
                    final_staff_count=1,
                    clef_assigned=self._get_clef_name(voice_type),
                    elements_merged=0,
                    warnings=warnings,
                    errors=errors
                )
            
            # Merge multiple parts into single part
            merged_part = self.merge_staff_elements(list(score.parts))
            # Cache flattened view for performance
            flattened_part = merged_part.flatten()
            elements_merged = len(flattened_part.notes)
            
            # Replace all parts with the merged part
            # Remove all existing parts
            parts_to_remove = list(score.parts)
            for part in parts_to_remove:
                score.remove(part)
            
            # Add the merged part
            score.append(merged_part)
            
            # Set appropriate clef and metadata
            self.set_appropriate_clef(merged_part, voice_type)
            self.update_part_metadata(merged_part, voice_type)
            
            return SimplificationResult(
                success=True,
                original_staff_count=original_staff_count,
                final_staff_count=1,
                clef_assigned=self._get_clef_name(voice_type),
                elements_merged=elements_merged,
                warnings=warnings,
                errors=errors
            )
            
        except Exception as e:
            raise StaffSimplificationError(f"Staff simplification failed: {e}")
    
    def merge_staff_elements(self, parts: List[music21.stream.Part]) -> music21.stream.Part:
        """
        Merge elements from multiple parts into single part.
        
        Args:
            parts: List of parts to merge
            
        Returns:
            Single merged part
        """
        if not parts:
            return music21.stream.Part()
        
        if len(parts) == 1:
            return parts[0]
        
        # Use the first part as the base
        merged_part = parts[0]
        
        # Merge elements from other parts
        for part in parts[1:]:
            self._merge_part_into_base(merged_part, part)
        
        return merged_part
    
    def _merge_part_into_base(self, base_part: music21.stream.Part, 
                            source_part: music21.stream.Part):
        """Merge elements from source part into base part."""
        # Get all measures from source part
        source_measures = source_part.getElementsByClass(music21.stream.Measure)
        base_measures = base_part.getElementsByClass(music21.stream.Measure)
        
        # Create a mapping of measure numbers
        base_measure_map = {m.number: m for m in base_measures if m.number is not None}
        
        for source_measure in source_measures:
            if source_measure.number is None:
                continue
                
            if source_measure.number in base_measure_map:
                # Merge into existing measure
                base_measure = base_measure_map[source_measure.number]
                self._merge_measure_elements(base_measure, source_measure)
            else:
                # Add new measure
                base_part.append(source_measure)
    
    def _merge_measure_elements(self, base_measure: music21.stream.Measure,
                              source_measure: music21.stream.Measure):
        """Merge elements from source measure into base measure."""
        # Add all elements from source measure to base measure
        for element in source_measure:
            # Skip if it's a voice container (we want the flattened content)
            if isinstance(element, music21.stream.Voice):
                for voice_element in element:
                    base_measure.insert(voice_element.offset, voice_element)
            else:
                base_measure.insert(element.offset, element)
    
    def set_appropriate_clef(self, part: music21.stream.Part, voice_type: str):
        """Set clef appropriate for voice type."""
        voice_type_lower = voice_type.lower()
        
        if voice_type_lower in self.clef_mappings:
            new_clef = self.clef_mappings[voice_type_lower]
            
            # Use music21's proper clef management instead of manual manipulation
            part.clef = new_clef
            
            # Ensure clef is properly set at the beginning of the part
            # music21 handles clef placement and management automatically
            # but we may need to ensure it's at offset 0
            if hasattr(part, 'getElementsByClass'):
                measures = part.getElementsByClass(music21.stream.Measure)
                if measures:
                    # Let music21 handle clef placement in measures automatically
                    # The part.clef setter manages this properly
                    pass
    
    def update_part_metadata(self, part: music21.stream.Part, voice_type: str):
        """Update part name and other metadata."""
        # Set part name
        part.partName = voice_type
        
        # Set instrument name if not already set
        if not hasattr(part, 'instrumentName') or not part.instrumentName:
            part.instrumentName = voice_type
        
        # Update any existing instrument objects
        instruments = part.getElementsByClass(music21.instrument.Instrument)
        for instrument in instruments:
            instrument.instrumentName = voice_type
    
    def get_appropriate_clef(self, voice_type: str) -> music21.clef.Clef:
        """
        Get appropriate clef for voice type.
        
        Args:
            voice_type: Voice type name
            
        Returns:
            Appropriate clef object
        """
        voice_type_lower = voice_type.lower()
        if voice_type_lower in self.clef_mappings:
            return self.clef_mappings[voice_type_lower]
        else:
            # Default to treble clef
            return music21.clef.TrebleClef()
    
    def _get_clef_name(self, voice_type: str) -> str:
        """Get the name of the clef for a voice type."""
        clef = self.get_appropriate_clef(voice_type)
        if isinstance(clef, music21.clef.TrebleClef):
            return 'treble'
        elif isinstance(clef, music21.clef.BassClef):
            return 'bass'
        elif isinstance(clef, music21.clef.AltoClef):
            return 'alto'
        else:
            return str(clef)
    
    def handle_cross_staff_elements(self, score: music21.stream.Score) -> music21.stream.Score:
        """
        Handle cross-staff musical elements like slurs, ties, and beams.
        
        Args:
            score: Score to process for cross-staff elements
            
        Returns:
            Score with cross-staff elements properly handled
        """
        try:
            # Process each part for cross-staff elements
            for part in score.parts:
                self._handle_cross_staff_in_part(part, score)
            
            return score
            
        except Exception as e:
            # Log warning but don't fail - this is enhancement, not critical
            if hasattr(self.context, 'add_warning'):
                self.context.add_warning(f"Cross-staff element handling failed: {e}")
            return score
    
    def _handle_cross_staff_in_part(self, part: music21.stream.Part, full_score: music21.stream.Score):
        """Handle cross-staff elements within a single part."""
        # Find spanner elements that might cross staffs
        spanners = part.getElementsByClass(music21.spanner.Spanner)
        
        for spanner in spanners:
            self._process_cross_staff_spanner(spanner, part, full_score)
        
        # Handle ties and slurs that might reference other staffs
        measures = part.getElementsByClass(music21.stream.Measure)
        for measure in measures:
            self._process_cross_staff_in_measure(measure, part, full_score)
    
    def _process_cross_staff_spanner(self, spanner: music21.spanner.Spanner,
                                   current_part: music21.stream.Part,
                                   full_score: music21.stream.Score):
        """Process a spanner that might cross staff boundaries."""
        try:
            # Check if spanner references notes in other parts
            spanned_notes = list(spanner)
            parts_referenced = set()
            
            for note in spanned_notes:
                # Find which part this note belongs to
                for part_index, part in enumerate(full_score.parts):
                    if note in part.flatten().notes:
                        parts_referenced.add(part_index)
            
            # If spanner crosses multiple parts, consolidate to current part
            if len(parts_referenced) > 1:
                self._consolidate_cross_staff_spanner(spanner, current_part, spanned_notes)
                
        except Exception:
            # If we can't process the spanner, leave it as-is
            pass
    
    def _consolidate_cross_staff_spanner(self, spanner: music21.spanner.Spanner,
                                       target_part: music21.stream.Part,
                                       spanned_notes: list):
        """Consolidate a cross-staff spanner to a single part."""
        try:
            # Find notes in the target part that correspond to the spanned notes
            target_notes = []
            flattened_part = target_part.flatten()
            
            for original_note in spanned_notes:
                # Find closest note by offset and pitch
                closest_note = self._find_closest_note(original_note, flattened_part.notes)
                if closest_note:
                    target_notes.append(closest_note)
            
            # If we found corresponding notes, update the spanner
            if target_notes:
                # Remove the old spanner
                if hasattr(spanner, 'activeSite') and spanner.activeSite:
                    spanner.activeSite.remove(spanner)
                
                # Create new spanner with target notes
                if isinstance(spanner, music21.spanner.Slur):
                    new_spanner = music21.spanner.Slur(target_notes)
                elif isinstance(spanner, music21.spanner.Tie):
                    # For ties, only connect consecutive notes of same pitch
                    if len(target_notes) >= 2:
                        new_spanner = music21.tie.Tie()
                        target_notes[0].tie = new_spanner
                        target_notes[1].tie = new_spanner
                else:
                    # Generic spanner
                    new_spanner = music21.spanner.Spanner(target_notes)
                
                # Add to target part if it's not a tie (ties are handled differently)
                if not isinstance(spanner, music21.spanner.Tie):
                    target_part.insert(0, new_spanner)
                    
        except Exception:
            # If consolidation fails, leave original spanner
            pass
    
    def _process_cross_staff_in_measure(self, measure: music21.stream.Measure,
                                      current_part: music21.stream.Part,
                                      full_score: music21.stream.Score):
        """Process cross-staff elements within a single measure."""
        # Look for notes with ties or slurs that might reference other parts
        for element in measure:
            if isinstance(element, music21.note.Note):
                self._check_note_cross_staff_references(element, current_part, full_score)
            elif isinstance(element, music21.chord.Chord):
                # Check each note in the chord
                for note in element.notes:
                    self._check_note_cross_staff_references(note, current_part, full_score)
    
    def _check_note_cross_staff_references(self, note: music21.note.Note,
                                         current_part: music21.stream.Part,
                                         full_score: music21.stream.Score):
        """Check if a note has cross-staff references and resolve them."""
        # Check for ties that might reference other parts
        if hasattr(note, 'tie') and note.tie:
            self._resolve_cross_staff_tie(note, current_part, full_score)
    
    def _resolve_cross_staff_tie(self, note: music21.note.Note,
                               current_part: music21.stream.Part,
                               full_score: music21.stream.Score):
        """Resolve ties that might reference notes in other parts."""
        try:
            if note.tie.type in ['start', 'continue']:
                # Find the next note of the same pitch in the current part
                flattened_part = current_part.flatten()
                notes_after = [n for n in flattened_part.notes
                             if (hasattr(n, 'offset') and hasattr(note, 'offset') and
                                 n.offset > note.offset and n.pitch == note.pitch)]
                
                if notes_after:
                    # Connect to the next note in the same part
                    next_note = min(notes_after, key=lambda n: n.offset)
                    if not hasattr(next_note, 'tie') or not next_note.tie:
                        next_note.tie = music21.tie.Tie()
                        next_note.tie.type = 'stop'
                        
        except Exception:
            # If tie resolution fails, leave as-is
            pass
    
    def _find_closest_note(self, target_note: music21.note.Note,
                          search_notes: list) -> music21.note.Note:
        """Find the closest note by offset and pitch."""
        if not search_notes or not hasattr(target_note, 'offset'):
            return None
            
        best_match = None
        best_score = float('inf')
        
        for note in search_notes:
            if not hasattr(note, 'offset'):
                continue
                
            # Calculate similarity score (lower is better)
            offset_diff = abs(float(note.offset) - float(target_note.offset))
            
            # Add pitch difference if both notes have pitch
            pitch_diff = 0
            if (hasattr(note, 'pitch') and hasattr(target_note, 'pitch') and
                note.pitch and target_note.pitch):
                pitch_diff = abs(note.pitch.midi - target_note.pitch.midi)
            
            score = offset_diff + (pitch_diff * 0.1)  # Weight offset more than pitch
            
            if score < best_score:
                best_score = score
                best_match = note
        
        return best_match
    