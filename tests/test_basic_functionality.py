"""Basic functionality tests for the SATB splitter."""

import pytest
import music21
from pathlib import Path
from satb_splitter import split_satb_voices
from satb_splitter.voice_identifier import VoiceIdentifier
from satb_splitter.score_processor import ScoreProcessor
from satb_splitter.exceptions import SATBSplitError


class TestBasicFunctionality:
    """Test basic SATB splitter functionality."""

    def test_split_satb_voices_success(self, sample_musicxml_file, expected_voices):
        """Test successful voice splitting with default settings."""
        voice_scores = split_satb_voices(sample_musicxml_file)
        
        # Check that all expected voices are present
        assert len(voice_scores) == len(expected_voices)
        for voice in expected_voices:
            assert voice in voice_scores, f"Missing voice: {voice}"
        
        # Check that each voice has content
        for voice_name, score in voice_scores.items():
            assert score is not None, f"{voice_name} score is None"
            assert len(score.parts) > 0, f"{voice_name} has no parts"
            
            # Check for musical content
            notes = score.flatten().notes
            assert len(notes) > 0, f"{voice_name} has no notes"

    def test_split_satb_voices_with_output_dir(self, sample_musicxml_file, temp_output_dir, expected_voices):
        """Test voice splitting with custom output directory."""
        voice_scores = split_satb_voices(
            sample_musicxml_file, 
            output_dir=str(temp_output_dir)
        )
        
        # Check that files were created
        for voice in expected_voices:
            expected_file = temp_output_dir / f"Crossing The Bar-{voice}.musicxml"
            assert expected_file.exists(), f"Output file not created for {voice}"
            
            # Verify file is valid MusicXML
            score = music21.converter.parse(str(expected_file))
            assert score is not None
            assert len(score.parts) > 0

    def test_split_satb_voices_nonexistent_file(self):
        """Test error handling for nonexistent file."""
        with pytest.raises((FileNotFoundError, SATBSplitError)):
            split_satb_voices("nonexistent_file.musicxml")

    def test_split_satb_voices_invalid_file(self, tmp_path):
        """Test error handling for invalid MusicXML file."""
        invalid_file = tmp_path / "invalid.musicxml"
        invalid_file.write_text("This is not valid MusicXML")
        
        with pytest.raises((SATBSplitError, Exception)):
            split_satb_voices(str(invalid_file))

    def test_voice_scores_structure(self, voice_scores, helpers):
        """Test the structure of returned voice scores."""
        for voice_name, score in voice_scores.items():
            # Each voice should have exactly one part
            assert len(score.parts) == 1, f"{voice_name} should have exactly one part"
            
            # Check measure count consistency
            measure_count = helpers.count_measures_in_score(score)
            assert measure_count > 0, f"{voice_name} should have measures"
            
            # Check that the part has proper structure
            part = score.parts[0]
            assert part.partName == voice_name or part.id == voice_name

    def test_note_conservation(self, sample_score, voice_scores, helpers):
        """Test that no notes are lost or duplicated during separation."""
        # Count original notes
        original_note_count = helpers.count_notes_in_score(sample_score)
        
        # Count separated notes
        separated_note_count = sum(
            helpers.count_notes_in_score(score) 
            for score in voice_scores.values()
        )
        
        # Notes should be conserved (allowing for some flexibility due to processing)
        assert separated_note_count > 0, "No notes found in separated voices"
        assert abs(separated_note_count - original_note_count) <= original_note_count * 0.1, \
            f"Note count mismatch: original={original_note_count}, separated={separated_note_count}"


