#!/usr/bin/env python3
"""
Diagnostic script to analyze direction elements and dashes spanners.
This addresses the broader issue of text-based spanners not being preserved.
"""

import music21
from music21 import converter
import xml.etree.ElementTree as ET

def analyze_direction_spanner_issue():
    """Analyze direction elements and dashes spanners in original vs voice parts."""
    
    print("=== Direction Elements and Dashes Spanner Analysis ===")
    
    print("\n1. Analyzing original score XML...")
    analyze_xml_directions("Crossing The Bar.musicxml", "Original")
    
    print("\n2. Analyzing soprano voice part XML...")
    analyze_xml_directions("Crossing The Bar_voices/Crossing The Bar-Soprano.musicxml", "Soprano")
    
    print("\n3. Analyzing music21 direction handling...")
    analyze_music21_directions()

def analyze_xml_directions(file_path, score_name):
    """Analyze direction elements directly from XML."""
    
    print(f"\n=== {score_name} Score XML Analysis ===")
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Find all direction elements
        directions = root.findall('.//direction')
        print(f"Found {len(directions)} direction elements")
        
        # Look for dashes elements
        dashes_elements = root.findall('.//dashes')
        print(f"Found {len(dashes_elements)} dashes elements")
        
        # Analyze each direction element
        for i, direction in enumerate(directions):
            measure_context = find_measure_context(direction)
            print(f"\nDirection {i+1} (measure {measure_context}):")
            
            # Look for words
            words = direction.findall('.//words')
            for word in words:
                print(f"  Words: '{word.text}' (attributes: {word.attrib})")
            
            # Look for dashes
            dashes = direction.findall('.//dashes')
            for dash in dashes:
                print(f"  Dashes: type='{dash.get('type')}', number='{dash.get('number')}'")
            
            # Look for wedges
            wedges = direction.findall('.//wedge')
            for wedge in wedges:
                print(f"  Wedge: type='{wedge.get('type')}', number='{wedge.get('number')}'")
        
        # Specifically look for measures 25-27
        print(f"\n=== Measures 25-27 in {score_name} ===")
        for measure_num in [25, 26, 27]:
            analyze_measure_directions(root, measure_num)
            
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")

def find_measure_context(element):
    """Find the measure number containing this element."""
    current = element
    while current is not None:
        if current.tag == 'measure':
            return current.get('number', 'unknown')
        current = current.getparent() if hasattr(current, 'getparent') else None
    return 'unknown'

def analyze_measure_directions(root, measure_num):
    """Analyze direction elements in a specific measure."""
    
    # Find the measure
    measure = root.find(f'.//measure[@number="{measure_num}"]')
    if measure is None:
        print(f"  Measure {measure_num}: Not found")
        return
    
    print(f"  Measure {measure_num}:")
    
    # Find directions in this measure
    directions = measure.findall('.//direction')
    if not directions:
        print(f"    No direction elements")
        return
    
    for direction in directions:
        # Look for words
        words = direction.findall('.//words')
        for word in words:
            print(f"    Words: '{word.text}'")
        
        # Look for dashes
        dashes = direction.findall('.//dashes')
        for dash in dashes:
            dash_type = dash.get('type')
            dash_number = dash.get('number')
            print(f"    Dashes: type='{dash_type}', number='{dash_number}'")

def analyze_music21_directions():
    """Analyze how music21 handles direction elements."""
    
    print("\n=== Music21 Direction Handling ===")
    
    # Load original score
    original_score = converter.parse("Crossing The Bar.musicxml")
    soprano_score = converter.parse("Crossing The Bar_voices/Crossing The Bar-Soprano.musicxml")
    
    print("\nOriginal score - looking for text expressions and dynamics:")
    analyze_music21_score_directions(original_score, "Original")
    
    print("\nSoprano score - looking for text expressions and dynamics:")
    analyze_music21_score_directions(soprano_score, "Soprano")

def analyze_music21_score_directions(score, score_name):
    """Analyze direction-related elements in a music21 score."""
    
    part = score.parts[0]
    
    # Look for text expressions
    text_expressions = part.getElementsByClass(music21.expressions.TextExpression)
    print(f"  Text expressions: {len(text_expressions)}")
    for expr in text_expressions:
        measure = expr.getContextByClass('Measure')
        measure_num = measure.number if measure else 'unknown'
        print(f"    Measure {measure_num}: '{expr.content}'")
    
    # Look for dynamics
    dynamics = part.getElementsByClass(music21.dynamics.Dynamic)
    print(f"  Dynamics: {len(dynamics)}")
    for dyn in dynamics:
        measure = dyn.getContextByClass('Measure')
        measure_num = measure.number if measure else 'unknown'
        print(f"    Measure {measure_num}: {dyn}")
    
    # Look for spanners
    spanners = part.getElementsByClass(music21.spanner.Spanner)
    print(f"  Spanners: {len(spanners)}")
    for spanner in spanners:
        print(f"    {type(spanner).__name__}")

if __name__ == "__main__":
    analyze_direction_spanner_issue()