"""
Unification rules for dynamics and lyrics in satb-split.
"""

import copy
import music21


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


def extract_dynamics_from_part(part):
    """Extract all dynamics from a music21 Part, including crescendos at part level."""
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
    
    # IMPORTANT: Also extract part-level crescendos/diminuendos
    # These are at the part level and don't belong to specific measures
    part_crescendos = list(part.getElementsByClass([music21.dynamics.Crescendo,
                                                  music21.dynamics.Diminuendo,
                                                  music21.dynamics.DynamicWedge]))
    for cresc in part_crescendos:
        dynamics.append({
            'measure': None,  # Part-level, not measure-specific
            'offset': cresc.offset,
            'value': str(cresc),
            'object': cresc,
            'type': 'part'
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
    """Copy dynamics from source to target parts, handling both measure and part-level dynamics."""
    for part_name in target_part_names:
        target_part = voices_dict[part_name]
        for dynamic_info in source_dynamics:
            original_dynamic = dynamic_info['object']
            new_dynamic = copy.deepcopy(original_dynamic)
            
            if dynamic_info['type'] == 'part':
                # Part-level dynamic (crescendo/diminuendo)
                target_part.insert(dynamic_info['offset'], new_dynamic)
                print(f"    Copied part-level {type(new_dynamic).__name__} to {part_name}")
            else:
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
