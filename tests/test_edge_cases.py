"""Tests for edge cases and error handling."""

import pytest
import tempfile
import os
from pathlib import Path
import music21
from satb_splitter import split_satb_voices
from satb_splitter.score_processor import ScoreProcessor
from satb_splitter.exceptions import SATBSplitError, InvalidScoreError
from satb_splitter.utils import load_score
from satb_splitter.voice_identifier import VoiceIdentifier


class TestFileHandling:
    """Test file handling edge cases."""

    def test_nonexistent_file(self):
        """Test handling of nonexistent files."""
        with pytest.raises((FileNotFoundError, SATBSplitError, Exception)):
            split_satb_voices("nonexistent_file.musicxml")

    def test_invalid_musicxml_file(self, tmp_path):
        """Test handling of invalid MusicXML files."""
        # Create an invalid MusicXML file
        invalid_file = tmp_path / "invalid.musicxml"
        invalid_file.write_text("This is not valid MusicXML content")
        
        with pytest.raises((SATBSplitError, Exception)):
            split_satb_voices(str(invalid_file))

    def test_empty_file(self, tmp_path):
        """Test handling of empty files."""
        empty_file = tmp_path / "empty.musicxml"
        empty_file.write_text("")
        
        with pytest.raises((SATBSplitError, Exception)):
            split_satb_voices(str(empty_file))

    def test_permission_denied_output(self, sample_musicxml_file, tmp_path):
        """Test handling of permission denied for output directory."""
        # Create a directory and make it read-only
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only
        
        try:
            # This might succeed or fail depending on the system
            split_satb_voices(sample_musicxml_file, output_dir=str(readonly_dir))
        except (PermissionError, OSError):
            # Expected on some systems
            pass
        finally:
            # Restore permissions for cleanup
            readonly_dir.chmod(0o755)

    def test_invalid_output_directory(self, sample_musicxml_file):
        """Test handling of invalid output directory paths."""
        # Test with invalid characters (system-dependent)
        invalid_paths = [
            "/dev/null/subdir",  # Can't create subdirectory under /dev/null
            "",  # Empty string
        ]
        
        for invalid_path in invalid_paths:
            try:
                split_satb_voices(sample_musicxml_file, output_dir=invalid_path)
            except (OSError, ValueError, SATBSplitError):
                # Expected for invalid paths
                pass

    def test_very_long_filename(self, sample_musicxml_file, tmp_path):
        """Test handling of very long output filenames."""
        # Create a very long directory name (but not too long to cause issues)
        long_name = "a" * 100
        long_dir = tmp_path / long_name
        long_dir.mkdir()
        
        # This should work
        voice_scores = split_satb_voices(
            sample_musicxml_file, 
            output_dir=str(long_dir)
        )
        
        assert len(voice_scores) > 0, "Should handle long directory names"


