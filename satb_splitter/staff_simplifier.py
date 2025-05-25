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
            elements_merged = len(merged_part.flatten().notes)
            
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
            
            # Remove existing clefs
            existing_clefs = part.getElementsByClass(music21.clef.Clef)
            for clef in existing_clefs:
                part.remove(clef)
            
            # Add new clef at the beginning
            part.insert(0, new_clef)
            
            # Also set clef in first measure if it exists
            measures = part.getElementsByClass(music21.stream.Measure)
            if measures:
                first_measure = measures[0]
                # Remove existing clefs from first measure
                measure_clefs = first_measure.getElementsByClass(music21.clef.Clef)
                for clef in measure_clefs:
                    first_measure.remove(clef)
                # Add new clef
                first_measure.insert(0, new_clef)
    
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
        """Handle elements that span multiple staves."""
        # In the copy-and-remove approach, cross-staff elements are automatically
        # handled because we start with complete copies. Elements that span
        # multiple staves will be preserved in each copy, and the voice removal
        # process will clean up the parts that don't belong to the target voice.
        
        # This method serves as a placeholder for any special handling that
        # might be needed in the future.
        
        return score