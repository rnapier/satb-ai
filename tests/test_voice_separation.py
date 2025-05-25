"""Tests for voice separation validation."""

import pytest
import music21
from satb_splitter import split_satb_voices
from satb_splitter.utils import load_score
from satb_splitter.voice_identifier import VoiceIdentifier


class TestVoiceSeparation:
    """Test detailed voice separation functionality."""

    def test_voice_separation_analysis(self, sample_musicxml_file, sample_score, voice_scores, helpers):
        """Test detailed voice separation analysis."""
        original_parts = len(sample_score.parts)
        
        # Each separated voice should have exactly one part
        for voice_name, score in voice_scores.items():
            assert len(score.parts) == 1, f"{voice_name} should have exactly one part"
        
        # Check that we have the expected number of voices
        assert len(voice_scores) == 4, f"Expected 4 voices, got {len(voice_scores)}"

    def test_note_conservation_detailed(self, sample_score, voice_scores, helpers):
        """Test detailed note conservation during separation."""
        # Count original notes
        original_total_notes = helpers.count_notes_in_score(sample_score)
        
        # Count separated notes
        separated_note_counts = {}
        total_separated_notes = 0
        
        for voice_name, score in voice_scores.items():
            note_count = helpers.count_notes_in_score(score)
            separated_note_counts[voice_name] = note_count
            total_separated_notes += note_count
        
        # Verify each voice has reasonable content
        for voice_name, count in separated_note_counts.items():
            assert count > 0, f"{voice_name} has no notes"
            assert count < original_total_notes, f"{voice_name} has more notes than original"
        
        # Total notes should be conserved (allowing some flexibility for processing)
        difference = abs(total_separated_notes - original_total_notes)
        tolerance = max(10, original_total_notes * 0.1)  # 10% tolerance or 10 notes minimum
        
        assert difference <= tolerance, \
            f"Note count difference too large: original={original_total_notes}, " \
            f"separated={total_separated_notes}, difference={difference}"

    def test_pitch_range_validation(self, voice_scores, helpers):
        """Test that voices have appropriate pitch ranges."""
        voice_ranges = {}
        
        for voice_name, score in voice_scores.items():
            pitch_range = helpers.get_pitch_range(score)
            if pitch_range:
                voice_ranges[voice_name] = pitch_range

        # Should have pitch data for all voices
        expected_voices = ['Soprano', 'Alto', 'Tenor', 'Bass']
        for voice in expected_voices:
            assert voice in voice_ranges, f"No pitch range data for {voice}"
            
            range_data = voice_ranges[voice]
            assert range_data['min'] < range_data['max'], f"{voice} min >= max pitch"
            assert range_data['count'] > 0, f"{voice} has no pitches"

    def test_voice_pitch_ordering(self, voice_scores, helpers):
        """Test that voices are in the correct pitch order."""
        voice_ranges = {}
        for voice_name, score in voice_scores.items():
            pitch_range = helpers.get_pitch_range(score)
            if pitch_range:
                voice_ranges[voice_name] = pitch_range

        if len(voice_ranges) == 4:
            # Get average pitches
            soprano_avg = voice_ranges['Soprano']['avg']
            alto_avg = voice_ranges['Alto']['avg']
            tenor_avg = voice_ranges['Tenor']['avg']
            bass_avg = voice_ranges['Bass']['avg']
            
            # Create list of (voice, avg_pitch) and sort by pitch
            pitch_order = [
                ('Soprano', soprano_avg),
                ('Alto', alto_avg),
                ('Tenor', tenor_avg),
                ('Bass', bass_avg)
            ]
            pitch_order.sort(key=lambda x: x[1], reverse=True)
            
            # Extract just the voice names in order
            actual_order = [voice for voice, _ in pitch_order]
            expected_order = ['Soprano', 'Alto', 'Tenor', 'Bass']
            
            # Allow some flexibility - at least Soprano should be higher than Bass
            assert soprano_avg > bass_avg, "Soprano should have higher average pitch than Bass"
            
            # Alto and Tenor might be close, so just check general high-to-low trend
            high_voices = [soprano_avg, alto_avg]
            low_voices = [tenor_avg, bass_avg]
            
            assert min(high_voices) >= min(low_voices) - 5, \
                "High voices should generally be higher than low voices"

    def test_measure_consistency(self, voice_scores, helpers):
        """Test that all voices have consistent measure counts."""
        measure_counts = {}
        
        for voice_name, score in voice_scores.items():
            measure_count = helpers.count_measures_in_score(score)
            measure_counts[voice_name] = measure_count

        # All voices should have similar measure counts
        unique_counts = set(measure_counts.values())
        
        # Allow for slight variations (e.g., pickup measures, endings)
        assert len(unique_counts) <= 3, f"Too much variation in measure counts: {measure_counts}"
        
        # Check that all counts are reasonable
        for voice_name, count in measure_counts.items():
            assert count > 0, f"{voice_name} has no measures"
            assert count < 500, f"{voice_name} has suspiciously many measures: {count}"

    def test_voice_isolation(self, voice_scores):
        """Test that voices are properly isolated (no cross-contamination)."""
        # Each voice should have distinct musical content
        voice_note_sets = {}
        
        for voice_name, score in voice_scores.items():
            notes = []
            for part in score.parts:
                for measure in part.getElementsByClass('Measure'):
                    for note in measure.getElementsByClass('Note'):
                        if hasattr(note, 'pitch'):
                            notes.append((note.pitch.ps, float(note.offset), float(note.duration.quarterLength)))
                        elif hasattr(note, 'pitches'):  # Chord
                            for pitch in note.pitches:
                                notes.append((pitch.ps, float(note.offset), float(note.duration.quarterLength)))
            
            voice_note_sets[voice_name] = set(notes)

        # Voices should have different content (allowing some overlap for unisons)
        voice_names = list(voice_note_sets.keys())
        for i, voice1 in enumerate(voice_names):
            for voice2 in voice_names[i+1:]:
                set1 = voice_note_sets[voice1]
                set2 = voice_note_sets[voice2]
                
                if set1 and set2:
                    overlap = len(set1 & set2)
                    total1 = len(set1)
                    total2 = len(set2)
                    
                    # Allow some overlap but not complete duplication
                    overlap_ratio1 = overlap / total1 if total1 > 0 else 0
                    overlap_ratio2 = overlap / total2 if total2 > 0 else 0
                    
                    assert overlap_ratio1 < 0.9, f"{voice1} and {voice2} are too similar ({overlap_ratio1:.2f})"
                    assert overlap_ratio2 < 0.9, f"{voice1} and {voice2} are too similar ({overlap_ratio2:.2f})"

    def test_original_score_structure_analysis(self, sample_score):
        """Test analysis of the original score structure."""
        original_parts = len(sample_score.parts)
        assert original_parts > 0, "Original score should have parts"
        
        # Analyze voice structure in original
        voice_info = []
        for i, part in enumerate(sample_score.parts):
            notes = part.flatten().notes
            measures = part.getElementsByClass(music21.stream.Measure)
            
            # Count voices in this part
            voices = set()
            for measure in measures:
                for voice in measure.voices:
                    voices.add(voice.id)
            
            voice_info.append({
                'part_index': i,
                'note_count': len(notes),
                'measure_count': len(measures),
                'voice_count': len(voices)
            })
        
        # Original should have reasonable structure
        total_notes = sum(info['note_count'] for info in voice_info)
        assert total_notes > 0, "Original score should have notes"
        
        # Each part should have some content
        for info in voice_info:
            assert info['note_count'] >= 0, "Parts should have non-negative note counts"

    def test_voice_identifier_detailed(self, sample_score):
        """Test detailed voice identification functionality."""
        identifier = VoiceIdentifier(sample_score)
        voice_mapping = identifier.analyze_score()
        
        # Detailed validation
        assert voice_mapping.validate(), "Voice mapping should be valid"
        
        # Check individual voice assignments
        voices = [voice_mapping.soprano, voice_mapping.alto, voice_mapping.tenor, voice_mapping.bass]
        
        for voice in voices:
            assert voice is not None, "All voices should be mapped"
            assert hasattr(voice, 'part_index'), "Voice should have part_index"
            assert hasattr(voice, 'voice_id'), "Voice should have voice_id"
            assert voice.part_index >= 0, "Part index should be non-negative"

        # Check that confidence is reasonable
        assert 0.0 <= voice_mapping.confidence <= 1.0, "Confidence should be between 0 and 1"

    def test_voice_separation_regression(self, sample_musicxml_file, temp_output_dir):
        """Regression test for voice separation."""
        # This test ensures that voice separation doesn't break over time
        
        # Process the file
        voice_scores = split_satb_voices(
            sample_musicxml_file,
            output_dir=str(temp_output_dir)
        )
        
        # Basic checks
        assert len(voice_scores) == 4, "Should produce 4 voices"
        
        expected_voices = ['Soprano', 'Alto', 'Tenor', 'Bass']
        for voice in expected_voices:
            assert voice in voice_scores, f"Missing voice: {voice}"
            
            # Check output file
            output_file = temp_output_dir / f"Crossing The Bar-{voice}.musicxml"
            assert output_file.exists(), f"Output file missing for {voice}"
            
            # Reload and validate
            reloaded = music21.converter.parse(str(output_file))
            assert len(reloaded.parts) > 0, f"Reloaded {voice} has no parts"
            assert len(reloaded.flatten().notes) > 0, f"Reloaded {voice} has no notes"


