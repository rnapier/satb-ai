#!/usr/bin/env python3
"""
Debug script to analyze spanner duplication issues.
"""

import tempfile
from pathlib import Path
from satb_splitter.main import split_satb_voices
from satb_splitter.spanner_processor import SpannerProcessor
from satb_splitter.utils import load_score

def debug_spanner_duplication():
    """Debug spanner duplication in voice processing."""
    score_path = Path("Crossing The Bar.musicxml")
    if not score_path.exists():
        print("❌ Sample score file not found")
        return
    
    print("🔍 Debugging Spanner Duplication")
    print("=" * 50)
    
    # Load original score and extract spanners with context
    original_score = load_score(str(score_path))
    spanner_processor = SpannerProcessor()
    spanners_with_context = spanner_processor.extract_all_spanners_from_score(original_score)
    
    print(f"📊 Original analysis:")
    print(f"   Total spanners with context: {len(spanners_with_context)}")
    
    # Analyze each spanner's context
    for i, context in enumerate(spanners_with_context):
        spanner = context['spanner']
        part_idx = context['part_index']
        voice_ids = context['voice_ids']
        print(f"   {i+1}. {type(spanner).__name__} in part {part_idx}, voices: {voice_ids}")
    
    # Test voice assignment logic
    print(f"\n🎯 Testing voice assignment:")
    voice_assignments = {'Soprano': [], 'Alto': [], 'Tenor': [], 'Bass': []}
    
    for i, context in enumerate(spanners_with_context):
        spanner = context['spanner']
        assigned_voices = []
        
        for voice_name in ['Soprano', 'Alto', 'Tenor', 'Bass']:
            voice_id_mapping = spanner_processor._get_voice_id_mapping_for_voice(voice_name)
            if spanner_processor._spanner_belongs_to_voice(context, voice_name, voice_id_mapping):
                assigned_voices.append(voice_name)
                voice_assignments[voice_name].append(i)
        
        print(f"   Spanner {i+1} assigned to: {assigned_voices}")
    
    print(f"\n📋 Voice assignment summary:")
    total_assignments = 0
    for voice_name, assignments in voice_assignments.items():
        print(f"   {voice_name}: {len(assignments)} spanners (indices: {assignments})")
        total_assignments += len(assignments)
    
    print(f"\n⚠️  Total assignments: {total_assignments} (should be ≤ {len(spanners_with_context)})")
    
    if total_assignments > len(spanners_with_context):
        print("🚨 DUPLICATION DETECTED! Same spanners assigned to multiple voices.")
        
        # Find duplicates
        all_assignments = []
        for voice_name, assignments in voice_assignments.items():
            for spanner_idx in assignments:
                all_assignments.append((voice_name, spanner_idx))
        
        # Group by spanner index
        from collections import defaultdict
        spanner_to_voices = defaultdict(list)
        for voice_name, spanner_idx in all_assignments:
            spanner_to_voices[spanner_idx].append(voice_name)
        
        for spanner_idx, voices in spanner_to_voices.items():
            if len(voices) > 1:
                spanner = spanners_with_context[spanner_idx]['spanner']
                print(f"   🔴 Spanner {spanner_idx+1} ({type(spanner).__name__}) assigned to: {voices}")

if __name__ == "__main__":
    debug_spanner_duplication()