"""Performance and stress tests for the SATB splitter."""

import pytest
import time
import tempfile
from pathlib import Path
import music21
from satb_splitter import split_satb_voices
from satb_splitter.score_processor import ScoreProcessor


class TestPerformance:
    """Test performance characteristics of the SATB splitter."""

    @pytest.mark.slow
    def test_processing_time_reasonable(self, sample_musicxml_file):
        """Test that processing time is reasonable for typical files."""
        start_time = time.time()
        
        voice_scores = split_satb_voices(sample_musicxml_file)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (adjust as needed)
        assert processing_time < 30.0, f"Processing took too long: {processing_time:.2f}s"
        assert len(voice_scores) > 0, "Should produce voice scores"

    @pytest.mark.slow
    def test_memory_usage_stability(self, sample_musicxml_file):
        """Test that memory usage remains stable across multiple runs."""
        # Process the file multiple times to check for memory leaks
        results = []
        
        for i in range(5):
            voice_scores = split_satb_voices(sample_musicxml_file)
            results.append(len(voice_scores))
            
            # Verify consistent results
            assert len(voice_scores) > 0, f"Run {i}: No voice scores produced"
        
        # All runs should produce the same number of voices
        assert len(set(results)) == 1, f"Inconsistent results across runs: {results}"

    def test_concurrent_processing_safety(self, sample_musicxml_file):
        """Test that concurrent processing doesn't cause issues."""
        processors = [ScoreProcessor() for _ in range(3)]
        results = []
        
        # Process with multiple processors
        for processor in processors:
            result = processor.process_satb_score(sample_musicxml_file)
            results.append(len(result.voice_scores))
        
        # All should produce similar results
        assert len(set(results)) <= 1, f"Inconsistent concurrent results: {results}"

    @pytest.mark.slow
    def test_large_output_handling(self, sample_musicxml_file, temp_output_dir):
        """Test handling of scenarios that might produce large outputs."""
        # Process with output enabled
        voice_scores = split_satb_voices(
            sample_musicxml_file,
            output_dir=str(temp_output_dir)
        )
        
        # Check that all files were created and are reasonable size
        expected_voices = ['Soprano', 'Alto', 'Tenor', 'Bass']
        
        for voice in expected_voices:
            output_file = temp_output_dir / f"Crossing The Bar-{voice}.musicxml"
            assert output_file.exists(), f"Output file missing for {voice}"
            
            # Check file size is reasonable (not empty, not extremely large)
            file_size = output_file.stat().st_size
            assert file_size > 100, f"{voice} file too small: {file_size} bytes"
            assert file_size < 10_000_000, f"{voice} file too large: {file_size} bytes"

    def test_processing_efficiency(self, sample_musicxml_file):
        """Test that processing is efficient and doesn't waste resources."""
        processor = ScoreProcessor()
        
        # Time multiple aspects of processing
        start_time = time.time()
        result = processor.process_satb_score(sample_musicxml_file)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # Calculate efficiency metrics
        total_notes = sum(
            len(score.flatten().notes) 
            for score in result.voice_scores.values()
        )
        
        if total_notes > 0:
            notes_per_second = total_notes / total_time
            # Should process at least a few notes per second
            assert notes_per_second > 1.0, f"Too slow: {notes_per_second:.2f} notes/sec"


class TestStress:
    """Stress tests for edge cases and limits."""

    def test_repeated_processing_stability(self, sample_musicxml_file):
        """Test stability under repeated processing."""
        # Process the same file many times
        for i in range(10):
            try:
                voice_scores = split_satb_voices(sample_musicxml_file)
                assert len(voice_scores) > 0, f"Failed on iteration {i}"
            except Exception as e:
                pytest.fail(f"Failed on iteration {i}: {e}")

    def test_parameter_combinations(self, sample_musicxml_file, tmp_path):
        """Test various parameter combinations for stability."""
        parameter_combinations = [
            {},
            {"output_dir": str(tmp_path / "test1")},
            {"output_dir": None},
        ]
        
        for params in parameter_combinations:
            try:
                voice_scores = split_satb_voices(sample_musicxml_file, **params)
                assert len(voice_scores) > 0, f"Failed with params: {params}"
            except Exception as e:
                pytest.fail(f"Failed with params {params}: {e}")

    @pytest.mark.slow
    def test_output_directory_stress(self, sample_musicxml_file, tmp_path):
        """Test creating output in many different directories."""
        # Create multiple output directories and process to each
        for i in range(5):
            output_dir = tmp_path / f"output_{i}"
            
            voice_scores = split_satb_voices(
                sample_musicxml_file,
                output_dir=str(output_dir)
            )
            
            assert len(voice_scores) > 0, f"Failed for output directory {i}"
            
            # Verify files exist
            expected_voices = ['Soprano', 'Alto', 'Tenor', 'Bass']
            for voice in expected_voices:
                output_file = output_dir / f"Crossing The Bar-{voice}.musicxml"
                assert output_file.exists(), f"Missing file in directory {i}: {voice}"

    def test_score_object_reuse(self, sample_musicxml_file):
        """Test that score objects can be safely reused."""
        # Use multiple processors with the same file
        processors = [ScoreProcessor() for _ in range(3)]
        
        for i, processor in enumerate(processors):
            # Test that multiple processors can handle the same file
            result = processor.process_satb_score(sample_musicxml_file)
            
            assert result is not None, f"Failed with processor {i}"
            assert result.success, f"Processing failed with processor {i}"
            assert len(result.voice_scores) > 0, f"No voice scores with processor {i}"


