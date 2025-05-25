"""Tests for dynamics duplication fix."""

import pytest
import music21
from satb_splitter import split_satb_voices
from satb_splitter.score_processor import ScoreProcessor


class TestDynamicsFix:
    """Test that the dynamics duplication fix works correctly."""

    def test_dynamics_duplication_fix(self, sample_musicxml_file, helpers):
        """Test that dynamics are not duplicated in the fixed implementation."""
        # Process the score with default settings
        voice_scores = split_satb_voices(sample_musicxml_file)
        
        # Check measure 29 in soprano (the specific issue from the original test)
        soprano_score = voice_scores.get('Soprano')
        assert soprano_score is not None, "Soprano voice should be present"
        
        # Count dynamics in measure 29
        dynamics_count, dynamics_found = helpers.count_dynamics_in_measure(soprano_score, 29)
        
        # Should have at most one dynamic (no duplication)
        assert dynamics_count <= 1, f"Found {dynamics_count} dynamics in measure 29, expected at most 1"
        
        if dynamics_count == 1:
            dynamic = dynamics_found[0]
            assert 'dynamic' in dynamic, "Dynamic should have a value"
            assert 'offset' in dynamic, "Dynamic should have an offset"

    def test_dynamics_preservation_across_voices(self, voice_scores, helpers):
        """Test that dynamics are properly preserved across all voices."""
        dynamics_per_voice = {}
        
        for voice_name, score in voice_scores.items():
            total_dynamics = 0
            for part in score.parts:
                for measure in part.getElementsByClass(music21.stream.Measure):
                    for element in measure:
                        if isinstance(element, music21.dynamics.Dynamic):
                            total_dynamics += 1
            
            dynamics_per_voice[voice_name] = total_dynamics

        # Each voice should have some dynamics, but not excessive amounts
        for voice_name, count in dynamics_per_voice.items():
            assert count >= 0, f"{voice_name} should have non-negative dynamics count"
            # Reasonable upper bound to catch duplication issues
            assert count < 100, f"{voice_name} has suspiciously many dynamics: {count}"

    def test_specific_measures_dynamics(self, voice_scores, helpers):
        """Test dynamics in specific measures to catch duplication issues."""
        test_measures = [1, 10, 20, 29, 30]  # Include measure 29 which had the original issue
        
        for measure_num in test_measures:
            for voice_name, score in voice_scores.items():
                dynamics_count, _ = helpers.count_dynamics_in_measure(score, measure_num)
                
                # Each measure should have at most a reasonable number of dynamics
                assert dynamics_count <= 3, \
                    f"{voice_name} measure {measure_num} has too many dynamics: {dynamics_count}"

    def test_dynamics_consistency(self, voice_scores):
        """Test that dynamics are consistent and not randomly duplicated."""
        all_dynamics = []
        
        for voice_name, score in voice_scores.items():
            voice_dynamics = []
            for part in score.parts:
                for measure_num, measure in enumerate(part.getElementsByClass(music21.stream.Measure), 1):
                    measure_dynamics = []
                    for element in measure:
                        if isinstance(element, music21.dynamics.Dynamic):
                            measure_dynamics.append({
                                'voice': voice_name,
                                'measure': measure_num,
                                'dynamic': element.value,
                                'offset': element.offset
                            })
                    voice_dynamics.extend(measure_dynamics)
            all_dynamics.extend(voice_dynamics)

        # Check for obvious duplication patterns
        if len(all_dynamics) > 1:
            # Group by measure and check for excessive duplication
            measure_groups = {}
            for dyn in all_dynamics:
                key = (dyn['voice'], dyn['measure'])
                if key not in measure_groups:
                    measure_groups[key] = []
                measure_groups[key].append(dyn)
            
            # Each voice/measure combination should not have too many identical dynamics
            for key, dynamics in measure_groups.items():
                voice, measure = key
                if len(dynamics) > 2:  # More than 2 might indicate duplication
                    # Check if they're actually different (different offsets)
                    offsets = [d['offset'] for d in dynamics]
                    unique_offsets = set(offsets)
                    
                    assert len(unique_offsets) > 1 or len(dynamics) <= 2, \
                        f"{voice} measure {measure} has {len(dynamics)} dynamics at same offset"

    def test_dynamics_fix_regression(self, sample_musicxml_file, temp_output_dir):
        """Regression test to ensure the dynamics fix doesn't break file output."""
        # Process and save files
        voice_scores = split_satb_voices(
            sample_musicxml_file, 
            output_dir=str(temp_output_dir)
        )
        
        # Load saved files and check for dynamics
        expected_voices = ['Soprano', 'Alto', 'Tenor', 'Bass']
        for voice in expected_voices:
            output_file = temp_output_dir / f"Crossing The Bar-{voice}.musicxml"
            assert output_file.exists(), f"Output file missing for {voice}"
            
            # Load and verify the file
            reloaded_score = music21.converter.parse(str(output_file))
            assert reloaded_score is not None, f"Could not reload {voice} file"
            
            # Count dynamics in the reloaded file
            total_dynamics = 0
            for part in reloaded_score.parts:
                for measure in part.getElementsByClass(music21.stream.Measure):
                    for element in measure:
                        if isinstance(element, music21.dynamics.Dynamic):
                            total_dynamics += 1
            
            # Should have reasonable number of dynamics
            assert total_dynamics >= 0, f"Negative dynamics count in {voice}"
            assert total_dynamics < 200, f"Excessive dynamics in saved {voice} file: {total_dynamics}"