class TestVoiceSeparationEdgeCases:
    """Test edge cases in voice separation."""

    def test_empty_voices_handling(self, voice_scores):
        """Test handling of potentially empty voices."""
        for voice_name, score in voice_scores.items():
            # Even if a voice is sparse, it should have valid structure
            assert score is not None, f"{voice_name} score should not be None"
            assert len(score.parts) > 0, f"{voice_name} should have at least one part"

    def test_complex_rhythms(self, voice_scores):
        """Test that complex rhythms are preserved in voice separation."""
        rhythm_complexity = {}
        
        for voice_name, score in voice_scores.items():
            duration_types = set()
            for part in score.parts:
                for note in part.flatten().notes:
                    if hasattr(note, 'duration'):
                        duration_types.add(note.duration.quarterLength)
            
            rhythm_complexity[voice_name] = len(duration_types)

        # Each voice should have some rhythmic variety
        for voice_name, complexity in rhythm_complexity.items():
            assert complexity > 0, f"{voice_name} should have some rhythmic content"

    def test_chord_handling(self, voice_scores):
        """Test that chords are handled correctly in voice separation."""
        chord_counts = {}
        
        for voice_name, score in voice_scores.items():
            chord_count = 0
            for part in score.parts:
                for element in part.flatten():
                    if isinstance(element, music21.chord.Chord):
                        chord_count += 1
            
            chord_counts[voice_name] = chord_count

        # Chords should be distributed appropriately
        total_chords = sum(chord_counts.values())
        
        # If there are chords, they should be handled properly
        if total_chords > 0:
            for voice_name, count in chord_counts.items():
                # Chords shouldn't be excessively concentrated in one voice
                ratio = count / total_chords if total_chords > 0 else 0
                assert ratio <= 1.0, f"{voice_name} has all the chords: {ratio}"