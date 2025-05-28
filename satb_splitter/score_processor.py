"""
Score processor module for orchestrating the SATB splitting pipeline.
"""

import copy
import time
from typing import Dict
import music21
from .utils import ProcessingContext, ProcessingResult, ValidationResult, load_score
from .voice_identifier import VoiceIdentifier
from .voice_remover import VoiceRemover
from .staff_simplifier import StaffSimplifier
from .contextual_unifier import ContextualUnifier
from .exceptions import ProcessingError, InvalidScoreError


class ScoreProcessor:
    """Main orchestrator for SATB splitting process."""
    
    def __init__(self):
        """Initialize the score processor."""
        pass
        
    def process_satb_score(self, input_file: str) -> ProcessingResult:
        """
        Process SATB score through complete pipeline.
        
        Args:
            input_file: Path to input score file
            
        Returns:
            ProcessingResult with voice scores and metadata
            
        Raises:
            ProcessingError: If processing fails at any stage
        """
        start_time = time.time()
        processing_steps = []
        warnings = []
        errors = []
        
        try:
            # Step 1: Load and validate input score
            processing_steps.append("Loading input score")
            original_score = load_score(input_file)
            
            validation_result = self.validate_input(original_score)
            if not validation_result.valid:
                errors.extend(validation_result.errors)
                if validation_result.errors:
                    raise ProcessingError(f"Input validation failed: {validation_result.errors[0]}")
            warnings.extend(validation_result.warnings)
            
            # Step 2: Identify voice locations
            processing_steps.append("Identifying voice locations")
            voice_identifier = VoiceIdentifier(original_score)
            voice_mapping = voice_identifier.analyze_score()
            
            # Create processing context
            context = ProcessingContext(
                original_score=original_score,
                voice_mapping=voice_mapping
            )
            
            # Step 3: Create complete copies for each voice
            processing_steps.append("Creating voice copies")
            voice_scores = self.create_voice_copies(original_score)
            
            # Step 4: Remove unwanted voices from each copy
            processing_steps.append("Removing unwanted voices")
            voice_remover = VoiceRemover(context)
            
            for voice_name in context.get_all_voices():
                voice_location = context.get_voice_location(voice_name)
                removal_result = voice_remover.remove_voices_except(
                    voice_scores[voice_name], voice_location)
                
                if not removal_result.success:
                    errors.extend(removal_result.errors)
                warnings.extend(removal_result.warnings)
            
            # Step 5: Simplify to single-staff layout
            processing_steps.append("Simplifying staff layout")
            staff_simplifier = StaffSimplifier(context)
            
            for voice_name in context.get_all_voices():
                simplification_result = staff_simplifier.convert_to_single_staff(
                    voice_scores[voice_name], voice_name)
                
                if not simplification_result.success:
                    errors.extend(simplification_result.errors)
                warnings.extend(simplification_result.warnings)
            
            # Step 6: Process spanners with voice-aware filtering
            processing_steps.append("Processing spanners with voice context")
            from .spanner_processor import SpannerProcessor
            spanner_processor = SpannerProcessor()
            
            # Extract spanners from original score with context
            spanners_with_context = spanner_processor.extract_all_spanners_from_score(original_score)
            
            # Apply voice-aware spanner processing
            spanner_result = spanner_processor.process_spanners_post_separation(
                voice_scores, spanners_with_context)
            
            if not spanner_result.get('success', True):
                errors.extend(spanner_result.get('errors', []))
            warnings.extend(spanner_result.get('warnings', []))
            
            # Step 7: Apply contextual unification
            processing_steps.append("Applying unification rules")
            contextual_unifier = ContextualUnifier(context)
            unification_result = contextual_unifier.apply_unification_rules(voice_scores)
            
            if not unification_result.success:
                errors.extend(unification_result.errors)
            warnings.extend(unification_result.warnings)
            
            # Step 7: Validate output
            processing_steps.append("Validating output")
            output_validation = self.validate_output(voice_scores)
            if not output_validation.valid:
                errors.extend(output_validation.errors)
            warnings.extend(output_validation.warnings)
            
            # Calculate statistics
            statistics = self._calculate_statistics(original_score, voice_scores)
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=len(errors) == 0,
                voice_scores=voice_scores,
                voice_mapping=voice_mapping,
                processing_steps=processing_steps,
                statistics=statistics,
                warnings=warnings,
                errors=errors,
                processing_time=processing_time
            )
            
        except (AttributeError, ValueError, TypeError) as e:
            processing_time = time.time() - start_time
            errors.append(f"Invalid input data: {e}")
            return ProcessingResult(
                success=False,
                voice_scores={},
                voice_mapping=None,
                processing_steps=processing_steps,
                statistics={},
                warnings=warnings,
                errors=errors,
                processing_time=processing_time
            )
        except music21.exceptions21.Music21Exception as e:
            processing_time = time.time() - start_time
            errors.append(f"Music21 error: {e}")
            return ProcessingResult(
                success=False,
                voice_scores={},
                voice_mapping=None,
                processing_steps=processing_steps,
                statistics={},
                warnings=warnings,
                errors=errors,
                processing_time=processing_time
            )
        except FileNotFoundError as e:
            processing_time = time.time() - start_time
            errors.append(f"File not found: {e}")
            return ProcessingResult(
                success=False,
                voice_scores={},
                voice_mapping=None,
                processing_steps=processing_steps,
                statistics={},
                warnings=warnings,
                errors=errors,
                processing_time=processing_time
            )
        except PermissionError as e:
            processing_time = time.time() - start_time
            errors.append(f"Permission denied: {e}")
            return ProcessingResult(
                success=False,
                voice_scores={},
                voice_mapping=None,
                processing_steps=processing_steps,
                statistics={},
                warnings=warnings,
                errors=errors,
                processing_time=processing_time
            )
        except Exception as e:
            processing_time = time.time() - start_time
            # Log unexpected exceptions for debugging
            import logging
            logging.error(f"Unexpected error in score processing: {type(e).__name__}: {e}")
            errors.append(f"Unexpected error: {type(e).__name__}: {e}")
            
            return ProcessingResult(
                success=False,
                voice_scores={},
                voice_mapping=None,
                processing_steps=processing_steps,
                statistics={},
                warnings=warnings,
                errors=errors,
                processing_time=processing_time
            )
    
    def validate_input(self, score: music21.stream.Score) -> ValidationResult:
        """Validate that input score is suitable for SATB splitting."""
        warnings = []
        errors = []
        details = {}
        
        try:
            # Comprehensive MusicXML structure validation
            
            # 1. Check if score has parts
            if not score.parts:
                errors.append("Score has no parts")
                return ValidationResult(
                    valid=False,
                    warnings=warnings,
                    errors=errors,
                    details=details
                )
            
            # 2. Validate part count and structure
            part_count = len(score.parts)
            details['part_count'] = part_count
            
            if part_count < 1:
                errors.append("Score must have at least 1 part")
            elif part_count > 4:
                warnings.append(f"Score has {part_count} parts, which is more than typical for SATB")
            
            # 3. Validate MusicXML-specific structure for each part
            total_notes = 0
            valid_parts = 0
            
            for i, part in enumerate(score.parts):
                part_errors = []
                part_warnings = []
                
                # Check for musical content
                try:
                    # Use cached flattened view for better performance
                    flattened_part = part.flatten()
                    notes = flattened_part.notes
                    part_note_count = len(notes)
                    total_notes += part_note_count
                    
                    if part_note_count == 0:
                        part_warnings.append(f"Part {i+1} contains no notes")
                    else:
                        valid_parts += 1
                except Exception as e:
                    part_errors.append(f"Part {i+1} structure error: {e}")
                
                # Validate clef structure using proper music21 API
                try:
                    clefs = part.getElementsByClass(music21.clef.Clef)
                    if not clefs:
                        part_warnings.append(f"Part {i+1} has no clef information")
                    else:
                        # Check if clefs are valid music21 clef objects
                        for clef in clefs:
                            if not isinstance(clef, music21.clef.Clef):
                                part_errors.append(f"Part {i+1} has invalid clef object")
                except Exception as e:
                    part_errors.append(f"Part {i+1} clef validation error: {e}")
                
                # Validate time signature structure
                try:
                    time_sigs = part.getElementsByClass(music21.meter.TimeSignature)
                    if not time_sigs:
                        part_warnings.append(f"Part {i+1} has no time signature")
                except Exception as e:
                    part_errors.append(f"Part {i+1} time signature validation error: {e}")
                
                # Validate measure structure
                try:
                    measures = part.getElementsByClass(music21.stream.Measure)
                    if not measures:
                        part_warnings.append(f"Part {i+1} has no explicit measures")
                    else:
                        # Check for voice structure within measures
                        voice_count = 0
                        for measure in measures[:5]:  # Check first 5 measures for performance
                            if hasattr(measure, 'voices') and measure.voices:
                                voice_count = max(voice_count, len(measure.voices))
                        
                        if voice_count > 4:
                            part_warnings.append(f"Part {i+1} has {voice_count} voices, more than typical for SATB")
                except Exception as e:
                    part_errors.append(f"Part {i+1} measure validation error: {e}")
                
                # Aggregate part-level issues
                if part_errors:
                    errors.extend(part_errors)
                if part_warnings:
                    warnings.extend(part_warnings)
            
            details['total_notes'] = total_notes
            details['valid_parts'] = valid_parts
            
            # 4. Overall score validation
            if total_notes == 0:
                errors.append("Score contains no musical notes")
            elif total_notes < 10:
                warnings.append("Score has very few notes, results may be limited")
            
            if valid_parts == 0:
                errors.append("No valid parts found in score")
            
            # 5. Validate MusicXML metadata structure
            try:
                if hasattr(score, 'metadata') and score.metadata:
                    # Check for basic metadata that affects MusicXML export
                    if not hasattr(score.metadata, 'title') or not score.metadata.title:
                        warnings.append("Score lacks title metadata")
                else:
                    warnings.append("Score lacks metadata information")
            except Exception as e:
                warnings.append(f"Metadata validation error: {e}")
            
            # 6. Check for measures across all parts
            total_measures = 0
            for part in score.parts:
                try:
                    measures = part.getElementsByClass(music21.stream.Measure)
                    total_measures = max(total_measures, len(measures))
                except Exception as e:
                    warnings.append(f"Measure counting error in part: {e}")
            
            details['total_measures'] = total_measures
            
            if total_measures == 0:
                warnings.append("No explicit measures found in score")
            
            return ValidationResult(
                valid=len(errors) == 0,
                warnings=warnings,
                errors=errors,
                details=details
            )
            
        except Exception as e:
            errors.append(f"Validation failed: {e}")
            return ValidationResult(
                valid=False,
                warnings=warnings,
                errors=errors,
                details=details
            )
    
    def create_voice_copies(self, original: music21.stream.Score) -> Dict[str, music21.stream.Score]:
        """Create complete copies of score for each voice."""
        voice_scores = {}
        
        voice_names = ['Soprano', 'Alto', 'Tenor', 'Bass']
        
        for voice_name in voice_names:
            # Create efficient score copy using music21's template method
            voice_scores[voice_name] = self._create_efficient_score_copy(original)
        
        return voice_scores
    
    def _create_efficient_score_copy(self, original: music21.stream.Score) -> music21.stream.Score:
        """Create an efficient copy of the score avoiding full deep copy."""
        # Use music21's score template for basic structure
        new_score = music21.stream.Score()
        
        # Copy metadata efficiently
        if original.metadata:
            new_score.metadata = music21.metadata.Metadata()
            # Copy essential metadata fields only
            if hasattr(original.metadata, 'title') and original.metadata.title:
                new_score.metadata.title = original.metadata.title
            if hasattr(original.metadata, 'composer') and original.metadata.composer:
                new_score.metadata.composer = original.metadata.composer
            if hasattr(original.metadata, 'workTitle') and original.metadata.workTitle:
                new_score.metadata.workTitle = original.metadata.workTitle
        
        # Copy parts with selective copying
        for original_part in original.parts:
            new_part = music21.stream.Part()
            
            # Copy part-level attributes
            if hasattr(original_part, 'partName') and original_part.partName:
                new_part.partName = original_part.partName
            if hasattr(original_part, 'partAbbreviation') and original_part.partAbbreviation:
                new_part.partAbbreviation = original_part.partAbbreviation
            
            # Copy essential elements efficiently using music21's built-in methods
            for element in original_part.elements:
                if isinstance(element, music21.stream.Measure):
                    # For measures, create new measure and copy essential content
                    new_measure = self._copy_measure_efficiently(element)
                    new_part.append(new_measure)
                elif isinstance(element, (music21.clef.Clef,
                                        music21.key.KeySignature,
                                        music21.meter.TimeSignature,
                                        music21.instrument.Instrument)):
                    # For these simple objects, use music21's clone method if available
                    try:
                        if hasattr(element, 'clone'):
                            new_part.append(element.clone())
                        else:
                            # Fallback to creating new instances with same properties
                            new_element = self._clone_element_efficiently(element)
                            if new_element:
                                new_part.append(new_element)
                    except Exception:
                        # If efficient copying fails, fallback to deepcopy for this element only
                        import copy
                        new_part.append(copy.deepcopy(element))
            
            # CRITICAL FIX: Copy spanners (including crescendos) from original part
            # Spanners are stored separately and not included in elements iteration
            self._copy_part_spanners(original_part, new_part)
            
            new_score.append(new_part)
        return new_score
    def _copy_part_spanners(self, original_part: music21.stream.Part, new_part: music21.stream.Part):
        """Copy spanners (crescendos, slurs, etc.) from original part to new part."""
        # NOTE: Spanners are now handled by voice-aware spanner processor
        # This method is disabled to prevent copying ALL spanners to ALL voices
        # The sophisticated spanner processing will handle voice-specific assignments
        pass
    
    def _copy_measure_efficiently(self, original_measure: music21.stream.Measure) -> music21.stream.Measure:
        """Create an efficient copy of a measure without full deep copy."""
        new_measure = music21.stream.Measure()
        
        # Copy measure number and basic properties
        if hasattr(original_measure, 'number') and original_measure.number is not None:
            new_measure.number = original_measure.number
        
        # Copy elements efficiently
        for element in original_measure:
            try:
                # Use music21's clone method if available for better performance
                if hasattr(element, 'clone'):
                    new_measure.append(element.clone())
                elif isinstance(element, music21.stream.Voice):
                    # For voices, create new voice and copy contents
                    new_voice = music21.stream.Voice()
                    new_voice.id = element.id if hasattr(element, 'id') else None
                    for voice_element in element:
                        if hasattr(voice_element, 'clone'):
                            new_voice.append(voice_element.clone())
                        else:
                            # Fallback to deepcopy for complex elements
                            import copy
                            new_voice.append(copy.deepcopy(voice_element))
                    new_measure.append(new_voice)
                else:
                    # For other elements, try clone first, then fallback
                    cloned = self._clone_element_efficiently(element)
                    if cloned:
                        new_measure.append(cloned)
                    else:
                        import copy
                        new_measure.append(copy.deepcopy(element))
            except Exception:
                # If all else fails, use deepcopy
                import copy
                new_measure.append(copy.deepcopy(element))
        
        return new_measure
    
    def _clone_element_efficiently(self, element) -> object:
        """Efficiently clone a music21 element."""
        try:
            # Try music21's clone method first
            if hasattr(element, 'clone'):
                return element.clone()
            
            # For specific element types, create new instances efficiently
            if isinstance(element, music21.clef.TrebleClef):
                return music21.clef.TrebleClef()
            elif isinstance(element, music21.clef.BassClef):
                return music21.clef.BassClef()
            elif isinstance(element, music21.clef.AltoClef):
                return music21.clef.AltoClef()
            elif isinstance(element, music21.key.KeySignature):
                return music21.key.KeySignature(sharps=element.sharps)
            elif isinstance(element, music21.meter.TimeSignature):
                return music21.meter.TimeSignature(element.numerator, element.denominator)
            elif isinstance(element, music21.instrument.Instrument):
                new_instrument = music21.instrument.Instrument()
                if hasattr(element, 'instrumentName'):
                    new_instrument.instrumentName = element.instrumentName
                return new_instrument
            elif isinstance(element, music21.note.Note):
                return music21.note.Note(
                    pitch=element.pitch,
                    quarterLength=element.quarterLength
                )
            elif isinstance(element, music21.note.Rest):
                return music21.note.Rest(quarterLength=element.quarterLength)
            elif isinstance(element, music21.chord.Chord):
                return music21.chord.Chord(
                    notes=[n.pitch for n in element.notes],
                    quarterLength=element.quarterLength
                )
            
            # If we don't have a specific handler, return None to signal fallback needed
            return None
            
        except Exception:
            return None
    
    
    def validate_output(self, voice_scores: Dict[str, music21.stream.Score]) -> ValidationResult:
        """Validate that output scores are correct and complete."""
        warnings = []
        errors = []
        details = {}
        
        try:
            # Check that we have all expected voices
            expected_voices = ['Soprano', 'Alto', 'Tenor', 'Bass']
            missing_voices = []
            
            for voice in expected_voices:
                if voice not in voice_scores:
                    missing_voices.append(voice)
            
            if missing_voices:
                errors.append(f"Missing voice scores: {missing_voices}")
            
            # Check each voice score
            for voice_name, score in voice_scores.items():
                voice_details = {}
                
                # Check if score has parts
                if not score.parts:
                    errors.append(f"{voice_name} score has no parts")
                    continue
                
                # Check for musical content
                note_count = len(score.flatten().notes)
                voice_details['note_count'] = note_count
                
                if note_count == 0:
                    warnings.append(f"{voice_name} score has no notes")
                
                # Check part count (should be 1 after simplification)
                part_count = len(score.parts)
                voice_details['part_count'] = part_count
                
                if part_count != 1:
                    warnings.append(f"{voice_name} score has {part_count} parts, expected 1")
                
                details[voice_name] = voice_details
            
            return ValidationResult(
                valid=len(errors) == 0,
                warnings=warnings,
                errors=errors,
                details=details
            )
            
        except Exception as e:
            errors.append(f"Output validation failed: {e}")
            return ValidationResult(
                valid=False,
                warnings=warnings,
                errors=errors,
                details=details
            )
    
    def _calculate_statistics(self, original_score: music21.stream.Score,
                            voice_scores: Dict[str, music21.stream.Score]) -> dict:
        """Calculate processing statistics."""
        statistics = {}
        
        # Input statistics
        statistics['input_measures'] = self._count_measures(original_score)
        statistics['input_parts'] = len(original_score.parts)
        statistics['input_voices'] = self._count_total_voices(original_score)
        
        # Output statistics
        statistics['output_scores'] = len(voice_scores)
        
        # Elements preserved per voice (optimize by caching flattened views)
        elements_preserved = {}
        for voice_name, score in voice_scores.items():
            # Use cached flattened view for performance
            flattened_score = score.flatten()
            elements_preserved[voice_name] = len(flattened_score.notes)
        statistics['elements_preserved'] = elements_preserved
        
        # Processing efficiency metrics (more meaningful than memory usage)
        statistics['total_elements_processed'] = sum(
            len(score.flatten().notes) for score in voice_scores.values()
        )
        statistics['average_elements_per_voice'] = (
            statistics['total_elements_processed'] / len(voice_scores)
            if voice_scores else 0
        )
        
        return statistics
    
    def _count_measures(self, score: music21.stream.Score) -> int:
        """Count the number of measures in a score."""
        max_measures = 0
        for part in score.parts:
            measures = part.getElementsByClass(music21.stream.Measure)
            max_measures = max(max_measures, len(measures))
        return max_measures
    
    def _count_total_voices(self, score: music21.stream.Score) -> int:
        """Count the total number of voices across all parts."""
        total_voices = 0
        for part in score.parts:
            voice_ids = set()
            for measure in part.getElementsByClass(music21.stream.Measure):
                for voice in measure.voices:
                    voice_ids.add(voice.id)
            total_voices += max(1, len(voice_ids))  # At least 1 voice per part
        return total_voices