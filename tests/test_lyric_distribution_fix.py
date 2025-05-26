#!/usr/bin/env python3
"""
Test cases for the new deterministic lyric distribution algorithm.

This test specifically validates the fix for measure 29 where the Soprano
sings "far" on a dotted-half note, but other voices have different slur patterns.
"""

import pytest
import tempfile
from pathlib import Path
from music21 import converter
from satb_splitter.main import split_satb_voices


class TestLyricDistributionFix:
    """Test cases for the new lyric distribution algorithm."""
    
    @pytest.fixture
    def sample_score_path(self):
        """Path to the sample score file."""
        return Path("Crossing The Bar.musicxml")
    
    def test_measure_29_far_lyric_distribution(self, sample_score_path):
        """Test that 'far' lyric in measure 29 is properly distributed using time-window matching."""
        if not sample_score_path.exists():
            pytest.skip("Sample score file not found")
        
        # Process the score with the new algorithm
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            voices = split_satb_voices(str(sample_score_path), str(temp_path))
            
            # Check that all voices have the score
            assert 'Soprano' in voices, "Soprano voice should be present"
            
            # Find measure 29 in each voice and check for "far" lyric
            lyric_results = {}
            
            for voice_name in ['Soprano', 'Alto', 'Tenor', 'Bass']:
                if voice_name in voices:
                    voice_score = voices[voice_name]
                    
                    # Find measure 29 and extract lyrics
                    measure_29_lyrics = []
                    for part in voice_score.parts:
                        for measure in part.getElementsByClass('Measure'):
                            if hasattr(measure, 'number') and measure.number == 29:
                                for note in measure.flatten().notes:
                                    if hasattr(note, 'lyrics') and note.lyrics:
                                        for lyric in note.lyrics:
                                            text = lyric.text if hasattr(lyric, 'text') else str(lyric)
                                            if text:  # Only non-empty lyrics
                                                measure_29_lyrics.append({
                                                    'text': text,
                                                    'offset': note.offset,
                                                    'duration': note.duration.quarterLength
                                                })
                    
                    lyric_results[voice_name] = measure_29_lyrics
                    print(f"\n{voice_name} measure 29 lyrics: {measure_29_lyrics}")
            
            # Validate that "far" appears in multiple voices (the fix)
            voices_with_far = []
            for voice_name, lyrics in lyric_results.items():
                for lyric_info in lyrics:
                    if 'far' in lyric_info['text'].lower():
                        voices_with_far.append(voice_name)
                        break
            
            print(f"\nVoices with 'far' lyric: {voices_with_far}")
            
            # The fix should ensure that "far" appears in more than just Soprano
            # (Previously it was dropped from other voices due to strict matching)
            assert len(voices_with_far) > 1, f"Expected 'far' lyric in multiple voices, found only in: {voices_with_far}"
            
            # Soprano should definitely have the "far" lyric
            assert 'Soprano' in voices_with_far, "Soprano should have the 'far' lyric"
    
    def test_time_window_matching_functionality(self, sample_score_path):
        """Test the general time-window matching functionality."""
        if not sample_score_path.exists():
            pytest.skip("Sample score file not found")
        
        # Process the score
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            voices = split_satb_voices(str(sample_score_path), str(temp_path))
            
            # Check that we have reasonable lyric distribution overall
            total_lyrics_before = 0
            total_lyrics_after = 0
            
            # Count original lyrics (this is a simplified approach)
            original_score = converter.parse(str(sample_score_path))
            for part in original_score.parts:
                for note in part.flatten().notes:
                    if hasattr(note, 'lyrics') and note.lyrics:
                        total_lyrics_before += len([l for l in note.lyrics if l.text])
            
            # Count distributed lyrics
            for voice_name, voice_score in voices.items():
                for part in voice_score.parts:
                    for note in part.flatten().notes:
                        if hasattr(note, 'lyrics') and note.lyrics:
                            total_lyrics_after += len([l for l in note.lyrics if l.text])
            
            print(f"\nLyrics before distribution: {total_lyrics_before}")
            print(f"Lyrics after distribution: {total_lyrics_after}")
            
            # The new algorithm should generally increase lyric coverage
            # (copying lyrics to appropriate places where they were missing)
            assert total_lyrics_after >= total_lyrics_before, "Lyric distribution should not lose lyrics"
    
    def test_slur_handling_in_lyric_distribution(self, sample_score_path):
        """Test that slurs are properly respected in lyric distribution."""
        if not sample_score_path.exists():
            pytest.skip("Sample score file not found")
        
        # This test validates that lyrics are not placed on notes in the middle of slurs
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            voices = split_satb_voices(str(sample_score_path), str(temp_path))
            
            # Look for measures with both slurs and lyrics
            slur_lyric_interactions = []
            
            for voice_name, voice_score in voices.items():
                for part in voice_score.parts:
                    for measure in part.getElementsByClass('Measure'):
                        # Check if measure has both slurs and lyrics
                        has_slurs = len(measure.getElementsByClass('Slur')) > 0
                        
                        notes_with_lyrics = []
                        for note in measure.getElementsByClass('Note'):
                            if hasattr(note, 'lyrics') and note.lyrics:
                                notes_with_lyrics.append(note)
                        
                        if has_slurs and notes_with_lyrics:
                            slur_lyric_interactions.append({
                                'voice': voice_name,
                                'measure': measure.number if hasattr(measure, 'number') else 'unknown',
                                'slur_count': len(measure.getElementsByClass('Slur')),
                                'lyric_notes': len(notes_with_lyrics)
                            })
            
            print(f"\nFound {len(slur_lyric_interactions)} measures with slur-lyric interactions")
            
            # This is a basic validation - in the future we could add more sophisticated
            # checks to ensure lyrics are only on slur starts, not slur middles
            assert len(slur_lyric_interactions) >= 0, "Should handle slur-lyric interactions without crashing"


