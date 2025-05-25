"""
Contextual unification module for applying simplified unification rules.
"""

from typing import Dict, List, Any
import music21
from .utils import ProcessingContext, UnificationResult
from .exceptions import UnificationError


class ContextualUnifier:
    """Applies unification rules using complete score context."""
    
    def __init__(self, context: ProcessingContext):
        """Initialize with processing context."""
        self.context = context
        self.unification_rules = self._load_rules()
    
    def _load_rules(self) -> dict:
        """Load unification rules from processing options."""
        return {
            'dynamics_soprano_to_all': True,
            'dynamics_common_to_all': True,
            'lyrics_fill_gaps': True,
            'lyrics_preserve_voice_specific': True,
            'spanners_system_wide_to_all': True,
            'spanners_preserve_voice_specific': True
        }
    
    def apply_unification_rules(self, voice_scores: Dict[str, music21.stream.Score]) -> UnificationResult:
        """
        Apply all unification rules to voice scores.
        
        Args:
            voice_scores: Dictionary of voice scores (modified in place)
            
        Returns:
            UnificationResult with details of applied rules
            
        Raises:
            UnificationError: If unification fails
        """
        import time
        start_time = time.time()
        
        try:
            rules_applied = []
            dynamics_unified = 0
            lyrics_unified = 0
            spanners_unified = 0
            warnings = []
            errors = []
            
            # Apply dynamics unification
            if self.context.processing_options.apply_dynamics_unification:
                dynamics_result = self.unify_dynamics(voice_scores)
                if dynamics_result['success']:
                    rules_applied.append('dynamics')
                    dynamics_unified = dynamics_result['elements_unified']
                    warnings.extend(dynamics_result.get('warnings', []))
                else:
                    errors.extend(dynamics_result.get('errors', []))
            
            # Apply lyrics unification
            if self.context.processing_options.apply_lyrics_unification:
                lyrics_result = self.unify_lyrics(voice_scores)
                if lyrics_result['success']:
                    rules_applied.append('lyrics')
                    lyrics_unified = lyrics_result['elements_unified']
                    warnings.extend(lyrics_result.get('warnings', []))
                else:
                    errors.extend(lyrics_result.get('errors', []))
            
            # Apply spanner unification
            if self.context.processing_options.apply_spanner_unification:
                spanners_result = self.unify_spanners(voice_scores)
                if spanners_result['success']:
                    rules_applied.append('spanners')
                    spanners_unified = spanners_result['elements_unified']
                    warnings.extend(spanners_result.get('warnings', []))
                else:
                    errors.extend(spanners_result.get('errors', []))
            
            # Apply tempo markings unification
            tempo_result = self.unify_tempo_markings(voice_scores)
            if tempo_result['success']:
                rules_applied.append('tempo_markings')
                warnings.extend(tempo_result.get('warnings', []))
            else:
                errors.extend(tempo_result.get('errors', []))
            
            processing_time = time.time() - start_time
            
            return UnificationResult(
                success=len(errors) == 0,
                rules_applied=rules_applied,
                dynamics_unified=dynamics_unified,
                lyrics_unified=lyrics_unified,
                spanners_unified=spanners_unified,
                warnings=warnings,
                errors=errors,
                processing_time=processing_time
            )
            
        except (AttributeError, ValueError, TypeError) as e:
            raise UnificationError(f"Invalid input data for unification: {e}")
        except music21.exceptions21.Music21Exception as e:
            raise UnificationError(f"Music21 error during unification: {e}")
        except KeyError as e:
            raise UnificationError(f"Missing required data for unification: {e}")
        except Exception as e:
            # Log the unexpected exception for debugging
            import logging
            logging.error(f"Unexpected error in unification: {type(e).__name__}: {e}")
            raise UnificationError(f"Unexpected error during unification: {type(e).__name__}: {e}")
    
    def unify_dynamics(self, voice_scores: Dict[str, music21.stream.Score]) -> dict:
        """Smart dynamics unification based on actual content."""
        try:
            elements_unified = 0
            warnings = []
            
            # Cross-reference dynamics between all voices
            cross_ref = self.cross_reference_elements(voice_scores)
            common_dynamics = cross_ref['common_elements'].get('dynamics', [])
            
            # Rule 1: Apply common dynamics to all voices
            for dynamic_info in common_dynamics:
                self._apply_dynamic_to_all_voices(dynamic_info, voice_scores)
                elements_unified += 1
            
            # Rule 2: Apply Soprano-only dynamics to all voices (traditional rule)
            if 'Soprano' in voice_scores:
                soprano_only_dynamics = self._find_soprano_only_dynamics(voice_scores)
                for dynamic_info in soprano_only_dynamics:
                    self._apply_dynamic_to_all_voices(dynamic_info, voice_scores)
                    elements_unified += 1
            
            return {
                'success': True,
                'elements_unified': elements_unified,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'success': False,
                'elements_unified': 0,
                'errors': [f"Dynamics unification failed: {e}"]
            }
    
    def unify_lyrics(self, voice_scores: Dict[str, music21.stream.Score]) -> dict:
        """Intelligent lyrics distribution."""
        try:
            elements_unified = 0
            warnings = []
            
            # Find positions where some voices have lyrics, others don't
            lyric_gaps = self._find_lyric_gaps(voice_scores)
            
            # Fill gaps with lyrics from other voices
            for gap_info in lyric_gaps:
                if self._fill_lyric_gap(gap_info, voice_scores):
                    elements_unified += 1
            
            return {
                'success': True,
                'elements_unified': elements_unified,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'success': False,
                'elements_unified': 0,
                'errors': [f"Lyrics unification failed: {e}"]
            }
    
    def unify_spanners(self, voice_scores: Dict[str, music21.stream.Score]) -> dict:
        """Context-aware spanner unification."""
        try:
            elements_unified = 0
            warnings = []
            
            # Identify system-wide spanners (tempo, rehearsal marks)
            system_spanners = []  # Placeholder - method was unused/empty
            
            # Apply system spanners to all voices
            for spanner_info in system_spanners:
                # Placeholder - method was unused/empty
                elements_unified += 1
            
            return {
                'success': True,
                'elements_unified': elements_unified,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'success': False,
                'elements_unified': 0,
                'errors': [f"Spanner unification failed: {e}"]
            }
    
    def unify_tempo_markings(self, voice_scores: Dict[str, music21.stream.Score]) -> dict:
        """Tempo and expression markings unification."""
        try:
            warnings = []
            
            # Find tempo markings in any voice
            tempo_markings = self._find_tempo_markings(voice_scores)
            
            # Apply tempo markings to all voices
            for tempo_info in tempo_markings:
                self._apply_tempo_to_all_voices(tempo_info, voice_scores)
            
            return {
                'success': True,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [f"Tempo unification failed: {e}"]
            }
    
    def cross_reference_elements(self, voice_scores: Dict[str, music21.stream.Score]) -> dict:
        """Cross-reference elements between voice scores for analysis."""
        common_elements = {'dynamics': [], 'lyrics': [], 'spanners': []}
        voice_specific_elements = {}
        
        # Analyze each voice for common elements
        for voice_name, score in voice_scores.items():
            voice_specific_elements[voice_name] = []
            
            # Find dynamics
            dynamics = self._extract_dynamics_from_score(score)
            for dynamic in dynamics:
                # Check if this dynamic appears in other voices at the same position
                if self._is_dynamic_common(dynamic, voice_scores, voice_name):
                    if dynamic not in common_elements['dynamics']:
                        common_elements['dynamics'].append(dynamic)
                else:
                    voice_specific_elements[voice_name].append(dynamic)
        
        return {
            'common_elements': common_elements,
            'voice_specific_elements': voice_specific_elements,
            'potential_unifications': []
        }
    
    def _apply_dynamic_to_all_voices(self, dynamic_info: dict, 
                                   voice_scores: Dict[str, music21.stream.Score]):
        """Apply a dynamic marking to all voice scores."""
        for voice_name, score in voice_scores.items():
            # Find the appropriate location in this voice's score
            target_measure = self._find_measure_by_number(score, dynamic_info['measure_number'])
            if target_measure:
                # Check if dynamic already exists at this position
                if not self._dynamic_exists_at_position(target_measure, dynamic_info['offset'], 
                                                      dynamic_info['dynamic']):
                    # Add the dynamic
                    dynamic_obj = music21.dynamics.Dynamic(dynamic_info['dynamic'])
                    target_measure.insert(dynamic_info['offset'], dynamic_obj)
    
    def _find_soprano_only_dynamics(self, voice_scores: Dict[str, music21.stream.Score]) -> List[dict]:
        """Find dynamics that appear only in the Soprano voice."""
        if 'Soprano' not in voice_scores:
            return []
        
        soprano_dynamics = self._extract_dynamics_from_score(voice_scores['Soprano'])
        soprano_only = []
        
        for dynamic in soprano_dynamics:
            # Check if this dynamic appears in other voices
            appears_elsewhere = False
            for voice_name, score in voice_scores.items():
                if voice_name != 'Soprano':
                    if self._dynamic_exists_in_score(score, dynamic):
                        appears_elsewhere = True
                        break
            
            if not appears_elsewhere:
                soprano_only.append(dynamic)
        
        return soprano_only
    
    def _find_lyric_gaps(self, voice_scores: Dict[str, music21.stream.Score]) -> List[dict]:
        """Find positions where some voices have lyrics, others don't."""
        gaps = []
        
        # Get all voice names for analysis
        voice_names = list(voice_scores.keys())
        
        # Analyze each measure across all voices
        for voice_name, score in voice_scores.items():
            for part in score.parts:
                for measure_idx, measure in enumerate(part.getElementsByClass('Measure')):
                    measure_number = measure.number if hasattr(measure, 'number') else measure_idx + 1
                    
                    # Get all notes with lyrics in this measure for this voice
                    notes_with_lyrics = self._get_notes_with_lyrics_in_measure(measure)
                    
                    # For each note with lyrics, check if other voices at same position need the lyric
                    for note_info in notes_with_lyrics:
                        gap_candidates = self._find_matching_notes_without_lyrics(
                            note_info, measure_number, voice_scores, voice_name
                        )
                        
                        for candidate in gap_candidates:
                            gaps.append({
                                'source_voice': voice_name,
                                'target_voice': candidate['voice'],
                                'measure_number': measure_number,
                                'offset': note_info['offset'],
                                'duration': note_info['duration'],
                                'lyric': note_info['lyric'],
                                'target_note': candidate['note']
                            })
        
        return gaps
    
    def _fill_lyric_gap(self, gap_info: dict,
                       voice_scores: Dict[str, music21.stream.Score]) -> bool:
        """Fill a lyric gap by copying lyrics from another voice."""
        try:
            target_note = gap_info['target_note']
            source_lyric = gap_info['lyric']
            
            # Create a copy of the lyric for the target note
            # Use the addLyric method which creates the lyric object properly
            lyric_text = source_lyric.text
            lyric_number = getattr(source_lyric, 'number', 1)
            lyric_syllabic = getattr(source_lyric, 'syllabic', None)
            
            # Add the lyric to the target note
            target_note.addLyric(lyric_text, lyric_number)
            
            # Set syllabic if available
            if lyric_syllabic and target_note.lyrics:
                target_note.lyrics[-1].syllabic = lyric_syllabic
            
            return True
            
        except Exception as e:
            print(f"Warning: Failed to fill lyric gap: {e}")
            return False
    
    def _get_notes_with_lyrics_in_measure(self, measure) -> List[dict]:
        """Extract all notes with lyrics from a measure."""
        notes_with_lyrics = []
        
        for note in measure.getElementsByClass('Note'):
            if note.lyrics:
                # Get the primary lyric (usually number 1)
                primary_lyric = note.lyrics[0] if note.lyrics else None
                if primary_lyric and primary_lyric.text:
                    notes_with_lyrics.append({
                        'note': note,
                        'offset': note.offset,
                        'duration': note.duration.quarterLength,
                        'lyric': primary_lyric
                    })
        
        return notes_with_lyrics
    
    def _find_matching_notes_without_lyrics(self, note_info: dict, measure_number: int,
                                          voice_scores: Dict[str, music21.stream.Score],
                                          source_voice: str) -> List[dict]:
        """Find notes in other voices at same position/duration that don't have lyrics."""
        candidates = []
        
        for voice_name, score in voice_scores.items():
            if voice_name == source_voice:
                continue
                
            # Find the corresponding measure in this voice
            target_measure = self._find_measure_in_score(score, measure_number)
            if not target_measure:
                continue
            
            # Look for notes at the same offset with same duration
            for note in target_measure.getElementsByClass('Note'):
                if (abs(note.offset - note_info['offset']) < 0.01 and  # Same timing (with small tolerance)
                    abs(note.duration.quarterLength - note_info['duration']) < 0.01 and  # Same duration
                    not note.lyrics):  # No existing lyrics
                    
                    candidates.append({
                        'voice': voice_name,
                        'note': note
                    })
        
        return candidates
    
    def _find_measure_in_score(self, score: music21.stream.Score, measure_number: int):
        """Find a specific measure by number in a score."""
        for part in score.parts:
            for measure in part.getElementsByClass('Measure'):
                if hasattr(measure, 'number') and measure.number == measure_number:
                    return measure
                # Fallback for measures without explicit numbers
                elif not hasattr(measure, 'number'):
                    # Assume measures are in order, use index
                    measures = list(part.getElementsByClass('Measure'))
                    if len(measures) >= measure_number:
                        return measures[measure_number - 1]
        return None
    
    def _find_tempo_markings(self, voice_scores: Dict[str, music21.stream.Score]) -> List[dict]:
        """Find tempo markings in any voice."""
        tempo_markings = []
        
        for voice_name, score in voice_scores.items():
            # Find tempo markings
            for element in score.flatten():
                if isinstance(element, (music21.tempo.TempoIndication, 
                                      music21.tempo.MetronomeMark)):
                    tempo_markings.append({
                        'tempo': element,
                        'offset': element.offset,
                        'measure_number': element.measureNumber
                    })
        
        return tempo_markings
    
    def _apply_tempo_to_all_voices(self, tempo_info: dict,
                                 voice_scores: Dict[str, music21.stream.Score]):
        """Apply tempo marking to all voice scores."""
        for voice_name, score in voice_scores.items():
            # Find the appropriate location
            target_measure = self._find_measure_by_number(score, tempo_info['measure_number'])
            if target_measure:
                # Check if tempo marking already exists
                existing_tempos = target_measure.getElementsByClass(
                    (music21.tempo.TempoIndication, music21.tempo.MetronomeMark))
                if not existing_tempos:
                    # Add the tempo marking
                    target_measure.insert(tempo_info['offset'], tempo_info['tempo'])
    
    def _extract_dynamics_from_score(self, score: music21.stream.Score) -> List[dict]:
        """Extract dynamics information from a score."""
        dynamics = []
        
        # Iterate through parts and measures to preserve correct offsets
        for part in score.parts:
            for measure in part.getElementsByClass(music21.stream.Measure):
                for element in measure:
                    if isinstance(element, music21.dynamics.Dynamic):
                        dynamics.append({
                            'dynamic': element.value,
                            'offset': element.offset,
                            'measure_number': measure.number
                        })
        
        return dynamics
    
    def _is_dynamic_common(self, dynamic: dict, voice_scores: Dict[str, music21.stream.Score],
                          exclude_voice: str) -> bool:
        """Check if a dynamic appears in multiple voices."""
        count = 0
        for voice_name, score in voice_scores.items():
            if voice_name != exclude_voice:
                if self._dynamic_exists_in_score(score, dynamic):
                    count += 1
        
        return count > 0
    
    def _dynamic_exists_in_score(self, score: music21.stream.Score, dynamic: dict) -> bool:
        """Check if a dynamic exists in a score at the specified position."""
        target_measure = self._find_measure_by_number(score, dynamic['measure_number'])
        if target_measure:
            return self._dynamic_exists_at_position(target_measure, dynamic['offset'], 
                                                  dynamic['dynamic'])
        return False
    
    def _find_measure_by_number(self, score: music21.stream.Score, 
                              measure_number: int) -> music21.stream.Measure:
        """Find a measure by its number in the score."""
        for part in score.parts:
            for measure in part.getElementsByClass(music21.stream.Measure):
                if measure.number == measure_number:
                    return measure
        return None
    
    def _dynamic_exists_at_position(self, measure: music21.stream.Measure,
                                  offset: float, dynamic_value: str) -> bool:
        """Check if a dynamic exists at a specific position in a measure."""
        dynamics = measure.getElementsByClass(music21.dynamics.Dynamic)
        for dynamic in dynamics:
            if abs(dynamic.offset - offset) < 0.1 and dynamic.value == dynamic_value:
                return True
        return False