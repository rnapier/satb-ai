"""
Unification rules for dynamics, lyrics, and spanners in satb-split.
"""

import copy
import music21
from typing import Dict, List, Any


def apply_unification(voices_dict):
    """Apply unification rules for dynamics and lyrics across SATB parts."""
    print("Analyzing dynamics and lyrics for unification...")
    
    # Extract dynamics from each voice
    soprano_dynamics = extract_dynamics_from_part(voices_dict['Soprano'])
    alto_dynamics = extract_dynamics_from_part(voices_dict['Alto'])
    tenor_dynamics = extract_dynamics_from_part(voices_dict['Tenor'])
    bass_dynamics = extract_dynamics_from_part(voices_dict['Bass'])
    
    print(f"  Dynamics found: Soprano={len(soprano_dynamics)}, Alto={len(alto_dynamics)}, Tenor={len(tenor_dynamics)}, Bass={len(bass_dynamics)}")
    
    # Apply dynamics unification rules
    unify_dynamics(voices_dict, soprano_dynamics, alto_dynamics, tenor_dynamics, bass_dynamics)
    
    # Extract lyrics from each voice
    soprano_lyrics = extract_lyrics_from_part(voices_dict['Soprano'])
    alto_lyrics = extract_lyrics_from_part(voices_dict['Alto'])
    tenor_lyrics = extract_lyrics_from_part(voices_dict['Tenor'])
    bass_lyrics = extract_lyrics_from_part(voices_dict['Bass'])
    
    print(f"  Lyrics found: Soprano={len(soprano_lyrics)}, Alto={len(alto_lyrics)}, Tenor={len(tenor_lyrics)}, Bass={len(bass_lyrics)}")
    
    # Apply lyrics unification rules
    unify_lyrics(voices_dict, soprano_lyrics, alto_lyrics, tenor_lyrics, bass_lyrics)


