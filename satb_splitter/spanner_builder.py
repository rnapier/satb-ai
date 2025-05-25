"""
Spanner reconstruction functionality for satb-split.
Rebuilds spanners in individual voice parts after voice splitting.
"""

import copy
import music21
from typing import Dict, List, Any


def rebuild_spanners_in_parts(voices_dict: Dict[str, music21.stream.Score], 
                             spanner_assignments: Dict[str, List[Dict[str, Any]]]) -> None:
    """
    Recreate spanners in individual voice parts based on assignments.
    
    Args:
        voices_dict: Dictionary mapping voice names to Score objects
        spanner_assignments: Dictionary mapping voice names to their assigned spanners
    """
    print("=== Rebuilding Spanners in Voice Parts ===")
    
    for voice_name, voice_score in voices_dict.items():
        voice_spanners = spanner_assignments.get(voice_name, [])
        if voice_spanners:
            print(f"Rebuilding {len(voice_spanners)} spanners for {voice_name}")
            voice_part = voice_score.parts[0]  # Get the single part in this voice score
            
            for spanner_info in voice_spanners:
                try:
                    recreate_spanner_in_part(voice_part, spanner_info)
                except Exception as e:
                    print(f"  Warning: Failed to recreate {spanner_info['type']} in {voice_name}: {e}")
        else:
            print(f"No spanners to rebuild for {voice_name}")


def recreate_spanner_in_part(part: music21.stream.Part, spanner_info: Dict[str, Any]) -> None:
    """
    Recreate a single spanner in a voice part.
    
    Args:
        part: music21.stream.Part to add the spanner to
        spanner_info: Information about the spanner to recreate
    """
    spanner_type = spanner_info['type']
    
    if spanner_type == 'Tie':
        recreate_tie_in_part(part, spanner_info)
    elif spanner_type == 'Slur':
        recreate_slur_in_part(part, spanner_info)
    elif spanner_type in ['Crescendo', 'Diminuendo']:
        recreate_wedge_in_part(part, spanner_info)
    else:
        print(f"    Warning: Unknown spanner type {spanner_type}, skipping")


def recreate_tie_in_part(part: music21.stream.Part, tie_info: Dict[str, Any]) -> None:
    """
    Recreate a tie in a voice part.
    Ties are handled as note attributes, not as separate spanner objects.
    
    Args:
        part: music21.stream.Part to add the tie to
        tie_info: Information about the tie
    """
    measure_number = tie_info['measure_number']
    note_pitch = tie_info['note_pitch']
    note_offset = tie_info['note_offset']
    tie_type = tie_info['tie_type']
    
    # Find the corresponding note in the target part
    target_note = find_note_in_part(part, measure_number, note_pitch, note_offset)
    
    if target_note:
        # Create and assign the tie
        if tie_type == 'start':
            target_note.tie = music21.tie.Tie('start')
        elif tie_type == 'stop':
            target_note.tie = music21.tie.Tie('stop')
        print(f"    Added tie ({tie_type}) to {note_pitch} in measure {measure_number}")
    else:
        print(f"    Warning: Could not find target note {note_pitch} at offset {note_offset} in measure {measure_number}")


def recreate_slur_in_part(part: music21.stream.Part, slur_info: Dict[str, Any]) -> None:
    """
    Recreate a slur in a voice part.
    
    Args:
        part: music21.stream.Part to add the slur to
        slur_info: Information about the slur
    """
    spanned_notes = slur_info['spanned_notes']
    
    if len(spanned_notes) < 2:
        print(f"    Warning: Slur needs at least 2 notes, found {len(spanned_notes)}")
        return
    
    # Find the corresponding notes in the target part
    target_notes = []
    for note_info in spanned_notes:
        target_note = find_note_in_part(
            part, 
            note_info.get('measure_number'),
            note_info['pitch'], 
            note_info['offset']
        )
        if target_note:
            target_notes.append(target_note)
    
    if len(target_notes) >= 2:
        # Create the slur
        slur = music21.spanner.Slur(target_notes)
        part.insert(0, slur)  # Insert at the beginning of the part
        print(f"    Added slur connecting {len(target_notes)} notes")
    else:
        print(f"    Warning: Could not find enough target notes for slur ({len(target_notes)}/{len(spanned_notes)})")