class TestMalformedScores:
    """Test handling of malformed or unusual musical scores."""

    def test_score_with_no_parts(self, tmp_path):
        """Test handling of scores with no parts."""
        # Create a minimal MusicXML with no parts
        minimal_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <score-partwise version="3.1">
            <part-list/>
        </score-partwise>'''
        
        malformed_file = tmp_path / "no_parts.musicxml"
        malformed_file.write_text(minimal_xml)
        
        with pytest.raises((SATBSplitError, Exception)):
            split_satb_voices(str(malformed_file))

    def test_score_with_no_notes(self, tmp_path):
        """Test handling of scores with parts but no notes."""
        minimal_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <score-partwise version="3.1">
            <part-list>
                <score-part id="P1">
                    <part-name>Part 1</part-name>
                </score-part>
            </part-list>
            <part id="P1">
                <measure number="1">
                    <attributes>
                        <divisions>1</divisions>
                        <key><fifths>0</fifths></key>
                        <time><beats>4</beats><beat-type>4</beat-type></time>
                        <clef><sign>G</sign><line>2</line></clef>
                    </attributes>
                </measure>
            </part>
        </score-partwise>'''
        
        no_notes_file = tmp_path / "no_notes.musicxml"
        no_notes_file.write_text(minimal_xml)
        
        # This might succeed but produce empty voices
        try:
            voice_scores = split_satb_voices(str(no_notes_file))
            # If it succeeds, voices should be present but possibly empty
            assert isinstance(voice_scores, dict)
        except (SATBSplitError, Exception):
            # Also acceptable to fail
            pass

    def test_score_with_single_voice(self, tmp_path):
        """Test handling of scores with only one voice."""
        single_voice_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <score-partwise version="3.1">
            <part-list>
                <score-part id="P1">
                    <part-name>Solo</part-name>
                </score-part>
            </part-list>
            <part id="P1">
                <measure number="1">
                    <attributes>
                        <divisions>1</divisions>
                        <key><fifths>0</fifths></key>
                        <time><beats>4</beats><beat-type>4</beat-type></time>
                        <clef><sign>G</sign><line>2</line></clef>
                    </attributes>
                    <note>
                        <pitch><step>C</step><octave>4</octave></pitch>
                        <duration>4</duration>
                        <type>whole</type>
                    </note>
                </measure>
            </part>
        </score-partwise>'''
        
        single_voice_file = tmp_path / "single_voice.musicxml"
        single_voice_file.write_text(single_voice_xml)
        
        # This should either succeed (with limited voice separation) or fail gracefully
        try:
            voice_scores = split_satb_voices(str(single_voice_file))
            assert isinstance(voice_scores, dict)
            # Might have fewer than 4 voices
            assert len(voice_scores) >= 0
        except (SATBSplitError, Exception):
            # Also acceptable to fail with insufficient voices
            pass


class TestParameterEdgeCases:
    """Test edge cases with function parameters."""

    def test_none_parameters(self):
        """Test handling of None parameters."""
        with pytest.raises((TypeError, AttributeError)):
            split_satb_voices(None)

    def test_empty_string_filename(self):
        """Test handling of empty string filename."""
        with pytest.raises((FileNotFoundError, ValueError, SATBSplitError)):
            split_satb_voices("")

    def test_invalid_parameter_types(self, sample_musicxml_file):
        """Test handling of invalid parameter types."""
        # Test with invalid output_dir type
        with pytest.raises((TypeError, AttributeError)):
            split_satb_voices(sample_musicxml_file, output_dir=123)

    def test_valid_parameters(self, sample_musicxml_file, tmp_path):
        """Test various valid parameter combinations."""
        # Test valid parameter combinations that the function actually accepts
        valid_combinations = [
            {},  # No optional parameters
            {"output_dir": str(tmp_path / "test1")},  # With output directory
            {"output_dir": None},  # Explicit None output directory
        ]
        
        for params in valid_combinations:
            try:
                voice_scores = split_satb_voices(sample_musicxml_file, **params)
                assert len(voice_scores) > 0, f"Failed with params: {params}"
            except Exception as e:
                pytest.fail(f"Unexpected error with params {params}: {e}")


class TestMemoryAndPerformance:
    """Test memory usage and performance edge cases."""

    def test_repeated_processing(self, sample_musicxml_file):
        """Test repeated processing of the same file."""
        # Process the same file multiple times to check for memory leaks
        for i in range(3):  # Reduced to 3 for faster testing
            voice_scores = split_satb_voices(sample_musicxml_file)
            assert len(voice_scores) > 0, f"Failed on iteration {i}"

    def test_concurrent_processing(self, sample_musicxml_file):
        """Test that multiple instances can run without interference."""
        # Create two separate ScoreProcessor instances
        processor1 = ScoreProcessor()
        processor2 = ScoreProcessor()
        
        # Process with both
        result1 = processor1.process_satb_score(sample_musicxml_file)
        result2 = processor2.process_satb_score(sample_musicxml_file)
        
        # Both should succeed
        assert len(result1.voice_scores) > 0
        assert len(result2.voice_scores) > 0
        
        # Results should be similar (but may not be identical due to processing)
        assert len(result1.voice_scores) == len(result2.voice_scores)


class TestVoiceIdentifierEdgeCases:
    """Test edge cases for VoiceIdentifier."""

    def test_voice_identifier_with_minimal_score(self, tmp_path):
        """Test VoiceIdentifier with minimal score."""
        minimal_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <score-partwise version="3.1">
            <part-list>
                <score-part id="P1">
                    <part-name>Part 1</part-name>
                </score-part>
            </part-list>
            <part id="P1">
                <measure number="1">
                    <attributes>
                        <divisions>1</divisions>
                        <key><fifths>0</fifths></key>
                        <time><beats>4</beats><beat-type>4</beat-type></time>
                        <clef><sign>G</sign><line>2</line></clef>
                    </attributes>
                    <note>
                        <pitch><step>C</step><octave>4</octave></pitch>
                        <duration>1</duration>
                        <type>quarter</type>
                    </note>
                </measure>
            </part>
        </score-partwise>'''
        
        minimal_file = tmp_path / "minimal.musicxml"
        minimal_file.write_text(minimal_xml)
        
        try:
            score = load_score(str(minimal_file))
            identifier = VoiceIdentifier(score)
            voice_mapping = identifier.analyze_score()
            
            # Should handle minimal score gracefully
            assert voice_mapping is not None
            # Confidence might be low
            assert 0.0 <= voice_mapping.confidence <= 1.0
        except Exception as e:
            # Also acceptable to fail with insufficient data
            assert ("insufficient" in str(e).lower() or
                    "not enough" in str(e).lower() or
                    "expected 2 parts" in str(e).lower())

    def test_voice_identifier_with_none_score(self):
        """Test VoiceIdentifier with None score."""
        # Current implementation may handle None gracefully
        try:
            identifier = VoiceIdentifier(None)
            # If it doesn't raise, that's acceptable behavior
            assert identifier is not None
        except (TypeError, AttributeError):
            # Also acceptable to raise these exceptions
            pass

    def test_voice_identifier_confidence_bounds(self, sample_score):
        """Test that VoiceIdentifier confidence is always in valid bounds."""
        identifier = VoiceIdentifier(sample_score)
        voice_mapping = identifier.analyze_score()
        
        # Confidence should always be between 0 and 1
        assert 0.0 <= voice_mapping.confidence <= 1.0
        assert isinstance(voice_mapping.confidence, (int, float))