def unify_spanners(voices_dict: Dict[str, music21.stream.Score],
                  extracted_spanners: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Apply unification rules for spanners across SATB parts.
    
    Args:
        voices_dict: Dictionary mapping voice names to Score objects
        extracted_spanners: Extracted spanners from original score
        
    Returns:
        Dictionary mapping voice names to their assigned spanners
    """
    print("=== Applying Spanner Unification Rules ===")
    
    spanner_assignments = {
        'Soprano': [],
        'Alto': [],
        'Tenor': [],
        'Bass': []
    }
    
    # Process each spanner type
    unify_wedges(extracted_spanners['wedges'], spanner_assignments)
    distribute_slurs(extracted_spanners['slurs'], spanner_assignments)
    distribute_ties(extracted_spanners['ties'], spanner_assignments)
    distribute_other_spanners(extracted_spanners['other_spanners'], spanner_assignments)
    
    # Print summary
    for voice_name, spanners in spanner_assignments.items():
        print(f"  {voice_name}: {len(spanners)} spanners assigned")
    
    return spanner_assignments


def unify_wedges(wedges: List[Dict[str, Any]], assignments: Dict[str, List[Dict[str, Any]]]) -> None:
    """Apply wedge (crescendo/diminuendo) unification rules."""
    print("  Applying wedge unification rules...")
    
    # Group wedges by timing to find potential system-wide wedges
    wedge_groups = group_wedges_by_timing(wedges)
    
    for group in wedge_groups:
        if len(group) == 1:
            # Single wedge - apply voice-specific or system-wide rules
            wedge = group[0]
            apply_single_wedge_rules(wedge, assignments)
        else:
            # Multiple wedges at similar timing - likely system-wide
            apply_multiple_wedge_rules(group, assignments)


def distribute_slurs(slurs: List[Dict[str, Any]], assignments: Dict[str, List[Dict[str, Any]]]) -> None:
    """Distribute slurs to appropriate voices (typically voice-specific)."""
    print("  Distributing slurs...")
    
    for slur in slurs:
        # Slurs are typically voice-specific
        target_voices = get_voice_assignment_for_spanner(slur)
        
        for voice_name in target_voices:
            if voice_name in assignments:
                assignments[voice_name].append(slur)
                print(f"    Assigned slur to {voice_name}")


def distribute_ties(ties: List[Dict[str, Any]], assignments: Dict[str, List[Dict[str, Any]]]) -> None:
    """Distribute ties to appropriate voices (always voice-specific)."""
    print("  Distributing ties...")
    
    for tie in ties:
        # Ties are always voice-specific
        target_voices = get_voice_assignment_for_spanner(tie)
        
        for voice_name in target_voices:
            if voice_name in assignments:
                assignments[voice_name].append(tie)


def distribute_other_spanners(other_spanners: List[Dict[str, Any]], assignments: Dict[str, List[Dict[str, Any]]]) -> None:
    """Distribute other types of spanners."""
    print("  Distributing other spanners...")
    
    for spanner in other_spanners:
        # Default to voice-specific distribution
        target_voices = get_voice_assignment_for_spanner(spanner)
        
        for voice_name in target_voices:
            if voice_name in assignments:
                assignments[voice_name].append(spanner)
                print(f"    Assigned {spanner['type']} to {voice_name}")


def group_wedges_by_timing(wedges: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """Group wedges that occur at similar times (potentially system-wide)."""
    groups = []
    tolerance = 1.0  # 1 beat tolerance
    
    for wedge in wedges:
        start_time = wedge.get('start_offset', 0)
        
        # Find existing group with similar timing
        found_group = False
        for group in groups:
            group_start = group[0].get('start_offset', 0)
            if abs(start_time - group_start) <= tolerance:
                group.append(wedge)
                found_group = True
                break
        
        if not found_group:
            groups.append([wedge])
    
    return groups


def apply_single_wedge_rules(wedge: Dict[str, Any], assignments: Dict[str, List[Dict[str, Any]]]) -> None:
    """Apply rules for a single wedge (no similar wedges in other parts)."""
    target_voices = get_voice_assignment_for_spanner(wedge)
    
    if not target_voices:
        # If no specific voice assignment, apply soprano-only rule
        print(f"    Single {wedge['type']} with no voice assignment - applying to Soprano only")
        assignments['Soprano'].append(wedge)
    elif len(target_voices) == 1 and target_voices[0] == 'Soprano':
        # Rule: If only Soprano has wedge, apply to all parts
        print(f"    Single {wedge['type']} in Soprano - applying to all parts")
        for voice_name in assignments.keys():
            assignments[voice_name].append(copy.deepcopy(wedge))
    else:
        # Apply to specific voices
        for voice_name in target_voices:
            if voice_name in assignments:
                assignments[voice_name].append(wedge)
                print(f"    Assigned {wedge['type']} to {voice_name}")


def apply_multiple_wedge_rules(wedge_group: List[Dict[str, Any]], assignments: Dict[str, List[Dict[str, Any]]]) -> None:
    """Apply rules for multiple wedges occurring at similar times."""
    wedge_type = wedge_group[0]['type']
    
    # Check if Soprano and Bass both have this wedge type
    has_soprano = any(w for w in wedge_group if 'Soprano' in get_voice_assignment_for_spanner(w))
    has_bass = any(w for w in wedge_group if 'Bass' in get_voice_assignment_for_spanner(w))
    
    if has_soprano and has_bass:
        # Rule: If Soprano and Bass have matching wedges, apply to all parts
        print(f"    Multiple {wedge_type} in Soprano and Bass - applying to all parts")
        representative_wedge = wedge_group[0]
        for voice_name in assignments.keys():
            assignments[voice_name].append(copy.deepcopy(representative_wedge))
    else:
        # Apply each wedge to its specific voice
        for wedge in wedge_group:
            target_voices = get_voice_assignment_for_spanner(wedge)
            for voice_name in target_voices:
                if voice_name in assignments:
                    assignments[voice_name].append(wedge)
                    print(f"    Assigned {wedge['type']} to {voice_name}")


# Import function to avoid circular imports - moved to top level
def get_voice_assignment_for_spanner(spanner_info: Dict[str, Any]) -> List[str]:
    """Get voice assignment for a spanner (imported to avoid circular import)."""
    from .spanner_extractor import get_voice_assignment_for_spanner as get_assignment
    return get_assignment(spanner_info)


def extract_dynamics_from_part(part):
    """Extract all dynamics from a music21 Part."""
    dynamics = []
    
    # Extract regular dynamics from measures
    for measure in part.getElementsByClass(music21.stream.Measure):
        for dynamic in measure.getElementsByClass(music21.dynamics.Dynamic):
            dynamics.append({
                'measure': measure.number,
                'offset': dynamic.offset,
                'value': str(dynamic),
                'object': dynamic,
                'type': 'measure'
            })
    
    return dynamics


def extract_lyrics_from_part(part):
    """Extract all lyrics from a music21 Part."""
    lyrics = []
    for measure in part.getElementsByClass(music21.stream.Measure):
        for note in measure.getElementsByClass(music21.note.Note):
            if note.lyric:
                lyrics.append({
                    'measure': measure.number,
                    'offset': note.offset,
                    'text': note.lyric,
                    'note': note
                })
    return lyrics


def unify_dynamics(voices_dict, soprano_dynamics, alto_dynamics, tenor_dynamics, bass_dynamics):
    """Apply dynamics unification rules."""
    # Rule 1: If only Soprano has dynamics, apply to all parts
    if soprano_dynamics and not alto_dynamics and not tenor_dynamics and not bass_dynamics:
        print("  Dynamics unification: Only Soprano has dynamics - applying to all parts")
        copy_dynamics_to_parts(soprano_dynamics, ['Alto', 'Tenor', 'Bass'], voices_dict)
        return
    
    # Rule 2: If Soprano and Tenor have matching dynamics, apply to all parts  
    if soprano_dynamics and tenor_dynamics:
        if dynamics_match(soprano_dynamics, tenor_dynamics):
            print("  Dynamics unification: Soprano and Tenor have matching dynamics - applying to all parts")
            copy_dynamics_to_parts(soprano_dynamics, ['Alto', 'Bass'], voices_dict)
            return
    
    # Rule 3: If Soprano and Bass have matching dynamics, apply to all parts
    if soprano_dynamics and bass_dynamics:
        if dynamics_match(soprano_dynamics, bass_dynamics):
            print("  Dynamics unification: Soprano and Bass have matching dynamics - applying to all parts")
            copy_dynamics_to_parts(soprano_dynamics, ['Alto', 'Tenor'], voices_dict)
            return
    
    print("  Dynamics unification: No unification rules apply - keeping original dynamics")


def unify_lyrics(voices_dict, soprano_lyrics, alto_lyrics, tenor_lyrics, bass_lyrics):
    """Apply lyrics unification rules."""
    soprano_count = len(soprano_lyrics)
    alto_count = len(alto_lyrics)
    tenor_count = len(tenor_lyrics)
    bass_count = len(bass_lyrics)
    
    # If Soprano has significantly more lyrics than others, apply to parts with no lyrics
    other_max = max(alto_count, tenor_count, bass_count)
    if soprano_count > 0 and soprano_count >= other_max * 3:
        print(f"  Lyrics unification: Soprano has majority of lyrics ({soprano_count} vs max {other_max}) - applying to parts with no lyrics")
        
        target_parts = []
        if alto_count == 0:
            target_parts.append('Alto')
        if tenor_count == 0:
            target_parts.append('Tenor')
        if bass_count == 0:
            target_parts.append('Bass')
        
        if target_parts:
            copy_lyrics_to_parts(soprano_lyrics, target_parts, voices_dict)
        return
    
    print("  Lyrics unification: Multiple parts have lyrics - keeping original distribution")


def dynamics_match(dynamics1, dynamics2):
    """Check if two dynamics lists have matching dynamics at the same positions."""
    if len(dynamics1) != len(dynamics2):
        return False
    
    for d1, d2 in zip(dynamics1, dynamics2):
        # Handle part-level dynamics (measure = None)
        if d1['measure'] != d2['measure']:
            return False
        if abs(d1['offset'] - d2['offset']) > 0.1:
            return False
        if d1['value'] != d2['value']:
            return False
    return True


def copy_dynamics_to_parts(source_dynamics, target_part_names, voices_dict):
    """Copy dynamics from source to target parts."""
    for part_name in target_part_names:
        target_part = voices_dict[part_name]
        for dynamic_info in source_dynamics:
            original_dynamic = dynamic_info['object']
            new_dynamic = copy.deepcopy(original_dynamic)
            
            # Measure-level dynamic
            measure_num = dynamic_info['measure']
            offset = dynamic_info['offset']
            
            # Find the corresponding measure in the target part
            for measure in target_part.getElementsByClass(music21.stream.Measure):
                if measure.number == measure_num:
                    measure.insert(offset, new_dynamic)
                    print(f"    Copied measure-level {type(new_dynamic).__name__} to {part_name} measure {measure_num}")
                    break


def copy_lyrics_to_parts(source_lyrics, target_part_names, voices_dict):
    """Copy lyrics from source to target parts."""
    for part_name in target_part_names:
        target_part = voices_dict[part_name]
        for lyric_info in source_lyrics:
            measure_num = lyric_info['measure']
            offset = lyric_info['offset']
            lyric_text = lyric_info['text']
            
            # Find the corresponding measure and note in the target part
            for measure in target_part.getElementsByClass(music21.stream.Measure):
                if measure.number == measure_num:
                    for note in measure.getElementsByClass(music21.note.Note):
                        if abs(note.offset - offset) < 0.1:  # Find note at same position
                            if not note.lyric:  # Only add if note doesn't already have lyrics
                                note.lyric = lyric_text
                            break
                    break