def recreate_wedge_in_part(part: music21.stream.Part, wedge_info: Dict[str, Any]) -> None:
    """
    Recreate a wedge (crescendo/diminuendo) in a voice part.
    
    Args:
        part: music21.stream.Part to add the wedge to
        wedge_info: Information about the wedge
    """
    wedge_type = wedge_info['type']
    spanned_notes = wedge_info['spanned_notes']
    
    if not spanned_notes:
        print(f"    Warning: {wedge_type} has no spanned notes")
        return
    
    # Find the corresponding notes in the target part
    target_notes = []
    for note_info in spanned_notes:
        target_note = find_note_in_part(
            part,
            note_info.get('measure_number'),
            note_info['pitch'],
            note_info['offset']
        )
        if target_note:
            target_notes.append(target_note)
    
    if target_notes:
        # Create the appropriate wedge type
        if wedge_type == 'Crescendo':
            wedge = music21.dynamics.Crescendo(target_notes)
        elif wedge_type == 'Diminuendo':
            wedge = music21.dynamics.Diminuendo(target_notes)
        else:
            print(f"    Warning: Unknown wedge type {wedge_type}")
            return
        
        part.insert(0, wedge)  # Insert at the beginning of the part
        print(f"    Added {wedge_type} spanning {len(target_notes)} notes")
    else:
        print(f"    Warning: Could not find target notes for {wedge_type}")


def find_note_in_part(part: music21.stream.Part, measure_number: int, pitch: str, offset: float) -> music21.note.Note:
    """
    Find a specific note in a part by measure, pitch, and offset.
    
    Args:
        part: music21.stream.Part to search in
        measure_number: Measure number to look in
        pitch: Pitch string to match
        offset: Offset within the measure
        
    Returns:
        The matching Note object, or None if not found
    """
    if measure_number is None:
        return None
    
    # Find the measure
    for measure in part.getElementsByClass(music21.stream.Measure):
        if measure.number == measure_number:
            # Look for the note with matching pitch and offset
            for note in measure.getElementsByClass(music21.note.Note):
                if (str(note.pitch) == pitch and 
                    abs(note.offset - offset) < 0.1):  # Small tolerance for floating point comparison
                    return note
            break
    
    return None


def validate_spanners_in_parts(voices_dict: Dict[str, music21.stream.Score]) -> Dict[str, Dict[str, int]]:
    """
    Validate that spanners have been properly recreated in voice parts.
    
    Args:
        voices_dict: Dictionary mapping voice names to Score objects
        
    Returns:
        Dictionary with validation results for each voice
    """
    print("=== Validating Spanners in Voice Parts ===")
    
    validation_results = {}
    
    for voice_name, voice_score in voices_dict.items():
        voice_part = voice_score.parts[0]
        
        # Count different types of spanners
        slurs = len(voice_part.getElementsByClass(music21.spanner.Slur))
        crescendos = len(voice_part.getElementsByClass(music21.dynamics.Crescendo))
        diminuendos = len(voice_part.getElementsByClass(music21.dynamics.Diminuendo))
        
        # Count tied notes
        tied_notes = 0
        for measure in voice_part.getElementsByClass(music21.stream.Measure):
            for note in measure.getElementsByClass(music21.note.Note):
                if hasattr(note, 'tie') and note.tie is not None:
                    tied_notes += 1
        
        validation_results[voice_name] = {
            'slurs': slurs,
            'crescendos': crescendos,
            'diminuendos': diminuendos,
            'tied_notes': tied_notes
        }
        
        total_spanners = slurs + crescendos + diminuendos
        print(f"{voice_name}: {total_spanners} spanners, {tied_notes} tied notes")
    
    return validation_results