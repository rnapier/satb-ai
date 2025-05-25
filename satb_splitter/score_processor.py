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
            
            # Step 6: Apply contextual unification
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
        except music21.exceptions21.Music21Exception as e:
            processing_time = time.time() - start_time
            errors.append(f"Music21 error: {e}")
        except FileNotFoundError as e:
            processing_time = time.time() - start_time
            errors.append(f"File not found: {e}")
        except PermissionError as e:
            processing_time = time.time() - start_time
            errors.append(f"Permission denied: {e}")
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
            # Create a deep copy of the original score
            voice_scores[voice_name] = copy.deepcopy(original)
        
        return voice_scores
    
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
        
        # Elements preserved per voice
        elements_preserved = {}
        for voice_name, score in voice_scores.items():
            elements_preserved[voice_name] = len(score.flatten().notes)
        statistics['elements_preserved'] = elements_preserved
        
        # Memory usage (approximate)
        import sys
        memory_usage = 0
        for score in voice_scores.values():
            memory_usage += sys.getsizeof(score)
        statistics['memory_usage_mb'] = memory_usage / (1024 * 1024)
        
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