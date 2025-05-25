"""
Spanner Processing Module for SATB Voice Separation.

This module handles the sophisticated processing of musical spanners after voice separation,
including filtering, copying, reference repair, and validation.
"""

import copy
import music21
from typing import Dict, List, Optional, Any, Tuple
from .spanner_analyzer import SpannerAnalyzer, SpannerMetadata, SpannerComplexity, SpannerType


class SpannerReferenceRepairer:
    """
    Repairs broken spanner note references after voice separation.
    
    Uses multiple strategies to find equivalent notes when original
    references become invalid due to voice removal.
    """
    
    def __init__(self):
        """Initialize the reference repairer."""
        pass
    
    def repair_spanner_references(self, spanner: Any, voice_notes: List[Any], 
                                strategy: str = "contextual") -> bool:
        """
        Repair all note references in a spanner.
        
        Args:
            spanner: The spanner to repair
            voice_notes: List of valid notes in the target voice
            strategy: Repair strategy to use
            
        Returns:
            True if repair was successful, False otherwise
        """
        try:
            if strategy == "basic":
                return self._repair_basic(spanner, voice_notes)
            elif strategy == "contextual":
                return self._repair_contextual(spanner, voice_notes)
            elif strategy == "selective":
                return self._repair_selective(spanner, voice_notes)
            elif strategy == "duplicate":
                return self._repair_duplicate(spanner, voice_notes)
            else:  # fallback
                return self._repair_fallback(spanner, voice_notes)
        except Exception:
            return False
    
    def _repair_basic(self, spanner: Any, voice_notes: List[Any]) -> bool:
        """Basic repair strategy for simple single-voice spanners."""
        try:
            # Handle single note references
            if hasattr(spanner, 'note') and spanner.note:
                equivalent = self._find_equivalent_note(spanner.note, voice_notes)
                if equivalent:
                    spanner.note = equivalent
                    return True
                else:
                    return False
            
            # Handle start/end note references
            success = True
            if hasattr(spanner, 'noteStart') and spanner.noteStart:
                equivalent = self._find_equivalent_note(spanner.noteStart, voice_notes)
                if equivalent:
                    spanner.noteStart = equivalent
                else:
                    success = False
            
            if hasattr(spanner, 'noteEnd') and spanner.noteEnd:
                equivalent = self._find_equivalent_note(spanner.noteEnd, voice_notes)
                if equivalent:
                    spanner.noteEnd = equivalent
                else:
                    success = False
            
            return success
        except Exception:
            return False
    
    def _repair_contextual(self, spanner: Any, voice_notes: List[Any]) -> bool:
        """Contextual repair strategy for complex single-voice spanners."""
        try:
            # Get spanned elements for analysis
            if not hasattr(spanner, 'getSpannedElements'):
                return self._repair_basic(spanner, voice_notes)
            
            spanned_elements = spanner.getSpannedElements()
            if not spanned_elements:
                return self._repair_basic(spanner, voice_notes)
            
            # Repair each spanned element with contextual awareness
            repaired_elements = []
            for element in spanned_elements:
                if hasattr(element, 'pitch'):
                    equivalent = self._find_equivalent_note_contextual(element, voice_notes, repaired_elements)
                    if equivalent:
                        repaired_elements.append(equivalent)
                    else:
                        # If we can't repair all elements, try fallback
                        return self._repair_fallback(spanner, voice_notes)
            
            # Update spanner references
            return self._update_spanner_with_repaired_elements(spanner, spanned_elements, repaired_elements)
        except Exception:
            return self._repair_fallback(spanner, voice_notes)
    
    def _repair_selective(self, spanner: Any, voice_notes: List[Any]) -> bool:
        """Selective repair strategy for cross-voice spanners."""
        try:
            # For cross-voice spanners, only keep notes that exist in this voice
            if not hasattr(spanner, 'getSpannedElements'):
                return self._repair_basic(spanner, voice_notes)
            
            spanned_elements = spanner.getSpannedElements()
            voice_note_set = set(voice_notes)
            
            # Find which spanned elements exist in this voice
            relevant_elements = [elem for elem in spanned_elements if elem in voice_note_set]
            
            if not relevant_elements:
                # No relevant elements in this voice - spanner should be skipped
                return False
            
            # Update spanner to only reference relevant elements
            if len(relevant_elements) == 1:
                # Single element - convert to simple spanner
                if hasattr(spanner, 'noteStart'):
                    spanner.noteStart = relevant_elements[0]
                if hasattr(spanner, 'noteEnd'):
                    spanner.noteEnd = relevant_elements[0]
                if hasattr(spanner, 'note'):
                    spanner.note = relevant_elements[0]
                return True
            else:
                # Multiple elements - update start/end
                if hasattr(spanner, 'noteStart'):
                    spanner.noteStart = relevant_elements[0]
                if hasattr(spanner, 'noteEnd'):
                    spanner.noteEnd = relevant_elements[-1]
                return True
        except Exception:
            return False
    
    def _repair_duplicate(self, spanner: Any, voice_notes: List[Any]) -> bool:
        """Duplicate repair strategy for structural spanners."""
        # For structural spanners, we usually want to copy them as-is
        # or attach them to the first available note
        try:
            if voice_notes and hasattr(spanner, 'note'):
                spanner.note = voice_notes[0]
                return True
            return True  # Structural spanners often don't need note references
        except Exception:
            return False
    
    def _repair_fallback(self, spanner: Any, voice_notes: List[Any]) -> bool:
        """Fallback repair strategy when others fail."""
        try:
            # Try to attach spanner to first and last notes in voice
            if not voice_notes:
                return False
            
            if hasattr(spanner, 'noteStart'):
                spanner.noteStart = voice_notes[0]
            if hasattr(spanner, 'noteEnd'):
                spanner.noteEnd = voice_notes[-1] if len(voice_notes) > 1 else voice_notes[0]
            if hasattr(spanner, 'note'):
                spanner.note = voice_notes[0]
            
            return True
        except Exception:
            return False
    
    def _find_equivalent_note(self, target_note: Any, voice_notes: List[Any]) -> Optional[Any]:
        """Find equivalent note using exact matching strategy."""
        if not target_note or not hasattr(target_note, 'pitch'):
            return None
        
        target_pitch = target_note.pitch
        
        # Strategy 1: Exact object match (rare but possible)
        if target_note in voice_notes:
            return target_note
        
        # Strategy 2: Exact pitch and timing match
        target_offset = getattr(target_note, 'offset', None)
        target_measure = self._get_note_measure_number(target_note)
        
        for note in voice_notes:
            if (note.pitch.name == target_pitch.name and 
                note.pitch.octave == target_pitch.octave):
                
                # Check measure match
                note_measure = self._get_note_measure_number(note)
                if target_measure is not None and note_measure is not None:
                    if target_measure == note_measure:
                        # Check offset match
                        if target_offset is not None:
                            note_offset = getattr(note, 'offset', None)
                            if note_offset is not None and abs(note_offset - target_offset) < 0.1:
                                return note
                        else:
                            return note
        
        # Strategy 3: Pitch match only
        for note in voice_notes:
            if (note.pitch.name == target_pitch.name and 
                note.pitch.octave == target_pitch.octave):
                return note
        
        return None
    
    def _find_equivalent_note_contextual(self, target_note: Any, voice_notes: List[Any], 
                                       already_matched: List[Any]) -> Optional[Any]:
        """Find equivalent note with contextual awareness of already matched notes."""
        candidates = []
        
        # First try exact matching
        exact_match = self._find_equivalent_note(target_note, voice_notes)
        if exact_match and exact_match not in already_matched:
            return exact_match
        
        # If exact match was already used, find best alternative
        if not target_note or not hasattr(target_note, 'pitch'):
            return None
        
        target_pitch = target_note.pitch
        
        for note in voice_notes:
            if note in already_matched:
                continue
                
            if (note.pitch.name == target_pitch.name and 
                note.pitch.octave == target_pitch.octave):
                candidates.append(note)
        
        # Return first available candidate
        return candidates[0] if candidates else None
    
    def _update_spanner_with_repaired_elements(self, spanner: Any, original_elements: List[Any], 
                                             repaired_elements: List[Any]) -> bool:
        """Update spanner references with repaired elements."""
        try:
            if len(original_elements) != len(repaired_elements):
                return False
            
            # Map original to repaired elements
            element_map = dict(zip(original_elements, repaired_elements))
            
            # Update direct references
            if hasattr(spanner, 'noteStart') and spanner.noteStart in element_map:
                spanner.noteStart = element_map[spanner.noteStart]
            
            if hasattr(spanner, 'noteEnd') and spanner.noteEnd in element_map:
                spanner.noteEnd = element_map[spanner.noteEnd]
            
            if hasattr(spanner, 'note') and spanner.note in element_map:
                spanner.note = element_map[spanner.note]
            
            return True
        except Exception:
            return False
    
    def _get_note_measure_number(self, note: Any) -> Optional[int]:
        """Get the measure number for a note."""
        try:
            if hasattr(note, 'activeSite') and note.activeSite:
                if hasattr(note.activeSite, 'number'):
                    return note.activeSite.number
        except Exception:
            pass
        return None


