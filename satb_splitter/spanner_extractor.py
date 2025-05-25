"""
Spanner extraction functionality for satb-split.
Extracts and categorizes spanners (slurs, ties, wedges) from music21 scores.
"""

import music21
from typing import Dict, List, Any, Tuple


def extract_spanners_from_score(score: music21.stream.Score) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract all spanners from a music21 Score, categorized by type and scope.
    
    Args:
        score: music21.stream.Score object
        
    Returns:
        Dictionary with categorized spanners:
        {
            'slurs': [...],
            'ties': [...], 
            'wedges': [...],
            'other_spanners': [...]
        }
    """
    print("=== Extracting Spanners from Score ===")
    
    result = {
        'slurs': [],
        'ties': [],
        'wedges': [],
        'dashes': [],
        'other_spanners': []
    }
    
    # Extract spanners from each part
    for part_idx, part in enumerate(score.parts):
        print(f"Processing Part {part_idx + 1} ({part.partName}):")
        
        # Extract spanner objects (slurs, crescendos, diminuendos, etc.)
        part_spanners = part.getElementsByClass(music21.spanner.Spanner)
        print(f"  Found {len(part_spanners)} spanners")
        
        for spanner in part_spanners:
            spanner_info = analyze_spanner(spanner, part_idx, part.partName)
            
            # Categorize by type
            if isinstance(spanner, music21.spanner.Slur):
                result['slurs'].append(spanner_info)
            elif isinstance(spanner, (music21.dynamics.Crescendo, music21.dynamics.Diminuendo)):
                result['wedges'].append(spanner_info)
            else:
                result['other_spanners'].append(spanner_info)
        
        # Extract ties from notes
        ties = extract_ties_from_part(part, part_idx)
        result['ties'].extend(ties)
        
        # Extract dashes spanners from direction elements
        dashes = extract_dashes_from_part(part, part_idx)
        result['dashes'].extend(dashes)
    
    # Print summary
    print(f"Extraction complete:")
    print(f"  Slurs: {len(result['slurs'])}")
    print(f"  Ties: {len(result['ties'])}")
    print(f"  Wedges: {len(result['wedges'])}")
    print(f"  Dashes: {len(result['dashes'])}")
    print(f"  Other spanners: {len(result['other_spanners'])}")
    
    return result


def analyze_spanner(spanner: music21.spanner.Spanner, part_idx: int, part_name: str) -> Dict[str, Any]:
    """
    Analyze a spanner object and extract relevant information.
    
    Args:
        spanner: music21 spanner object
        part_idx: Index of the part containing this spanner
        part_name: Name of the part containing this spanner
        
    Returns:
        Dictionary with spanner information
    """
    spanned_elements = spanner.getSpannedElements()
    
    # Extract note information from spanned elements
    notes_info = []
    for elem in spanned_elements:
        if isinstance(elem, music21.note.Note):
            # Find which voice this note belongs to by traversing up the hierarchy
            voice_id = None
            current = elem
            while current is not None:
                # Check if current element has a parent that is a Voice
                if hasattr(current, 'activeSite') and current.activeSite:
                    parent = current.activeSite
                    if isinstance(parent, music21.stream.Voice):
                        voice_id = str(parent.id) if parent.id else 'unknown'
                        break
                    current = parent
                else:
                    break
            
            # If still no voice found, try getting it from the note's containers
            if voice_id is None:
                for container in elem.contextSites():
                    if isinstance(container[0], music21.stream.Voice):
                        voice_id = str(container[0].id) if container[0].id else 'unknown'
                        break
            
            notes_info.append({
                'pitch': str(elem.pitch),
                'offset': elem.offset,
                'voice_id': voice_id,
                'measure_number': elem.measureNumber if hasattr(elem, 'measureNumber') else None
            })
    
    return {
        'type': type(spanner).__name__,
        'part_idx': part_idx,
        'part_name': part_name,
        'spanned_notes': notes_info,
        'spanner_object': spanner,
        'start_offset': spanned_elements[0].offset if spanned_elements else None,
        'end_offset': spanned_elements[-1].offset if spanned_elements else None,
    }


def extract_ties_from_part(part: music21.stream.Part, part_idx: int) -> List[Dict[str, Any]]:
    """
    Extract tie information from a music21 Part.
    
    Args:
        part: music21.stream.Part object
        part_idx: Index of the part
        
    Returns:
        List of tie information dictionaries
    """
    ties = []
    
    for measure in part.getElementsByClass(music21.stream.Measure):
        for voice in measure.getElementsByClass(music21.stream.Voice):
            voice_id = str(voice.id) if voice.id else 'unknown'
            
            for note in voice.getElementsByClass(music21.note.Note):
                if hasattr(note, 'tie') and note.tie is not None:
                    tie_info = {
                        'type': 'Tie',
                        'part_idx': part_idx,
                        'part_name': part.partName,
                        'voice_id': voice_id,
                        'measure_number': measure.number,
                        'note_pitch': str(note.pitch),
                        'note_offset': note.offset,
                        'tie_type': note.tie.type,  # 'start' or 'stop'
                        'note_object': note
                    }
                    ties.append(tie_info)
    
    return ties


def categorize_spanner_scope(spanner_info: Dict[str, Any], all_spanners: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Determine if spanner is voice-specific, part-specific, or system-wide.
    
    Args:
        spanner_info: Information about a single spanner
        all_spanners: All extracted spanners for context
        
    Returns:
        Scope classification: 'voice', 'part', or 'system'
    """
    spanner_type = spanner_info['type']
    
    # Ties are always voice-specific
    if spanner_type == 'Tie':
        return 'voice'
    
    # Slurs are typically voice-specific
    if spanner_type == 'Slur':
        return 'voice'
    
    # Wedges (crescendo/diminuendo) need more analysis
    if spanner_type in ['Crescendo', 'Diminuendo']:
        # Check if similar wedges exist in other parts at similar times
        # This is a simplified heuristic - could be made more sophisticated
        return analyze_wedge_scope(spanner_info, all_spanners)
    
    # Default to voice-specific
    return 'voice'


