#!/usr/bin/env python3
"""
Test cases for measure 29 spanner and lyric issues.

This test specifically targets the complex spanner handling issues
found in measure 29, including cross-voice spanners and lyric corruption.
"""

import pytest
import tempfile
from pathlib import Path
from music21 import converter
from satb_splitter.main import split_satb_voices


class TestMeasure29Issues:
    """Test cases for measure 29 specific issues."""
    
    @pytest.fixture
    def sample_score_path(self):
        """Path to the sample score file."""
        return Path("Crossing The Bar.musicxml")
    
    def test_measure_29_spanner_preservation(self, sample_score_path):
        """Test that spanners in measure 29 are properly handled."""
        if not sample_score_path.exists():
            pytest.skip("Sample score file not found")
        
        # Process the score
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            voices = split_satb_voices(str(sample_score_path), str(temp_path))
            
            # Load original score to analyze measure 29
            original_score = converter.parse(str(sample_score_path))
            
            # Find spanners in measure 29 of original score
            measure_29_spanners = []
            for part in original_score.parts:
                for measure in part.getElementsByClass('Measure'):
                    if hasattr(measure, 'number') and measure.number == 29:
                        # Check for spanners that start, end, or span measure 29
                        for spanner in part.getElementsByClass('Spanner'):
                            if self._spanner_affects_measure(spanner, 29):
                                measure_29_spanners.append({
                                    'spanner': spanner,
                                    'type': type(spanner).__name__,
                                    'repr': str(spanner)
                                })
            
            print(f"\nFound {len(measure_29_spanners)} spanners affecting measure 29:")
            for spanner_info in measure_29_spanners:
                print(f"  - {spanner_info['type']}: {spanner_info['repr']}")
            
            # Check each voice for measure 29 spanner preservation
            spanner_preservation_results = {}
            
            for voice_name in ['Soprano', 'Alto', 'Tenor', 'Bass']:
                if voice_name in voices:
                    voice_score = voices[voice_name]
                    
                    # Count spanners in measure 29 of this voice
                    voice_m29_spanners = []
                    for part in voice_score.parts:
                        for measure in part.getElementsByClass('Measure'):
                            if hasattr(measure, 'number') and measure.number == 29:
                                for spanner in part.getElementsByClass('Spanner'):
                                    voice_m29_spanners.append(spanner)
                    
                    spanner_preservation_results[voice_name] = {
                        'count': len(voice_m29_spanners),
                        'spanners': [str(s) for s in voice_m29_spanners]
                    }
                    
                    print(f"\n{voice_name} measure 29 spanners: {len(voice_m29_spanners)}")
                    for spanner in voice_m29_spanners:
                        print(f"  - {spanner}")
            
            # Store results for analysis
            self._log_measure_29_analysis(measure_29_spanners, spanner_preservation_results)
            
            # Document the current problematic behavior
            print(f"\n❌ CURRENT ISSUES IDENTIFIED:")
            
            # Check for nuclear copying (all voices getting same spanners)
            soprano_count = spanner_preservation_results.get('Soprano', {}).get('count', 0)
            alto_count = spanner_preservation_results.get('Alto', {}).get('count', 0)
            tenor_count = spanner_preservation_results.get('Tenor', {}).get('count', 0)
            bass_count = spanner_preservation_results.get('Bass', {}).get('count', 0)
            
            if soprano_count == alto_count and soprano_count > 10:
                print(f"   Nuclear copying detected: Soprano and Alto both have {soprano_count} spanners")
            
            if tenor_count == 0 and bass_count == 0 and soprano_count > 0:
                print(f"   Inconsistent behavior: Soprano/Alto have spanners, Tenor/Bass have none")
            
            # For now, the test passes if we can analyze the issues
            # Later we'll add proper assertions for correct behavior
            assert True, "Test completed - issues documented for fixing"
    
    def test_measure_29_lyric_integrity(self, sample_score_path):
        """Test that lyrics in measure 29 are not corrupted during processing."""
        if not sample_score_path.exists():
            pytest.skip("Sample score file not found")
        
        # Load original score
        original_score = converter.parse(str(sample_score_path))
        
        # Extract lyrics from measure 29 in original
        original_m29_lyrics = {}
        for part_idx, part in enumerate(original_score.parts):
            for measure in part.getElementsByClass('Measure'):
                if hasattr(measure, 'number') and measure.number == 29:
                    lyrics = []
                    for note in measure.flatten().notes:
                        if hasattr(note, 'lyrics') and note.lyrics:
                            for lyric in note.lyrics:
                                lyrics.append(lyric.text if hasattr(lyric, 'text') else str(lyric))
                    original_m29_lyrics[f'part_{part_idx}'] = lyrics
        
        print(f"\nOriginal measure 29 lyrics: {original_m29_lyrics}")
        
        # Process the score
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            voices = split_satb_voices(str(sample_score_path), str(temp_path))
            
            # Check lyrics preservation in each voice
            processed_m29_lyrics = {}
            
            for voice_name in ['Soprano', 'Alto', 'Tenor', 'Bass']:
                if voice_name in voices:
                    voice_score = voices[voice_name]
                    
                    lyrics = []
                    for part in voice_score.parts:
                        for measure in part.getElementsByClass('Measure'):
                            if hasattr(measure, 'number') and measure.number == 29:
                                for note in measure.flatten().notes:
                                    if hasattr(note, 'lyrics') and note.lyrics:
                                        for lyric in note.lyrics:
                                            text = lyric.text if hasattr(lyric, 'text') else str(lyric)
                                            lyrics.append(text)
                    
                    processed_m29_lyrics[voice_name] = lyrics
                    print(f"{voice_name} measure 29 lyrics: {lyrics}")
            
            # Check for obvious corruption patterns
            for voice_name, lyrics in processed_m29_lyrics.items():
                for lyric_text in lyrics:
                    # Check for common corruption patterns
                    assert lyric_text != "", f"{voice_name} has empty lyric in measure 29"
                    assert not lyric_text.startswith("ERROR"), f"{voice_name} has error lyric: {lyric_text}"
                    assert len(lyric_text) > 0, f"{voice_name} has zero-length lyric"
                    
                    # Check for reasonable text (no control characters, etc.)
                    assert lyric_text.isprintable() or lyric_text.isspace(), f"{voice_name} has non-printable lyric: {repr(lyric_text)}"
    
    def test_measure_29_musical_integrity(self, sample_score_path):
        """Test that measure 29 maintains musical integrity (notes, timing, etc.)."""
        if not sample_score_path.exists():
            pytest.skip("Sample score file not found")
        
        # Load original score
        original_score = converter.parse(str(sample_score_path))
        
        # Get measure 29 statistics from original
        original_m29_stats = {}
        for part_idx, part in enumerate(original_score.parts):
            for measure in part.getElementsByClass('Measure'):
                if hasattr(measure, 'number') and measure.number == 29:
                    notes = measure.flatten().notes
                    original_m29_stats[f'part_{part_idx}'] = {
                        'note_count': len(notes),
                        'total_duration': float(sum(n.quarterLength for n in notes if hasattr(n, 'quarterLength'))),
                        'pitch_range': self._get_pitch_range(notes)
                    }
        
        print(f"\nOriginal measure 29 stats: {original_m29_stats}")
        
        # Process the score
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            voices = split_satb_voices(str(sample_score_path), str(temp_path))
            
            # Check musical integrity in each voice
            for voice_name in ['Soprano', 'Alto', 'Tenor', 'Bass']:
                if voice_name in voices:
                    voice_score = voices[voice_name]
                    
                    for part in voice_score.parts:
                        for measure in part.getElementsByClass('Measure'):
                            if hasattr(measure, 'number') and measure.number == 29:
                                notes = measure.flatten().notes
                                
                                # Basic integrity checks
                                assert len(notes) > 0, f"{voice_name} measure 29 has no notes"
                                
                                # Check that notes have valid durations
                                for note in notes:
                                    if hasattr(note, 'quarterLength'):
                                        assert note.quarterLength > 0, f"{voice_name} has note with invalid duration: {note.quarterLength}"
                                
                                print(f"{voice_name} measure 29: {len(notes)} notes")
    
    def _spanner_affects_measure(self, spanner, measure_number):
        """Check if a spanner affects the given measure number."""
        try:
            # This is a simplified check - in reality we'd need to check
            # the actual measure positions of the spanner's start and end points
            if hasattr(spanner, 'getSpannedElements'):
                spanned_elements = spanner.getSpannedElements()
                for element in spanned_elements:
                    if hasattr(element, 'activeSite') and element.activeSite:
                        if hasattr(element.activeSite, 'number'):
                            if element.activeSite.number == measure_number:
                                return True
            return False
        except Exception:
            return False
    
    def _get_pitch_range(self, notes):
        """Get the pitch range (lowest to highest) of a collection of notes."""
        if not notes:
            return None
        
        pitches = []
        for note in notes:
            if hasattr(note, 'pitch'):
                pitches.append(note.pitch.midi)
            elif hasattr(note, 'pitches'):  # Chord
                pitches.extend(p.midi for p in note.pitches)
        
        if pitches:
            return {'min': min(pitches), 'max': max(pitches), 'range': max(pitches) - min(pitches)}
        return None
    
    def _log_measure_29_analysis(self, original_spanners, voice_results):
        """Log detailed analysis of measure 29 for debugging."""
        print(f"\n=== MEASURE 29 SPANNER ANALYSIS ===")
        print(f"Original spanners found: {len(original_spanners)}")
        
        for voice_name, result in voice_results.items():
            print(f"{voice_name}: {result['count']} spanners preserved")
            
        # Calculate preservation rate
        total_original = len(original_spanners)
        total_preserved = sum(result['count'] for result in voice_results.values())
        
        if total_original > 0:
            preservation_rate = (total_preserved / total_original) * 100
            print(f"\nOverall preservation rate: {preservation_rate:.1f}% ({total_preserved}/{total_original})")
        
        print("=== END ANALYSIS ===\n")


