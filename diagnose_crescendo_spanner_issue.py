#!/usr/bin/env python3
"""
Diagnostic script to analyze the crescendo spanner issue in measures 25-27.
"""

import music21
from music21 import converter

def analyze_crescendo_issue():
    """Analyze the crescendo spanner issue in the original score vs voice parts."""
    
    print("=== Crescendo Spanner Issue Analysis ===")
    
    # Load original score
    print("\n1. Loading original score...")
    original_score = converter.parse("Crossing The Bar.musicxml")
    
    # Load soprano voice part
    print("2. Loading soprano voice part...")
    soprano_score = converter.parse("Crossing The Bar_voices/Crossing The Bar-Soprano.musicxml")
    
    print("\n=== Original Score Analysis ===")
    analyze_crescendo_in_score(original_score, "Original")
    
    print("\n=== Soprano Voice Part Analysis ===")
    analyze_crescendo_in_score(soprano_score, "Soprano")
    
    print("\n=== Diagnosis Summary ===")
    print("Expected in measures 25-27:")
    print("  - Measure 25: 'cresc.' text + dashes start")
    print("  - Measure 26: (continuation of dashes)")
    print("  - Measure 27: dashes stop")
    print("\nActual in soprano part:")
    print("  - Measure 25: 'cresc.' text only (missing dashes start)")
    print("  - Measure 26: (no continuation)")
    print("  - Measure 27: (no dashes stop)")

def analyze_crescendo_in_score(score, score_name):
    """Analyze crescendo-related elements in a score."""
    
    print(f"\nAnalyzing {score_name} score...")
    
    # Get the first part (or only part for voice files)
    part = score.parts[0]
    
    # Look for measures 25-27
    for measure_num in [25, 26, 27]:
        measure = None
        for m in part.getElementsByClass('Measure'):
            if m.number == measure_num:
                measure = m
                break
        
        if measure:
            print(f"\n  Measure {measure_num}:")
            
            # Look for direction elements
            directions = measure.getElementsByClass('MetronomeMark') + \
                        measure.getElementsByClass('TempoIndication') + \
                        measure.getElementsByClass('TextExpression')
            
            # Look for any elements with text
            for elem in measure.recurse():
                if hasattr(elem, 'content') and elem.content:
                    if 'cresc' in str(elem.content).lower():
                        print(f"    Found text: '{elem.content}' (type: {type(elem).__name__})")
                
                # Look for dynamics
                if isinstance(elem, (music21.dynamics.Dynamic, music21.dynamics.DynamicSymbol)):
                    print(f"    Found dynamic: {elem} (type: {type(elem).__name__})")
            
            # Check for spanners that start or end in this measure
            spanners = part.getElementsByClass(music21.spanner.Spanner)
            for spanner in spanners:
                spanned_elements = spanner.getSpannedElements()
                if spanned_elements:
                    first_elem = spanned_elements[0]
                    last_elem = spanned_elements[-1]
                    
                    # Check if spanner starts or ends in this measure
                    first_measure = first_elem.getContextByClass('Measure')
                    last_measure = last_elem.getContextByClass('Measure')
                    
                    if first_measure and first_measure.number == measure_num:
                        print(f"    Spanner starts: {type(spanner).__name__}")
                    if last_measure and last_measure.number == measure_num:
                        print(f"    Spanner ends: {type(spanner).__name__}")
        else:
            print(f"\n  Measure {measure_num}: Not found")

if __name__ == "__main__":
    analyze_crescendo_issue()