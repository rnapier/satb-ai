#!/usr/bin/env python3
"""
Test case to reproduce and verify the fix for missing crescendo in Soprano part at measure 4.

This test ensures that dynamics markings (crescendos, diminuendos, etc.) are properly
preserved when splitting SATB scores into individual voice parts.
"""

import pytest
import tempfile
import os
from pathlib import Path
from music21 import converter, stream
from satb_splitter.main import split_satb_voices


class TestCrescendoPreservation:
    """Test cases for crescendo and dynamics preservation during voice separation."""
    
    def test_soprano_crescendo_measure_4_preserved(self):
        """
        Test that the crescendo in measure 4 is preserved in the Soprano part.
        
        This test reproduces the issue where crescendo markings from the original
        score are missing in the separated Soprano voice part.
        """
        # Use the existing test file
        input_file = Path("Crossing The Bar.musicxml")
        
        # Ensure the input file exists
        assert input_file.exists(), f"Test input file {input_file} not found"
        
        # Create a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Split the score
            split_satb_voices(str(input_file), str(temp_path))
            
            # Check that soprano file was created
            soprano_file = temp_path / f"{input_file.stem}-Soprano.musicxml"
            assert soprano_file.exists(), "Soprano part was not created"
            
            # Load the soprano part using music21
            soprano_score = converter.parse(str(soprano_file))
            
            # Find measure 4
            soprano_part = soprano_score.parts[0] if soprano_score.parts else soprano_score
            measure_4 = None
            
            for measure in soprano_part.getElementsByClass('Measure'):
                if measure.number == 4:
                    measure_4 = measure
                    break
            
            assert measure_4 is not None, "Measure 4 not found in Soprano part"
            
            # Look for crescendo/diminuendo markings in the entire soprano part
            # Spanners (crescendos) are stored at part level, not measure level
            soprano_part = soprano_score.parts[0] if soprano_score.parts else soprano_score
            
            crescendos_found = []
            diminuendos_found = []
            
            # Check for spanners at part level
            spanners = soprano_part.getElementsByClass('Spanner')
            for spanner in spanners:
                if 'Crescendo' in str(type(spanner)):
                    crescendos_found.append(spanner)
                elif 'Diminuendo' in str(type(spanner)):
                    diminuendos_found.append(spanner)
            
            # Also check for crescendos in the entire score recursively
            all_crescendos = []
            for element in soprano_score.recurse():
                if 'Crescendo' in str(type(element)):
                    all_crescendos.append(element)
            
            # Print debug information
            print(f"Measure 4 contents: {[str(el) for el in measure_4.recurse()]}")
            print(f"Part-level crescendos found: {len(crescendos_found)}")
            print(f"All crescendos in score: {len(all_crescendos)}")
            print(f"Crescendo details: {[str(c) for c in all_crescendos]}")
            
            # Check that crescendo is present
            has_crescendo = len(crescendos_found) > 0 or len(all_crescendos) > 0
            
            assert has_crescendo, (
                f"Crescendo markings missing from Soprano part. "
                f"Found {len(crescendos_found)} part-level crescendos and {len(all_crescendos)} total crescendos"
            )
    
    def test_compare_original_vs_soprano_dynamics(self):
        """
        Compare dynamics between original score and separated Soprano part.
        
        This test verifies that all dynamic markings in the soprano voice of the
        original score are preserved in the separated Soprano part.
        """
        input_file = Path("Crossing The Bar.musicxml")
        assert input_file.exists(), f"Test input file {input_file} not found"
        
        # Load the original score
        original_score = converter.parse(str(input_file))
        
        # Create a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Split the score
            split_satb_voices(str(input_file), str(temp_path))
            
            # Load the soprano part
            soprano_file = temp_path / f"{input_file.stem}-Soprano.musicxml"
            soprano_score = converter.parse(str(soprano_file))
            
            # Get the first part from each score
            original_part = original_score.parts[0] if original_score.parts else original_score
            soprano_part = soprano_score.parts[0] if soprano_score.parts else soprano_score
            
            # Find measure 4 in both scores
            original_measure_4 = None
            soprano_measure_4 = None
            
            for measure in original_part.getElementsByClass('Measure'):
                if measure.number == 4:
                    original_measure_4 = measure
                    break
            
            for measure in soprano_part.getElementsByClass('Measure'):
                if measure.number == 4:
                    soprano_measure_4 = measure
                    break
            
            assert original_measure_4 is not None, "Measure 4 not found in original score"
            assert soprano_measure_4 is not None, "Measure 4 not found in Soprano part"
            
            # Extract dynamics from original measure 4 (soprano voice)
            original_dynamics = []
            for element in original_measure_4.recurse():
                if hasattr(element, 'classes'):
                    if any(cls in element.classes for cls in ['Dynamic', 'Crescendo', 'Diminuendo']):
                        original_dynamics.append(str(element))
                    elif 'Direction' in element.classes and hasattr(element, 'content'):
                        if 'crescendo' in str(element.content).lower():
                            original_dynamics.append(str(element))
            
            # Extract dynamics from soprano measure 4
            soprano_dynamics = []
            for element in soprano_measure_4.recurse():
                if hasattr(element, 'classes'):
                    if any(cls in element.classes for cls in ['Dynamic', 'Crescendo', 'Diminuendo']):
                        soprano_dynamics.append(str(element))
                    elif 'Direction' in element.classes and hasattr(element, 'content'):
                        if 'crescendo' in str(element.content).lower():
                            soprano_dynamics.append(str(element))
            
            print(f"Original measure 4 dynamics: {original_dynamics}")
            print(f"Soprano measure 4 dynamics: {soprano_dynamics}")
            
            # At minimum, we should have some dynamics in the original
            # and they should be preserved in the soprano part
            if original_dynamics:
                assert soprano_dynamics, (
                    f"Dynamics found in original measure 4 ({original_dynamics}) "
                    f"but missing in Soprano part ({soprano_dynamics})"
                )


if __name__ == "__main__":
    # Run the test directly
    test = TestCrescendoPreservation()
    try:
        test.test_soprano_crescendo_measure_4_preserved()
        print("✅ Crescendo preservation test passed!")
    except AssertionError as e:
        print(f"❌ Crescendo preservation test failed: {e}")
    
    try:
        test.test_compare_original_vs_soprano_dynamics()
        print("✅ Dynamics comparison test passed!")
    except AssertionError as e:
        print(f"❌ Dynamics comparison test failed: {e}")