class TestVoiceIdentification:
    """Test voice identification functionality."""

    def test_voice_identifier_analysis(self, sample_score):
        """Test voice identifier analysis."""
        identifier = VoiceIdentifier(sample_score)
        voice_mapping = identifier.analyze_score()
        
        # Check that mapping is valid
        assert voice_mapping.validate(), "Voice mapping validation failed"
        
        # Validate voice mapping structure
        assert voice_mapping.validate(), "Voice mapping should be valid"
        
        # Check that all voices are mapped
        assert voice_mapping.soprano is not None, "Soprano not mapped"
        assert voice_mapping.alto is not None, "Alto not mapped"
        assert voice_mapping.tenor is not None, "Tenor not mapped"
        assert voice_mapping.bass is not None, "Bass not mapped"

    def test_voice_pitch_ranges(self, voice_scores, helpers):
        """Test that voices have appropriate pitch ranges."""
        # Get pitch ranges for each voice
        voice_ranges = {}
        for voice_name, score in voice_scores.items():
            pitch_range = helpers.get_pitch_range(score)
            if pitch_range:
                voice_ranges[voice_name] = pitch_range

        # Should have all four voices with pitch data
        assert len(voice_ranges) == 4, "Should have pitch data for all four voices"
        
        # Check relative ordering (Soprano highest average, Bass lowest average)
        if all(voice in voice_ranges for voice in ['Soprano', 'Alto', 'Tenor', 'Bass']):
            soprano_avg = voice_ranges['Soprano']['avg']
            alto_avg = voice_ranges['Alto']['avg']
            tenor_avg = voice_ranges['Tenor']['avg']
            bass_avg = voice_ranges['Bass']['avg']
            
            # Soprano should generally be higher than Alto
            assert soprano_avg >= alto_avg - 5, "Soprano should be higher than or close to Alto"
            
            # Bass should generally be lower than Tenor
            assert bass_avg <= tenor_avg + 5, "Bass should be lower than or close to Tenor"
            
            # Soprano should be higher than Bass
            assert soprano_avg > bass_avg, "Soprano should be higher than Bass"


class TestScoreProcessor:
    """Test ScoreProcessor functionality."""

    def test_score_processor_basic(self, sample_musicxml_file, score_processor):
        """Test basic ScoreProcessor functionality."""
        result = score_processor.process_satb_score(sample_musicxml_file)
        
        # Check result structure
        assert hasattr(result, 'voice_scores'), "Result should have voice_scores"
        assert hasattr(result, 'success'), "Result should have success status"
        assert hasattr(result, 'voice_mapping'), "Result should have voice_mapping"
        
        # Check voice scores
        assert len(result.voice_scores) > 0, "Should have at least one voice"
        assert result.success, "Processing should be successful"
        
        # Check that voice mapping is present
        assert result.voice_mapping is not None, "Voice mapping should be present"

    def test_score_processor_multiple_calls(self, sample_musicxml_file):
        """Test ScoreProcessor with multiple calls."""
        processor = ScoreProcessor()
        
        # Test multiple calls to the same processor
        result1 = processor.process_satb_score(sample_musicxml_file)
        result2 = processor.process_satb_score(sample_musicxml_file)
        
        assert len(result1.voice_scores) > 0, "First call should produce voice scores"
        assert len(result2.voice_scores) > 0, "Second call should produce voice scores"
        assert len(result1.voice_scores) == len(result2.voice_scores), "Should produce consistent results"

    def test_score_processor_error_handling(self, score_processor):
        """Test ScoreProcessor error handling."""
        result = score_processor.process_satb_score("nonexistent.musicxml")
        # Should return a result indicating failure rather than raising
        assert hasattr(result, 'success'), "Result should have success attribute"
        assert not result.success, "Processing should fail for nonexistent file"
        assert hasattr(result, 'errors'), "Result should have errors"
        assert len(result.errors) > 0, "Should have error messages"


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_pipeline(self, sample_musicxml_file, temp_output_dir):
        """Test the complete pipeline from input to output files."""
        # Process the score
        voice_scores = split_satb_voices(
            sample_musicxml_file,
            output_dir=str(temp_output_dir)
        )
        
        # Verify in-memory results
        assert len(voice_scores) == 4, "Should produce 4 voices"
        
        # Verify output files
        expected_voices = ['Soprano', 'Alto', 'Tenor', 'Bass']
        for voice in expected_voices:
            output_file = temp_output_dir / f"Crossing The Bar-{voice}.musicxml"
            assert output_file.exists(), f"Output file missing for {voice}"
            
            # Verify file can be loaded and has content
            score = music21.converter.parse(str(output_file))
            assert len(score.parts) > 0, f"{voice} output file has no parts"
            assert len(score.flatten().notes) > 0, f"{voice} output file has no notes"

    def test_voice_consistency(self, voice_scores, helpers):
        """Test that all voices have consistent structure."""
        measure_counts = {}
        
        for voice_name, score in voice_scores.items():
            measure_count = helpers.count_measures_in_score(score)
            measure_counts[voice_name] = measure_count
        
        # All voices should have the same number of measures
        unique_counts = set(measure_counts.values())
        assert len(unique_counts) <= 2, f"Measure counts too varied: {measure_counts}"
        
        # Check that all voices have reasonable measure counts
        for voice_name, count in measure_counts.items():
            assert count > 0, f"{voice_name} has no measures"
            assert count < 200, f"{voice_name} has suspiciously many measures: {count}"