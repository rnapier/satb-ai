#!/usr/bin/env python3
"""
Test script to reproduce and verify the fix for the missing crescendo in measure 4 of the Soprano part.
"""

from pathlib import Path
from satb_splitter.main import split_satb_voices
from music21 import converter
import tempfile

def test_measure_4_crescendo_reproduction():
    """Test case to reproduce the original problem and verify the solution."""
    
    original_file = Path("Crossing The Bar.musicxml")
    
    if not original_file.exists():
        print("❌ Sample score file not found")
        return
    
    print("=== REPRODUCING MEASURE 4 CRESCENDO ISSUE ===")
    print("Original problem: 'At measure 4, the Soprano part is missing the crescendo'")
    print()
    
    # Process the score
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        voices = split_satb_voices(str(original_file), str(temp_path))
        
        if 'Soprano' not in voices:
            print("❌ FAILURE: Soprano voice not found in results")
            return
        
        soprano_score = voices['Soprano']
        
        # Find measure 4
        soprano_part = soprano_score.parts[0]
        measures = soprano_part.getElementsByClass('Measure')
        
        if len(measures) < 4:
            print(f"❌ FAILURE: Only {len(measures)} measures found, need at least 4")
            return
        
        measure_4 = measures[3]  # 0-based indexing
        
        print(f"📏 MEASURE 4 ANALYSIS:")
        print(f"Measure 4 elements: {[str(elem) for elem in measure_4.elements]}")
        
        # Check for crescendos in measure 4
        crescendos_in_measure = []
        for element in measure_4.elements:
            if 'Crescendo' in str(type(element)):
                crescendos_in_measure.append(element)
        
        print(f"Crescendos directly in measure 4: {len(crescendos_in_measure)}")
        
        # Check for part-level crescendos
        part_crescendos = []
        for element in soprano_part.elements:
            if 'Crescendo' in str(type(element)):
                part_crescendos.append(element)
        
        print(f"Total crescendos in Soprano part: {len(part_crescendos)}")
        
        # Check if any crescendos span measure 4
        spanning_crescendos = []
        for crescendo in part_crescendos:
            try:
                if hasattr(crescendo, 'getSpannedElements'):
                    spanned = crescendo.getSpannedElements()
                    spanned_measures = set()
                    for note in spanned:
                        if hasattr(note, 'activeSite') and note.activeSite:
                            if hasattr(note.activeSite, 'number'):
                                spanned_measures.add(note.activeSite.number)
                    
                    if 4 in spanned_measures:
                        spanning_crescendos.append(crescendo)
                        print(f"✅ Found crescendo spanning measure 4: {crescendo}")
            except Exception as e:
                print(f"Error checking crescendo span: {e}")
        
        print(f"Crescendos spanning measure 4: {len(spanning_crescendos)}")
        
        # Test export preservation
        soprano_file = temp_path / f"{original_file.stem}-Soprano.musicxml"
        if soprano_file.exists():
            print(f"\n📁 EXPORT TEST:")
            try:
                exported_score = converter.parse(str(soprano_file))
                exported_part = exported_score.parts[0]
                
                exported_crescendos = []
                for element in exported_part.elements:
                    if 'Crescendo' in str(type(element)):
                        exported_crescendos.append(element)
                
                print(f"Crescendos in exported file: {len(exported_crescendos)}")
                
                if len(exported_crescendos) > 0:
                    print("✅ SUCCESS: Crescendos preserved in export")
                else:
                    print("❌ FAILURE: No crescendos in exported file")
                    
            except Exception as e:
                print(f"❌ Export test failed: {e}")
        
        # Final verdict
        print(f"\n🎯 FINAL RESULTS:")
        has_crescendo_in_memory = len(part_crescendos) > 0 or len(spanning_crescendos) > 0
        
        if has_crescendo_in_memory:
            print("✅ SUCCESS: Soprano part has crescendo markings in memory")
        else:
            print("❌ FAILURE: No crescendos found in Soprano part")
        
        # Test the specific case from the original issue
        if len(spanning_crescendos) > 0:
            print("✅ SUCCESS: Found crescendos that span measure 4")
            print("🎉 ISSUE RESOLVED: Original problem is fixed!")
        else:
            print("❌ ISSUE PERSISTS: No crescendos spanning measure 4 found")

if __name__ == "__main__":
    test_measure_4_crescendo_reproduction()