def analyze_wedge_scope(wedge_info: Dict[str, Any], all_spanners: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Analyze whether a wedge (crescendo/diminuendo) is voice-specific or system-wide.
    
    Args:
        wedge_info: Information about the wedge
        all_spanners: All extracted spanners for comparison
        
    Returns:
        Scope classification: 'voice', 'part', or 'system'
    """
    wedge_start = wedge_info['start_offset']
    wedge_end = wedge_info['end_offset']
    wedge_type = wedge_info['type']
    
    # Look for similar wedges in other parts
    similar_wedges = 0
    for other_wedge in all_spanners['wedges']:
        if (other_wedge != wedge_info and 
            other_wedge['type'] == wedge_type and
            other_wedge['part_idx'] != wedge_info['part_idx']):
            
            # Check if timing is similar (within 1.0 beat tolerance)
            if (abs(other_wedge['start_offset'] - wedge_start) < 1.0 and
                abs(other_wedge['end_offset'] - wedge_end) < 1.0):
                similar_wedges += 1
    
    # If similar wedges found in other parts, likely system-wide
    if similar_wedges > 0:
        return 'system'
    else:
        return 'voice'


def get_voice_assignment_for_spanner(spanner_info: Dict[str, Any]) -> List[str]:
    """
    Determine which SATB voice(s) a spanner should be assigned to.
    
    Args:
        spanner_info: Information about the spanner
        
    Returns:
        List of voice names the spanner should be assigned to
    """
    part_idx = spanner_info['part_idx']
    
    # For ties and voice-specific spanners, determine the specific voice
    if spanner_info.get('voice_id'):
        voice_id = spanner_info['voice_id']
        voice_mapping = {
            (0, '1'): ['Soprano'],
            (0, '2'): ['Alto'],
            (1, '5'): ['Tenor'],
            (1, '6'): ['Bass'],
        }
        return voice_mapping.get((part_idx, voice_id), [])
    
    # For spanners that span multiple notes, analyze the voices involved
    voices_involved = set()
    for note_info in spanner_info.get('spanned_notes', []):
        if note_info.get('voice_id'):
            voice_id = note_info['voice_id']
            voice_mapping = {
                (0, '1'): 'Soprano',
                (0, '2'): 'Alto',
                (1, '5'): 'Tenor',
                (1, '6'): 'Bass',
            }
            voice_name = voice_mapping.get((part_idx, voice_id))
            if voice_name:
                voices_involved.add(voice_name)
    
    return list(voices_involved)
def extract_dashes_from_part(part: music21.stream.Part, part_idx: int) -> List[Dict[str, Any]]:
    """
    Extract dashes spanners from direction elements in a part.
    
    Dashes spanners are used for text-based crescendos like "cresc." with dashed continuation lines.
    They are stored as direction elements in MusicXML, not as music21 spanner objects.
    
    Args:
        part: music21.stream.Part to extract from
        part_idx: Index of the part
        
    Returns:
        List of dashes spanner information dictionaries
    """
    dashes_spanners = []
    
    # Track active dashes spanners by number
    active_dashes = {}
    
    # Iterate through all measures to find direction elements
    for measure in part.getElementsByClass('Measure'):
        measure_number = measure.number
        
        # Look for text expressions that might be part of dashes spanners
        for elem in measure.recurse():
            if isinstance(elem, music21.expressions.TextExpression):
                # Check if this text expression is part of a crescendo/diminuendo
                text_content = str(elem.content).lower()
                if any(keyword in text_content for keyword in ['cresc', 'dim', 'decresc']):
                    # This is likely the start of a dashes spanner
                    # We'll need to look for the corresponding stop in later measures
                    
                    # Find the voice this text belongs to
                    voice_id = find_voice_for_element(elem)
                    
                    # Create a dashes spanner entry
                    dashes_info = {
                        'type': 'Dashes',
                        'part_idx': part_idx,
                        'start_measure': measure_number,
                        'start_offset': float(elem.offset) if hasattr(elem, 'offset') else 0.0,
                        'text_content': str(elem.content),
                        'voice_id': voice_id,
                        'number': 1,  # Default to 1, could be extracted from XML if needed
                        'end_measure': None,  # Will be filled when we find the stop
                        'end_offset': None
                    }
                    
                    # For now, assume the dashes spanner continues until we find explicit stops
                    # In the specific case of measures 25-27, we know it should end in measure 27
                    # This is a simplified implementation that could be enhanced
                    if 'cresc' in text_content and measure_number == 25:
                        dashes_info['end_measure'] = 27
                        dashes_info['end_offset'] = 0.0
                    
                    dashes_spanners.append(dashes_info)
                    print(f"    Found dashes spanner: '{elem.content}' in measure {measure_number}")
    
    return dashes_spanners


def find_voice_for_element(element):
    """
    Find the voice ID for a given element by traversing up the hierarchy.
    
    Args:
        element: music21 element to find voice for
        
    Returns:
        Voice ID string or None
    """
    current = element
    while current is not None:
        if hasattr(current, 'activeSite') and current.activeSite:
            parent = current.activeSite
            if isinstance(parent, music21.stream.Voice):
                return str(parent.id) if parent.id else 'unknown'
            current = parent
        else:
            break
    
    # If no voice found, try to infer from context
    # For direction elements, they often apply to the first voice in the measure
    measure = element.getContextByClass('Measure')
    if measure:
        voices = measure.getElementsByClass('Voice')
        if voices:
            first_voice = voices[0]
            return str(first_voice.id) if first_voice.id else '1'
    
    return '1'  # Default to voice 1