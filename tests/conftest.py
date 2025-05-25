"""Pytest configuration and fixtures for satb_splitter tests."""

import pytest
import os
from pathlib import Path
import tempfile
import music21
from satb_splitter import split_satb_voices
from satb_splitter.score_processor import ScoreProcessor
from satb_splitter.utils import load_score


@pytest.fixture(scope="session")
def test_data_dir():
    """Path to the test data directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def sample_musicxml_file(test_data_dir):
    """Path to the sample MusicXML file."""
    file_path = test_data_dir / "Crossing The Bar.musicxml"
    if not file_path.exists():
        pytest.skip(f"Test file {file_path} not found")
    return str(file_path)


@pytest.fixture(scope="session")
def sample_score(sample_musicxml_file):
    """Load the sample score for testing."""
    return load_score(sample_musicxml_file)


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def score_processor():
    """Create a ScoreProcessor instance."""
    return ScoreProcessor()


@pytest.fixture
def voice_scores(sample_musicxml_file):
    """Process the sample file and return voice scores."""
    return split_satb_voices(sample_musicxml_file)


@pytest.fixture
def expected_voices():
    """List of expected voice names."""
    return ['Soprano', 'Alto', 'Tenor', 'Bass']


class TestHelpers:
    """Helper methods for testing."""
    
    @staticmethod
    def count_notes_in_score(score):
        """Count total notes in a score."""
        return len(score.flatten().notes)
    
    @staticmethod
    def count_measures_in_score(score):
        """Count measures in a score."""
        if not score.parts:
            return 0
        return len(score.parts[0].getElementsByClass(music21.stream.Measure))
    
    @staticmethod
    def get_pitch_range(score):
        """Get pitch range statistics for a score."""
        notes = score.flatten().notes
        if not notes:
            return None
        
        pitches = []
        for note in notes:
            if hasattr(note, 'pitch'):
                pitches.append(note.pitch.ps)
            elif hasattr(note, 'pitches'):  # Chord
                pitches.extend([p.ps for p in note.pitches])
        
        if not pitches:
            return None
        
        return {
            'min': min(pitches),
            'max': max(pitches),
            'avg': sum(pitches) / len(pitches),
            'count': len(pitches)
        }
    
    @staticmethod
    def get_lyrics_from_measure(score, measure_number):
        """Extract lyrics from a specific measure."""
        lyrics = []
        for part in score.parts:
            measures = list(part.getElementsByClass('Measure'))
            if len(measures) >= measure_number:
                measure = measures[measure_number - 1]
                
                for note in measure.getElementsByClass('Note'):
                    if note.lyrics:
                        for lyric in note.lyrics:
                            if lyric.text:
                                lyrics.append(lyric.text)
        return lyrics
    
    @staticmethod
    def count_dynamics_in_measure(score, measure_number):
        """Count dynamics in a specific measure."""
        count = 0
        dynamics_found = []
        
        for part in score.parts:
            measures = list(part.getElementsByClass(music21.stream.Measure))
            if len(measures) >= measure_number:
                measure = measures[measure_number - 1]
                for element in measure:
                    if isinstance(element, music21.dynamics.Dynamic):
                        count += 1
                        dynamics_found.append({
                            'dynamic': element.value,
                            'offset': element.offset
                        })
        
        return count, dynamics_found


@pytest.fixture
def helpers():
    """Provide test helper methods."""
    return TestHelpers()