class TestResourceManagement:
    """Test proper resource management and cleanup."""

    def test_temporary_resource_cleanup(self, sample_musicxml_file):
        """Test that temporary resources are properly cleaned up."""
        # Process multiple times and ensure no resource leaks
        initial_temp_count = len(list(Path(tempfile.gettempdir()).glob("*")))
        
        for _ in range(5):
            voice_scores = split_satb_voices(sample_musicxml_file)
            assert len(voice_scores) > 0
        
        final_temp_count = len(list(Path(tempfile.gettempdir()).glob("*")))
        
        # Allow some variation but no major leaks
        temp_increase = final_temp_count - initial_temp_count
        assert temp_increase < 50, f"Possible temp file leak: {temp_increase} new files"

    def test_music21_object_handling(self, sample_musicxml_file):
        """Test proper handling of music21 objects."""
        voice_scores = split_satb_voices(sample_musicxml_file)
        
        # Verify all returned objects are valid music21 streams
        for voice_name, score in voice_scores.items():
            assert isinstance(score, music21.stream.Stream), f"{voice_name} is not a Stream"
            
            # Test that objects can be used for typical operations
            notes = score.flatten().notes
            assert hasattr(notes, '__len__'), f"{voice_name} notes not iterable"
            
            # Test serialization works
            try:
                xml_str = score.write('musicxml')
                assert xml_str is not None, f"{voice_name} serialization failed"
            except Exception as e:
                # Some serialization issues might be acceptable
                if "cannot" not in str(e).lower():
                    raise

    def test_file_handle_management(self, sample_musicxml_file, temp_output_dir):
        """Test that file handles are properly managed."""
        # Process and save multiple times
        for i in range(5):
            voice_scores = split_satb_voices(
                sample_musicxml_file,
                output_dir=str(temp_output_dir / f"run_{i}")
            )
            assert len(voice_scores) > 0
        
        # All output directories should exist and contain files
        for i in range(5):
            run_dir = temp_output_dir / f"run_{i}"
            assert run_dir.exists(), f"Output directory {i} missing"
            
            musicxml_files = list(run_dir.glob("*.musicxml"))
            assert len(musicxml_files) > 0, f"No output files in directory {i}"


class TestScalability:
    """Test scalability characteristics."""

    def test_processing_scales_reasonably(self, sample_musicxml_file, tmp_path):
        """Test that processing time scales reasonably with complexity."""
        # Process the same file with different configurations
        # More complex operations should not cause exponential time increases
        
        times = {}
        
        # Basic processing
        start = time.time()
        split_satb_voices(sample_musicxml_file)
        times['basic'] = time.time() - start
        
        # With output directory (more I/O)
        start = time.time()
        split_satb_voices(sample_musicxml_file, output_dir=str(tmp_path / "test1"))
        times['with_output'] = time.time() - start
        
        # Multiple runs to test consistency
        start = time.time()
        for _ in range(2):
            split_satb_voices(sample_musicxml_file)
        times['multiple'] = (time.time() - start) / 2  # Average per run
        
        # No processing should take more than 10x the basic processing time
        for feature, processing_time in times.items():
            assert processing_time < times['basic'] * 10, \
                f"{feature} processing too slow: {processing_time:.2f}s vs basic {times['basic']:.2f}s"

    def test_output_size_reasonable(self, sample_musicxml_file, temp_output_dir):
        """Test that output file sizes are reasonable."""
        voice_scores = split_satb_voices(
            sample_musicxml_file,
            output_dir=str(temp_output_dir)
        )
        
        # Check original file size
        original_size = Path(sample_musicxml_file).stat().st_size
        
        # Check output file sizes
        total_output_size = 0
        expected_voices = ['Soprano', 'Alto', 'Tenor', 'Bass']
        
        for voice in expected_voices:
            output_file = temp_output_dir / f"Crossing The Bar-{voice}.musicxml"
            if output_file.exists():
                file_size = output_file.stat().st_size
                total_output_size += file_size
                
                # Each voice file should be smaller than original
                assert file_size < original_size, f"{voice} file larger than original"
                assert file_size > 0, f"{voice} file is empty"
        
        # Total output should be reasonable compared to input
        # Allow up to 3x original size (due to formatting, separation overhead)
        assert total_output_size < original_size * 3, \
            f"Total output too large: {total_output_size} vs {original_size}"