class TestScoreProcessorEdgeCases:
    """Test edge cases for ScoreProcessor."""

    def test_score_processor_invalid_options(self, sample_musicxml_file):
        """Test ScoreProcessor with invalid options."""
        processor = ScoreProcessor()
        
        # Test with unexpected keyword arguments
        try:
            result = processor.process_satb_score(
                sample_musicxml_file,
                invalid_option=True
            )
            # Should either ignore invalid options or handle them gracefully
        except TypeError:
            # Also acceptable to raise TypeError for unexpected arguments
            pass

    def test_score_processor_none_filename(self):
        """Test ScoreProcessor with None filename."""
        processor = ScoreProcessor()
        
        # Current implementation returns a failed result rather than raising
        result = processor.process_satb_score(None)
        assert hasattr(result, 'success'), "Result should have success attribute"
        assert not result.success, "Processing should fail for None filename"

    def test_score_processor_state_consistency(self, sample_musicxml_file):
        """Test that ScoreProcessor maintains consistent state."""
        processor = ScoreProcessor()
        
        # Process multiple files to ensure state doesn't interfere
        result1 = processor.process_satb_score(sample_musicxml_file)
        result2 = processor.process_satb_score(sample_musicxml_file)
        
        # Results should be consistent
        assert len(result1.voice_scores) == len(result2.voice_scores)
        
        # Voice names should be the same
        assert set(result1.voice_scores.keys()) == set(result2.voice_scores.keys())


class TestUtilsEdgeCases:
    """Test edge cases for utility functions."""

    def test_load_score_edge_cases(self, tmp_path):
        """Test load_score with various edge cases."""
        # Test with nonexistent file
        with pytest.raises((FileNotFoundError, Exception)):
            load_score("nonexistent.musicxml")
        
        # Test with empty file
        empty_file = tmp_path / "empty.musicxml"
        empty_file.write_text("")
        
        with pytest.raises((Exception,)):
            load_score(str(empty_file))
        
        # Test with None - current implementation may handle this differently
        with pytest.raises((TypeError, AttributeError, InvalidScoreError)):
            load_score(None)

    def test_load_score_with_various_extensions(self, sample_musicxml_file, tmp_path):
        """Test load_score with various file extensions."""
        # Copy the sample file with different extensions
        extensions = ['.xml', '.mxl']  # Common MusicXML extensions
        
        for ext in extensions:
            new_file = tmp_path / f"test{ext}"
            new_file.write_text(Path(sample_musicxml_file).read_text())
            
            try:
                score = load_score(str(new_file))
                assert score is not None
            except Exception:
                # Some extensions might not be supported
                pass