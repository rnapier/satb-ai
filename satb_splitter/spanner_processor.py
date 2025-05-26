"""
Spanner Processing Module for SATB Voice Separation.

This module handles the sophisticated processing of musical spanners after voice separation,
including filtering, copying, reference repair, and validation.
"""

import copy
import music21
from music21.spanner import Slur
from music21.expressions import TextExpression
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
                                       original_spanners_with_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main entry point for post-separation spanner processing.
        
        Args:
            voice_scores: Dict of voice_name -> score with separated voices
            original_spanners_with_context: List of spanner context dicts from original score
            
        Returns:
            Dict with processing results and statistics
        """
        processing_results = {
            'success': True,
            'voice_results': {},
            'total_spanners_processed': len(original_spanners_with_context),
            'total_spanners_preserved': 0,
            'warnings': [],
            'errors': []
        }
        
        try:
            # Extract voice notes for analysis
            all_voice_notes = {}
            for voice_name, voice_score in voice_scores.items():
                all_voice_notes[voice_name] = self._extract_voice_notes(voice_score)
            
            print(f"Processing {len(original_spanners_with_context)} spanners with voice context...")
            
            # Process each voice using voice-aware spanner filtering
            for voice_name, voice_score in voice_scores.items():
                voice_result = self._process_voice_spanners_with_context(
                    voice_name, voice_score, original_spanners_with_context)
                processing_results['voice_results'][voice_name] = voice_result
                processing_results['total_spanners_preserved'] += voice_result['spanners_preserved']
                processing_results['warnings'].extend(voice_result['warnings'])
                processing_results['errors'].extend(voice_result['errors'])
            
            # Calculate success rate
            total_expected = len(original_spanners_with_context)  # More realistic expectation
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
    
    def _process_voice_spanners_with_context(self, voice_name: str, voice_score: Any,
                                           spanners_with_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process spanners for a specific voice using voice context information."""
        result = {
            'voice_name': voice_name,
            'spanners_analyzed': len(spanners_with_context),
            'spanners_relevant': 0,
            'spanners_preserved': 0,
            'spanners_failed': 0,
            'warnings': [],
            'errors': []
        }
        
        try:
            # Get voice notes for reference repair
            voice_notes = self._extract_voice_notes(voice_score)
            
            # Map voice names to music21 voice IDs based on our voice identification
            voice_id_mapping = self._get_voice_id_mapping_for_voice(voice_name)
            
            # Filter spanners that belong to this voice
            relevant_spanners = []
            for spanner_context in spanners_with_context:
                if self._spanner_belongs_to_voice(spanner_context, voice_name, voice_id_mapping):
                    relevant_spanners.append(spanner_context['spanner'])
            
            result['spanners_relevant'] = len(relevant_spanners)
            print(f"  {voice_name}: {len(relevant_spanners)} relevant spanners (direct voice matching)")
            
            # Process each relevant spanner
            for spanner in relevant_spanners:
                success = self._process_single_spanner_simple(spanner, voice_score, voice_notes)
                if success:
                    result['spanners_preserved'] += 1
                else:
                    result['spanners_failed'] += 1
                    result['warnings'].append(f"Failed to preserve spanner in {voice_name}: {spanner}")
            
        except Exception as e:
            result['errors'].append(f"Voice spanner processing failed for {voice_name}: {e}")
        
        return result
    
    def _get_voice_id_mapping_for_voice(self, voice_name: str) -> List[str]:
        """Get the music21 voice IDs that correspond to a voice name."""
        # Based on the deterministic voice identification we saw in the logs:
        # Soprano: Part 0, Voice 1
        # Alto: Part 0, Voice 2
        # Tenor: Part 1, Voice 5
        # Bass: Part 1, Voice 6
        
        voice_mapping = {
            'Soprano': ['1'],
            'Alto': ['2'],
            'Tenor': ['5'],
            'Bass': ['6']
        }
        
        return voice_mapping.get(voice_name, [])
    
    def _spanner_belongs_to_voice(self, spanner_context: Dict[str, Any],
                                 voice_name: str, voice_id_mapping: List[str]) -> bool:
        """Determine if a spanner belongs to a specific voice."""
        spanner_voice_ids = spanner_context.get('voice_ids', [])
        
        # If no voice context found, fall back to part-based assignment
        if not spanner_voice_ids:
            part_index = spanner_context.get('part_index', -1)
            if voice_name in ['Soprano', 'Alto'] and part_index == 0:
                return True
            elif voice_name in ['Tenor', 'Bass'] and part_index == 1:
                return True
            return False
        
        # Check for voice ID overlap
        voice_matches = []
        for voice_id in voice_id_mapping:
            if voice_id in spanner_voice_ids:
                voice_matches.append(voice_id)
        
        if not voice_matches:
            return False
        
        # Handle cross-voice spanners: assign to the PRIMARY voice only
        # (the first voice in the spanner's voice list to avoid duplication)
        if len(spanner_voice_ids) > 1:
            # This is a cross-voice spanner, assign to primary voice only
            primary_voice_id = self._get_primary_voice_id(spanner_voice_ids)
            return primary_voice_id in voice_id_mapping
        else:
            # Single-voice spanner, normal assignment
            return True
    
    def _get_primary_voice_id(self, voice_ids: List[str]) -> str:
        """Get the primary voice ID for cross-voice spanners."""
        # Filter out non-string IDs (memory addresses) and keep only voice ID strings
        string_voice_ids = [vid for vid in voice_ids if isinstance(vid, str) and vid.isdigit()]
        
        if not string_voice_ids:
            return voice_ids[0] if voice_ids else None
        
        # Assign to the lowest numbered voice (primary voice)
        # This prevents duplication while maintaining musical logic
        return min(string_voice_ids, key=int)
    
    def _process_single_spanner_simple(self, spanner: Any, voice_score: Any,
                                     voice_notes: List[Any]) -> bool:
        """Process a single spanner with simplified logic."""
        try:
            # Clone the spanner
            spanner_copy = copy.deepcopy(spanner)
            
            # Repair references using basic strategy (since we know this spanner belongs to this voice)
            repair_success = self.repairer.repair_spanner_references(
                spanner_copy, voice_notes, "basic")
            
            if repair_success:
                # Add spanner to voice score
                self._add_spanner_to_voice_score(spanner_copy, voice_score)
                return True
            else:
                return False
                
        except Exception:
            return False
    
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
        """Add a spanner to the appropriate part in the voice score with proper note association."""
        try:
            if not voice_score.parts:
                return
                
            part = voice_score.parts[0]
            
            # For slurs, we need to ensure they're properly associated with notes
            if hasattr(spanner, 'classes') and 'Slur' in spanner.classes:
                self._add_slur_to_notes(spanner, part)
            else:
                # For other spanners (dynamics, etc.), append to part
                part.append(spanner)
                
        except Exception as e:
            print(f"Warning: Failed to add spanner to voice score: {e}")
    
    def _add_slur_to_notes(self, slur: Any, part: Any) -> None:
        """Add slur markings to the appropriate notes in the part."""
        try:
            # Get spanned elements (music21 uses this for slurs)
            spanned_elements = []
            if hasattr(slur, 'getSpannedElements'):
                spanned_elements = slur.getSpannedElements()
            elif hasattr(slur, 'noteStart') and hasattr(slur, 'noteEnd'):
                # Fallback to direct attributes
                spanned_elements = [slur.noteStart, slur.noteEnd]
            
            if len(spanned_elements) >= 2:
                start_note = spanned_elements[0]
                end_note = spanned_elements[-1]
                
                # Find equivalent notes in the part
                part_notes = []
                for measure in part.getElementsByClass('Measure'):
                    for note in measure.flatten().notes:
                        part_notes.append(note)
                
                # Find matching start and end notes
                start_match = self._find_matching_note_in_part(start_note, part_notes)
                end_match = self._find_matching_note_in_part(end_note, part_notes)
                
                if start_match and end_match:
                    # Create a new slur spanning the matched notes
                    new_slur = Slur()
                    new_slur.addSpannedElements([start_match, end_match])
                    
                    # Add the slur to the part
                    part.append(new_slur)
                    
                else:
                    # Fallback: add slur to part
                    part.append(slur)
            else:
                # Fallback: add slur to part
                part.append(slur)
                
        except Exception as e:
            # Fallback: add slur to part
            try:
                part.append(slur)
            except:
                pass
    
    def _find_matching_note_in_part(self, target_note: Any, part_notes: List[Any]) -> Any:
        """Find a matching note in the part notes."""
        if not target_note or not hasattr(target_note, 'pitch'):
            return None
            
        target_pitch = target_note.pitch
        
        # Look for exact pitch match
        for note in part_notes:
            if (hasattr(note, 'pitch') and
                note.pitch.name == target_pitch.name and
                note.pitch.octave == target_pitch.octave):
                return note
        
        return None
    
    def extract_all_spanners_from_score(self, score: Any) -> List[Dict[str, Any]]:
        """Extract all spanners from a complete score with voice context."""
        spanners_with_context = []
        try:
            for part_idx, part in enumerate(score.parts):
                part_spanners = part.getElementsByClass('Spanner')
                for spanner in part_spanners:
                    spanner_context = {
                        'spanner': spanner,
                        'part_index': part_idx,
                        'voice_ids': self._extract_spanner_voice_context(spanner)
                    }
                    spanners_with_context.append(spanner_context)
        except Exception:
            pass
        return spanners_with_context
    
    def _extract_spanner_voice_context(self, spanner: Any) -> List[str]:
        """Extract the voice IDs that a spanner is associated with."""
        voice_ids = set()
        try:
            if hasattr(spanner, 'getSpannedElements'):
                spanned_elements = spanner.getSpannedElements()
                for element in spanned_elements:
                    # Check if element has voice information
                    if hasattr(element, 'getOffsetBySite'):
                        # Get the containing voice/measure
                        for site in element.sites:
                            if hasattr(site, 'id') and site.id:
                                voice_ids.add(site.id)
                    
                    # Also check activeSite for voice information
                    if hasattr(element, 'activeSite') and element.activeSite:
                        if hasattr(element.activeSite, 'id') and element.activeSite.id:
                            voice_ids.add(element.activeSite.id)
        except Exception:
            pass
        
        return list(voice_ids)