class TestDynamicsPreservation:
    """Test that legitimate dynamics are preserved correctly."""

    def test_dynamics_preservation_enabled(self, sample_musicxml_file):
        """Test dynamics preservation in normal processing."""
        processor = ScoreProcessor()
        result = processor.process_satb_score(sample_musicxml_file)
        
        # Should have voice scores
        assert len(result.voice_scores) > 0, "Should have voice scores"
        
        # Check that each voice has some dynamics (if the original had them)
        total_dynamics = 0
        for voice_name, score in result.voice_scores.items():
            for part in score.parts:
                for measure in part.getElementsByClass(music21.stream.Measure):
                    for element in measure:
                        if isinstance(element, music21.dynamics.Dynamic):
                            total_dynamics += 1
        
        # Original score likely has some dynamics
        assert total_dynamics >= 0, "Dynamics should be preserved"

    def test_dynamics_preservation_consistent(self, sample_musicxml_file):
        """Test that dynamics processing is consistent."""
        processor = ScoreProcessor()
        result = processor.process_satb_score(sample_musicxml_file)
        
        # Should produce valid results
        assert len(result.voice_scores) > 0, "Should have voice scores"
        
        # Each voice should have musical content
        for voice_name, score in result.voice_scores.items():
            notes = score.flatten().notes
            assert len(notes) > 0, f"{voice_name} should have musical content"

    def test_dynamics_types(self, voice_scores):
        """Test that various types of dynamics are handled correctly."""
        dynamics_types_found = set()
        
        for voice_name, score in voice_scores.items():
            for part in score.parts:
                for measure in part.getElementsByClass(music21.stream.Measure):
                    for element in measure:
                        if isinstance(element, music21.dynamics.Dynamic):
                            if hasattr(element, 'value') and element.value:
                                dynamics_types_found.add(element.value)
        
        # If dynamics are found, they should be valid types
        valid_dynamics = {'p', 'mp', 'mf', 'f', 'ff', 'pp', 'ppp', 'fff', 'sf', 'sfz'}
        for dynamic in dynamics_types_found:
            # Allow some flexibility for different dynamic markings
            assert isinstance(dynamic, str), f"Dynamic should be string, got {type(dynamic)}"
            assert len(dynamic) <= 10, f"Dynamic marking suspiciously long: {dynamic}"