class SpannerProcessor:
    """
    Main processor for handling spanners after voice separation.
    
    Coordinates the analysis, filtering, copying, and repair of spanners
    to ensure they remain valid and musically meaningful in separated voices.
    """
    
    def __init__(self):
        """Initialize the spanner processor."""
        self.analyzer = SpannerAnalyzer()
        self.repairer = SpannerReferenceRepairer()
    
    def process_spanners_post_separation(self, voice_scores: Dict[str, Any], 
                                       original_spanners: List[Any]) -> Dict[str, Any]:
        """
        Main entry point for post-separation spanner processing.
        
        Args:
            voice_scores: Dict of voice_name -> score with separated voices
            original_spanners: List of spanners from the original score
            
        Returns:
            Dict with processing results and statistics
        """
        processing_results = {
            'success': True,
            'voice_results': {},
            'total_spanners_processed': len(original_spanners),
            'total_spanners_preserved': 0,
            'warnings': [],
            'errors': []
        }
        
        try:
            # Extract voice notes for analysis
            all_voice_notes = {}
            for voice_name, voice_score in voice_scores.items():
                all_voice_notes[voice_name] = self._extract_voice_notes(voice_score)
            
            # Analyze all spanners with voice note context
            print(f"Analyzing {len(original_spanners)} spanners for voice relevance...")
            spanner_metadata = self.analyzer.batch_analyze_spanners(original_spanners, all_voice_notes)
            
            # Process each voice
            for voice_name, voice_score in voice_scores.items():
                voice_result = self._process_voice_spanners(
                    voice_name, voice_score, spanner_metadata)
                processing_results['voice_results'][voice_name] = voice_result
                processing_results['total_spanners_preserved'] += voice_result['spanners_preserved']
                processing_results['warnings'].extend(voice_result['warnings'])
                processing_results['errors'].extend(voice_result['errors'])
            
            # Calculate success rate
            total_expected = len(original_spanners) * len(voice_scores)  # Upper bound
            total_preserved = processing_results['total_spanners_preserved']
            preservation_rate = (total_preserved / total_expected * 100) if total_expected > 0 else 0
            
            print(f"Spanner processing complete: {total_preserved} spanners preserved "
                  f"({preservation_rate:.1f}% preservation rate)")
            
        except Exception as e:
            processing_results['success'] = False
            processing_results['errors'].append(f"Spanner processing failed: {e}")
        
        return processing_results
    
    def _process_voice_spanners(self, voice_name: str, voice_score: Any, 
                               spanner_metadata: List[SpannerMetadata]) -> Dict[str, Any]:
        """Process spanners for a specific voice."""
        result = {
            'voice_name': voice_name,
            'spanners_analyzed': len(spanner_metadata),
            'spanners_relevant': 0,
            'spanners_preserved': 0,
            'spanners_failed': 0,
            'warnings': [],
            'errors': []
        }
        
        try:
            # Get voice notes for reference repair
            voice_notes = self._extract_voice_notes(voice_score)
            
            # Filter relevant spanners for this voice
            relevant_spanners = self.analyzer.filter_spanners_for_voice(spanner_metadata, voice_name)
            result['spanners_relevant'] = len(relevant_spanners)
            
            print(f"  {voice_name}: {len(relevant_spanners)} relevant spanners (of {len(spanner_metadata)} total)")
            
            # Process each relevant spanner
            for metadata in relevant_spanners:
                success = self._process_single_spanner(metadata, voice_score, voice_notes)
                if success:
                    result['spanners_preserved'] += 1
                else:
                    result['spanners_failed'] += 1
                    result['warnings'].append(f"Failed to preserve spanner in {voice_name}: {metadata.spanner}")
            
        except Exception as e:
            result['errors'].append(f"Voice spanner processing failed for {voice_name}: {e}")
        
        return result
    
    def _process_single_spanner(self, metadata: SpannerMetadata, voice_score: Any, 
                               voice_notes: List[Any]) -> bool:
        """Process a single spanner for a voice."""
        try:
            # Clone the spanner
            spanner_copy = copy.deepcopy(metadata.spanner)
            
            # Repair references
            repair_success = self.repairer.repair_spanner_references(
                spanner_copy, voice_notes, metadata.repair_strategy)
            
            if repair_success:
                # Add spanner to voice score
                self._add_spanner_to_voice_score(spanner_copy, voice_score)
                return True
            else:
                return False
                
        except Exception:
            return False
    
    def _extract_voice_notes(self, voice_score: Any) -> List[Any]:
        """Extract all notes from a voice score."""
        notes = []
        try:
            for part in voice_score.parts:
                for measure in part.getElementsByClass('Measure'):
                    for note in measure.flatten().notes:
                        notes.append(note)
        except Exception:
            pass
        return notes
    
    def _add_spanner_to_voice_score(self, spanner: Any, voice_score: Any) -> None:
        """Add a spanner to the appropriate part in the voice score."""
        try:
            # Add to the first part (there should only be one after simplification)
            if voice_score.parts:
                voice_score.parts[0].append(spanner)
        except Exception:
            pass
    
    def extract_all_spanners_from_score(self, score: Any) -> List[Any]:
        """Extract all spanners from a complete score."""
        spanners = []
        try:
            for part in score.parts:
                part_spanners = part.getElementsByClass('Spanner')
                spanners.extend(part_spanners)
        except Exception:
            pass
        return spanners