#!/usr/bin/env python3
"""
Debug script to analyze how crescendos are stored in the original score vs separated parts.
"""

from music21 import converter
from pathlib import Path

def analyze_all_direction_elements(file_path):
    """Analyze what types of direction elements exist throughout the score."""
    score = converter.parse(str(file_path))
    
    print(f"=== Analyzing {file_path} ===")
    
    # Search for any direction-related elements throughout the entire score
    direction_elements = []
    crescendo_elements = []
    wedge_elements = []
    dynamic_elements = []
    
    for element in score.recurse():
        element_str = str(element).lower()
        element_type = str(type(element).__name__)
        
        # Look for various types of direction/dynamic elements
        if 'direction' in element_type.lower():
            direction_elements.append((element, element_type))
        
        if 'crescendo' in element_str or 'crescendo' in element_type.lower():
            crescendo_elements.append((element, element_type))
            
        if 'wedge' in element_str:
            wedge_elements.append((element, element_type))
            
        if 'dynamic' in element_type.lower():
            dynamic_elements.append((element, element_type))
    
    print(f"Direction elements found: {len(direction_elements)}")
    for element, element_type in direction_elements:
        print(f"  - {element} (type: {element_type})")
        
    print(f"Crescendo elements found: {len(crescendo_elements)}")
    for element, element_type in crescendo_elements:
        print(f"  - {element} (type: {element_type})")
        
    print(f"Wedge elements found: {len(wedge_elements)}")  
    for element, element_type in wedge_elements:
        print(f"  - {element} (type: {element_type})")
        
    print(f"Dynamic elements found: {len(dynamic_elements)}")
    for element, element_type in dynamic_elements:
        print(f"  - {element} (type: {element_type})")

def analyze_measure_4_detailed(file_path):
    """Detailed analysis of measure 4 structure."""
    score = converter.parse(str(file_path))
    
    print(f"\n=== Detailed Measure 4 Analysis for {file_path} ===")
    
    # Find measure 4 and examine its structure
    for part_idx, part in enumerate(score.parts):
        print(f"Part {part_idx}: {part}")
        for measure in part.getElementsByClass('Measure'):
            if measure.number == 4:
                print(f"  Measure 4 found in part {part_idx}")
                print(f"  Measure 4 direct elements:")
                for i, element in enumerate(measure):
                    print(f"    {i}: {element} (type: {type(element).__name__})")
                
                print(f"  Measure 4 all recursive elements:")
                for i, element in enumerate(measure.recurse()):
                    print(f"    {i}: {element} (type: {type(element).__name__})")
                    # Check for any direction-related attributes
                    if hasattr(element, '__dict__'):
                        attrs = [attr for attr in dir(element) if 'direction' in attr.lower() or 'dynamic' in attr.lower()]
                        if attrs:
                            print(f"      Direction/Dynamic related attributes: {attrs}")

def check_raw_musicxml_parsing(file_path):
    """Check if we can find crescendo info in the raw MusicXML."""
    print(f"\n=== Raw MusicXML Check for {file_path} ===")
    
    # Read the raw file and look for crescendo/wedge content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for crescendo-related content in the raw XML
        if 'crescendo' in content.lower():
            print("Found 'crescendo' in raw MusicXML")
            # Find lines containing crescendo
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'crescendo' in line.lower():
                    print(f"  Line {i+1}: {line.strip()}")
        
        if 'wedge' in content.lower():
            print("Found 'wedge' in raw MusicXML")
            # Find lines containing wedge
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'wedge' in line.lower():
                    print(f"  Line {i+1}: {line.strip()}")
        
        # Look specifically in measure 4
        if 'measure number="4"' in content:
            print("Found measure 4 in raw MusicXML")
            # Extract measure 4 content
            measure_start = content.find('measure number="4"')
            measure_end = content.find('</measure>', measure_start)
            if measure_start != -1 and measure_end != -1:
                measure_content = content[measure_start:measure_end + 10]
                if 'crescendo' in measure_content.lower() or 'wedge' in measure_content.lower():
                    print("Found crescendo/wedge in measure 4:")
                    print(measure_content[:500] + "..." if len(measure_content) > 500 else measure_content)
                else:
                    print("No crescendo/wedge found in measure 4 content")
            
    except Exception as e:
        print(f"Error reading raw MusicXML: {e}")

def main():
    """Main analysis function."""
    
    # Analyze original file
    original_file = Path("Crossing The Bar.musicxml")
    if original_file.exists():
        analyze_all_direction_elements(original_file)
        analyze_measure_4_detailed(original_file)
        check_raw_musicxml_parsing(original_file)
    else:
        print(f"Original file {original_file} not found")
    
    print("\n" + "="*80 + "\n")
    
    # Analyze soprano part
    soprano_file = Path("Crossing The Bar_voices/Crossing The Bar-Soprano.musicxml")
    if soprano_file.exists():
        analyze_all_direction_elements(soprano_file)
        analyze_measure_4_detailed(soprano_file)
        check_raw_musicxml_parsing(soprano_file)
    else:
        print(f"Soprano file {soprano_file} not found")

if __name__ == "__main__":
    main()