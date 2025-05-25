"""
Test cases for verifying correct title formatting in voice scores.
"""

import tempfile
import shutil
from pathlib import Path
import music21
import pytest

from satb_splitter.utils import save_voice_scores


class TestTitleFormatting:
    """Test title formatting for voice scores."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_voice_movement_format_should_be_original_title_with_voice_in_parentheses(self):
        """Test that voice movement names follow format: '<original title> (<voice>)'."""
        # Create a simple test score with a title
        original_score = music21.stream.Score()
        original_score.metadata = music21.metadata.Metadata()
        original_score.metadata.title = "Crossing The Bar"
        
        # Add a simple part with a note
        part = music21.stream.Part()
        measure = music21.stream.Measure()
        measure.append(music21.note.Note('C4', quarterLength=1))
        part.append(measure)
        original_score.append(part)
        
        # Create voice scores (simulating what the processor would create)
        voice_scores = {}
        for voice_name in ['Soprano', 'Alto', 'Tenor', 'Bass']:
            # Create a copy for each voice
            voice_score = music21.stream.Score()
            voice_score.metadata = music21.metadata.Metadata()
            voice_score.metadata.title = original_score.metadata.title
            
            # Copy the part
            voice_part = music21.stream.Part()
            voice_measure = music21.stream.Measure()
            voice_measure.append(music21.note.Note('C4', quarterLength=1))
            voice_part.append(voice_measure)
            voice_score.append(voice_part)
            
            voice_scores[voice_name] = voice_score
        
        # Save the voice scores
        base_name = "Crossing The Bar"
        created_files = save_voice_scores(voice_scores, self.temp_dir, base_name)
        
        # Verify that files were created
        assert len(created_files) == 4
        
        # Load each saved file and check the title
        for voice_name in ['Soprano', 'Alto', 'Tenor', 'Bass']:
            file_path = Path(self.temp_dir) / f"{base_name}-{voice_name}.musicxml"
            assert file_path.exists(), f"File should exist: {file_path}"
            
            # Load the saved score
            saved_score = music21.converter.parse(str(file_path))
            
            # Check the movement name format (this is what actually gets displayed as title)
            expected_movement = f"{base_name} ({voice_name})"
            actual_movement = saved_score.metadata.movementName
            
            assert actual_movement == expected_movement, (
                f"Movement name format incorrect for {voice_name}. "
                f"Expected: '{expected_movement}', Got: '{actual_movement}'"
            )
            
            # Verify part name is just the voice name
            if saved_score.parts:
                expected_part_name = voice_name
                actual_part_name = saved_score.parts[0].partName
                
                assert actual_part_name == expected_part_name, (
                    f"Part name incorrect for {voice_name}. "
                    f"Expected: '{expected_part_name}', Got: '{actual_part_name}'"
                )
    
    def test_movement_name_should_include_original_title(self):
        """Test that movement name includes original title with voice in parentheses."""
        # Create a simple test score
        original_score = music21.stream.Score()
        original_score.metadata = music21.metadata.Metadata()
        original_score.metadata.title = "Test Song"
        
        # Add a simple part
        part = music21.stream.Part()
        measure = music21.stream.Measure()
        measure.append(music21.note.Note('C4', quarterLength=1))
        part.append(measure)
        original_score.append(part)
        
        # Create voice score
        voice_scores = {'Soprano': original_score}
        
        # Save the voice score
        base_name = "Test Song"
        save_voice_scores(voice_scores, self.temp_dir, base_name)
        
        # Load and check movement name
        file_path = Path(self.temp_dir) / f"{base_name}-Soprano.musicxml"
        saved_score = music21.converter.parse(str(file_path))
        
        # Movement name should be "Test Song (Soprano)", not "Soprano Part"
        expected_movement = "Test Song (Soprano)"
        actual_movement = saved_score.metadata.movementName
        
        assert actual_movement == expected_movement, (
            f"Movement name incorrect. Expected: '{expected_movement}', Got: '{actual_movement}'"
        )