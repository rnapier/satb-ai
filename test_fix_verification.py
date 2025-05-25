#!/usr/bin/env python3
"""
Test script to verify the dynamics duplication fix.
"""

import sys
import os
from pathlib import Path
import music21

# Add the current directory to Python path
sys.path.insert(0, '.')

from satb_splitter import split_satb_voices
from satb_splitter.utils import ProcessingOptions

def verify_fix():
    """Verify that the dynamics duplication fix works."""
    print("🔧 VERIFYING DYNAMICS DUPLICATION FIX")
    print("=" * 50)
    
    try:
        # Process the score with the fix
        options = ProcessingOptions(
            apply_dynamics_unification=True,
            apply_lyrics_unification=True,
            apply_spanner_unification=True
        )
        
        print("Processing score with fixed unification...")
        voice_scores = split_satb_voices("Crossing The Bar.musicxml", options=options)
        
        print("✓ Processing completed successfully")
        
        # Check measure 29 in soprano
        soprano_score = voice_scores['Soprano']
        
        print("\nAnalyzing measure 29 in fixed soprano score...")
        dynamics_count = 0
        dynamics_found = []
        
        for part in soprano_score.parts:
            for measure in part.getElementsByClass(music21.stream.Measure):
                if measure.number == 29:
                    for element in measure:
                        if isinstance(element, music21.dynamics.Dynamic):
                            dynamics_count += 1
                            dynamics_found.append({
                                'dynamic': element.value,
                                'offset': element.offset
                            })
                            print(f"  Found: {element.value} at offset {element.offset}")
        
        print(f"\nTotal dynamics in measure 29: {dynamics_count}")
        
        if dynamics_count == 1:
            print("✅ SUCCESS: Only one dynamic found - duplication fixed!")
            
            # Save the fixed soprano file for comparison
            output_path = "Crossing The Bar_voices_fixed"
            os.makedirs(output_path, exist_ok=True)
            
            soprano_file = os.path.join(output_path, "Crossing The Bar-Soprano.musicxml")
            soprano_score.write('musicxml', fp=soprano_file)
            print(f"✓ Fixed soprano file saved to: {soprano_file}")
            
            return True
        else:
            print(f"❌ FAILURE: Found {dynamics_count} dynamics - duplication still exists!")
            for i, dyn in enumerate(dynamics_found):
                print(f"  {i+1}. {dyn['dynamic']} at offset {dyn['offset']}")
            return False
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the fix verification."""
    success = verify_fix()
    
    if success:
        print("\n🎉 FIX VERIFICATION SUCCESSFUL!")
        print("The duplicate dynamics issue has been resolved.")
        return 0
    else:
        print("\n💥 FIX VERIFICATION FAILED!")
        print("The issue may still exist or a new problem occurred.")
        return 1

if __name__ == "__main__":
    sys.exit(main())