#!/usr/bin/env python3
"""
Debug script to analyze voice coverage calculation issues.
"""

import tempfile
from pathlib import Path
from music21 import converter
from satb_splitter.main import split_satb_voices
from satb_splitter.spanner_processor import SpannerProcessor
from satb_splitter.spanner_analyzer import SpannerAnalyzer
from satb_splitter.utils import load_score

def debug_voice_coverage():
    """Debug the voice coverage calculation."""
    score_path = Path("Crossing The Bar.musicxml")
    if not score_path.exists():
        print("❌ Sample score file not found")
        return
    
    print("🔍 Debugging Voice Coverage Calculation")
    print("=" * 60)
    
    # Load original score and extract spanners
    original_score = load_score(str(score_path))
    spanner_processor = SpannerProcessor()
    original_spanners = spanner_processor.extract_all_spanners_from_score(original_score)
    
    # Process voices to get separated notes
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        voices = split_satb_voices(str(score_path), str(temp_path))
        
        # Extract ALL notes from each voice (not just measure 29)
        all_voice_notes = {}
        for voice_name, voice_score in voices.items():
            notes = []
            for part in voice_score.parts:
                for measure in part.getElementsByClass('Measure'):
                    for note in measure.flatten().notes:
                        notes.append(note)
            all_voice_notes[voice_name] = notes
            print(f"📝 {voice_name}: {len(notes)} total notes")
        
        # Test a specific spanner's coverage calculation
        if original_spanners:
            print(f"\n🔍 Testing spanner coverage calculation:")
            test_spanner = original_spanners[5]  # Try a slur (index 5 from earlier debug)
            print(f"   Testing spanner: {type(test_spanner).__name__}: {test_spanner}")
            
            # Get spanner notes
            analyzer = SpannerAnalyzer()
            spanner_notes = analyzer._extract_note_references(test_spanner)
            print(f"   Spanner references {len(spanner_notes)} notes:")
            
            for i, note in enumerate(spanner_notes):
                if hasattr(note, 'pitch'):
                    print(f"     {i+1}. {note.pitch.name}{note.pitch.octave}")
            
            # Calculate coverage manually
            print(f"\n📊 Voice coverage calculation:")
            coverage = analyzer._analyze_voice_coverage(spanner_notes, all_voice_notes)
            
            for voice_name, cov in coverage.items():
                print(f"   {voice_name}: {cov:.2%} coverage")
                
                # Show which notes matched
                if cov > 0:
                    matching_count = 0
                    for spanner_note in spanner_notes:
                        if hasattr(spanner_note, 'pitch'):
                            spanner_pitch = spanner_note.pitch
                            for voice_note in all_voice_notes[voice_name]:
                                if (hasattr(voice_note, 'pitch') and
                                    voice_note.pitch.name == spanner_pitch.name and
                                    voice_note.pitch.octave == spanner_pitch.octave):
                                    matching_count += 1
                                    print(f"     ✅ Matched: {spanner_pitch.name}{spanner_pitch.octave}")
                                    break
            
            # Test with different relevance thresholds
            print(f"\n🎯 Testing different relevance thresholds:")
            thresholds = [0.0, 0.1, 0.2, 0.5]
            for threshold in thresholds:
                relevant_voices = []
                for voice_name, cov in coverage.items():
                    if cov >= threshold:
                        relevant_voices.append(voice_name)
                print(f"   Threshold {threshold:.1%}: {relevant_voices}")

if __name__ == "__main__":
    debug_voice_coverage()