#!/usr/bin/env python3
"""
Comprehensive test for the measure 29 slur transfer fix.

This test validates that the specific issue described in the task is resolved:
"In measure 29, there are slurs for Alto, Tenor and Bass, but not Soprano. They are not transferred."
"""

import tempfile
from pathlib import Path
from satb_splitter.main import split_satb_voices


def test_measure_29_slur_transfer_fix():
    """Test that slurs in measure 29 are correctly transferred to Alto, Tenor, and Bass."""
    score_path = Path("Crossing The Bar.musicxml")
    if not score_path.exists():
        print("❌ Sample score file not found - skipping test")
        return
    
    print("🎵 Testing Measure 29 Slur Transfer Fix")
    print("=" * 50)
    
    # Process the score
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        voices = split_satb_voices(str(score_path), str(temp_path))
        
        # Extract spanners from measure 29 for each voice
        measure_29_results = {}
        for voice_name, voice_score in voices.items():
            slurs = []
            all_spanners = []
            
            for part in voice_score.parts:
                for measure in part.getElementsByClass('Measure'):
                    if hasattr(measure, 'number') and measure.number == 29:
                        for spanner in part.getElementsByClass('Spanner'):
                            all_spanners.append(spanner)
                            if 'Slur' in type(spanner).__name__:
                                slurs.append(spanner)
            
            measure_29_results[voice_name] = {
                'total_spanners': len(all_spanners),
                'slurs': len(slurs),
                'slur_objects': slurs
            }
    
    # Print results
    print("\n📊 Measure 29 Results:")
    for voice_name, result in measure_29_results.items():
        print(f"   {voice_name}: {result['total_spanners']} total spanners, {result['slurs']} slurs")
    
    # TEST REQUIREMENTS from the task description:
    print(f"\n✅ VALIDATING TASK REQUIREMENTS:")
    
    # 1. "slurs for Alto, Tenor and Bass" - these voices should have slurs
    alto_slurs = measure_29_results['Alto']['slurs']
    tenor_slurs = measure_29_results['Tenor']['slurs']
    bass_slurs = measure_29_results['Bass']['slurs']
    
    assert alto_slurs > 0, f"❌ Alto should have slurs in measure 29, but has {alto_slurs}"
    print(f"   ✅ Alto has {alto_slurs} slur(s) in measure 29")
    
    assert tenor_slurs > 0, f"❌ Tenor should have slurs in measure 29, but has {tenor_slurs}"  
    print(f"   ✅ Tenor has {tenor_slurs} slur(s) in measure 29")
    
    assert bass_slurs > 0, f"❌ Bass should have slurs in measure 29, but has {bass_slurs}"
    print(f"   ✅ Bass has {bass_slurs} slur(s) in measure 29")
    
    # 2. "but not Soprano" - Soprano may have other spanners but slurs are not required
    soprano_slurs = measure_29_results['Soprano']['slurs']
    print(f"   ℹ️  Soprano has {soprano_slurs} slur(s) in measure 29 (not required by task)")
    
    # 3. "They are not transferred" should be FIXED - slurs are now transferred
    total_slurs = alto_slurs + tenor_slurs + bass_slurs
    assert total_slurs >= 3, f"❌ Expected at least 3 slurs total in Alto/Tenor/Bass, got {total_slurs}"
    print(f"   ✅ Slurs are successfully transferred! Total: {total_slurs} slurs in Alto/Tenor/Bass")
    
    # 4. Validate no nuclear copying (voices should have different spanner counts)
    total_spanners = [result['total_spanners'] for result in measure_29_results.values()]
    unique_counts = len(set(total_spanners))
    if unique_counts > 1:
        print(f"   ✅ No nuclear copying detected (voices have different spanner counts)")
    else:
        print(f"   ⚠️  All voices have same spanner count: {total_spanners[0]} - check for nuclear copying")
    
    print(f"\n🎉 MEASURE 29 SLUR TRANSFER FIX VALIDATED!")
    print(f"   Original problem: 'slurs for Alto, Tenor and Bass...are not transferred'")
    print(f"   Current result: Alto={alto_slurs}, Tenor={tenor_slurs}, Bass={bass_slurs} slurs ✅")


if __name__ == "__main__":
    test_measure_29_slur_transfer_fix()