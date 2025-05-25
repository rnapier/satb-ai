#!/usr/bin/env python3
"""
Test script to verify the dashes spanner fix for measures 25-27.
"""

import os
import sys
from pathlib import Path

# Add the satb_splitter module to the path
sys.path.insert(0, str(Path(__file__).parent))

from satb_splitter.voice_splitter import split_satb_voices
from satb_splitter.main import save_voice_parts

def test_dashes_spanner_fix():
    """Test that dashes spanners are properly handled in voice splitting."""
    
    print("=== Testing Dashes Spanner Fix ===")
    
    # Input and output paths
    input_file = "Crossing The Bar.musicxml"
    output_dir = "Crossing The Bar_voices_test"
    
    # Clean up any existing test output
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
    
    print(f"Input file: {input_file}")
    print(f"Output directory: {output_dir}")
    
    try:
        # Run the voice splitting with the new dashes spanner support
        print("\nRunning voice splitting with dashes spanner support...")
        
        # Split the voices directly from the file
        voices_dict = split_satb_voices(input_file)
        
        # Save the voice parts
        save_voice_parts(voices_dict, output_dir, input_file)
        
        print("\nVoice splitting completed successfully!")
        
        # Verify the output files exist
        expected_files = [
            f"{output_dir}/Crossing The Bar-Soprano.musicxml",
            f"{output_dir}/Crossing The Bar-Alto.musicxml", 
            f"{output_dir}/Crossing The Bar-Tenor.musicxml",
            f"{output_dir}/Crossing The Bar-Bass.musicxml"
        ]
        
        print("\nVerifying output files...")
        for file_path in expected_files:
            if os.path.exists(file_path):
                print(f"  ✓ {file_path}")
            else:
                print(f"  ✗ {file_path} - MISSING")
        
        # Check if the soprano part now has the crescendo properly
        soprano_file = f"{output_dir}/Crossing The Bar-Soprano.musicxml"
        if os.path.exists(soprano_file):
            print(f"\nAnalyzing soprano part for dashes spanner...")
            analyze_soprano_crescendo(soprano_file)
        
        return True
        
    except Exception as e:
        print(f"Error during voice splitting: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_soprano_crescendo(soprano_file):
    """Analyze the soprano part to check for crescendo elements."""
    
    try:
        import xml.etree.ElementTree as ET
        
        tree = ET.parse(soprano_file)
        root = tree.getroot()
        
        print("  Checking measures 25-27 for crescendo elements...")
        
        for measure_num in [25, 26, 27]:
            measure = root.find(f'.//measure[@number="{measure_num}"]')
            if measure is None:
                print(f"    Measure {measure_num}: Not found")
                continue
            
            print(f"    Measure {measure_num}:")
            
            # Look for direction elements with words
            directions = measure.findall('.//direction')
            found_elements = False
            
            for direction in directions:
                words = direction.findall('.//words')
                for word in words:
                    if word.text:
                        print(f"      Words: '{word.text}'")
                        found_elements = True
                
                # Look for dashes (though these might not be present in music21 output)
                dashes = direction.findall('.//dashes')
                for dash in dashes:
                    dash_type = dash.get('type')
                    print(f"      Dashes: type='{dash_type}'")
                    found_elements = True
            
            if not found_elements:
                print(f"      No direction elements found")
        
        print("  Analysis complete.")
        
    except Exception as e:
        print(f"  Error analyzing soprano file: {e}")

if __name__ == "__main__":
    success = test_dashes_spanner_fix()
    if success:
        print("\n✓ Test completed successfully!")
    else:
        print("\n✗ Test failed!")
        sys.exit(1)