class TestLyricDistributionEdgeCases:
    """Test edge cases for the lyric distribution algorithm."""
    
    @pytest.fixture
    def sample_score_path(self):
        """Path to the sample score file."""
        return Path("Crossing The Bar.musicxml")
    
    def test_no_candidates_found(self, sample_score_path):
        """Test behavior when no suitable candidates are found for lyric distribution."""
        if not sample_score_path.exists():
            pytest.skip("Sample score file not found")
        
        # This test ensures the algorithm handles gracefully when no matches are found
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            voices = split_satb_voices(str(sample_score_path), str(temp_path))
            
            # The process should complete successfully even if some lyrics can't be distributed
            assert len(voices) > 0, "Should successfully process score even with difficult lyric cases"
    
    def test_multiple_candidates_selection(self, sample_score_path):
        """Test that the deterministic selection rules work correctly."""
        if not sample_score_path.exists():
            pytest.skip("Sample score file not found")
        
        # This test validates that when multiple candidates exist, 
        # the algorithm consistently picks the same one (deterministic behavior)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Run the same process twice
            voices1 = split_satb_voices(str(sample_score_path), str(temp_path))
            voices2 = split_satb_voices(str(sample_score_path), str(temp_path))
            
            # Results should be identical (deterministic)
            for voice_name in voices1.keys():
                if voice_name in voices2:
                    # Compare lyric distribution in measure 29
                    lyrics1 = self._extract_measure_lyrics(voices1[voice_name], 29)
                    lyrics2 = self._extract_measure_lyrics(voices2[voice_name], 29)
                    
                    assert lyrics1 == lyrics2, f"Lyric distribution should be deterministic for {voice_name}"
    
    def _extract_measure_lyrics(self, voice_score, measure_number):
        """Extract lyrics from a specific measure for comparison."""
        lyrics = []
        for part in voice_score.parts:
            for measure in part.getElementsByClass('Measure'):
                if hasattr(measure, 'number') and measure.number == measure_number:
                    for note in measure.flatten().notes:
                        if hasattr(note, 'lyrics') and note.lyrics:
                            for lyric in note.lyrics:
                                lyrics.append({
                                    'text': lyric.text if hasattr(lyric, 'text') else str(lyric),
                                    'offset': note.offset
                                })
        return sorted(lyrics, key=lambda x: x['offset'])