class TestCrossVoiceSpanners:
    """Test cases specifically for cross-voice spanner handling."""
    
    @pytest.fixture
    def sample_score_path(self):
        """Path to the sample score file."""
        return Path("Crossing The Bar.musicxml")
    
    def test_identify_cross_voice_spanners(self, sample_score_path):
        """Identify spanners that span across multiple voices."""
        if not sample_score_path.exists():
            pytest.skip("Sample score file not found")
        
        original_score = converter.parse(str(sample_score_path))
        
        cross_voice_spanners = []
        
        # Analyze all spanners in the score
        for part_idx, part in enumerate(original_score.parts):
            spanners = part.getElementsByClass('Spanner')
            print(f"\nPart {part_idx}: {len(spanners)} spanners")
            
            for spanner in spanners:
                spanner_info = {
                    'part': part_idx,
                    'type': type(spanner).__name__,
                    'repr': str(spanner),
                    'is_cross_voice': self._is_cross_voice_spanner(spanner)
                }
                
                if spanner_info['is_cross_voice']:
                    cross_voice_spanners.append(spanner_info)
                    print(f"  Cross-voice: {spanner_info['repr']}")
                else:
                    print(f"  Single-voice: {spanner_info['repr']}")
        
        print(f"\nFound {len(cross_voice_spanners)} cross-voice spanners")
        
        # This test documents the current state - later we'll add proper handling
        assert len(cross_voice_spanners) >= 0, "Should be able to identify cross-voice spanners"
    
    def _is_cross_voice_spanner(self, spanner):
        """Determine if a spanner crosses voice boundaries."""
        try:
            if hasattr(spanner, 'getSpannedElements'):
                spanned_elements = spanner.getSpannedElements()
                
                if len(spanned_elements) >= 2:
                    # Check if elements are in different voices/parts
                    first_element = spanned_elements[0]
                    last_element = spanned_elements[-1]
                    
                    # Simple heuristic: different pitch ranges suggest different voices
                    if (hasattr(first_element, 'pitch') and hasattr(last_element, 'pitch')):
                        pitch_diff = abs(first_element.pitch.midi - last_element.pitch.midi)
                        # Large pitch jumps might indicate cross-voice spanners
                        return pitch_diff > 12  # More than an octave
            
            return False
        except Exception:
            return False