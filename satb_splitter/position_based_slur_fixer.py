"""
Position-based slur preservation that matches notes by measure and pitch.
"""

import music21
from typing import Dict, List, Any, Tuple


class PositionBasedSlurFixer:
    """Preserve slurs by matching notes based on their position in measures."""
    
    def __init__(self):
        """Initialize the position-based slur fixer."""
        pass
        
    def preserve_slurs_by_position(self, 
                                 original_score: music21.stream.Score,
                                 voice_scores: Dict[str, music21.stream.Score]) -> None:
        """
        Preserve slurs by finding notes at the same positions after voice separation.
        
        Args:
            original_score: Original SATB score
            voice_scores: Dictionary of separated voice scores
        """
        print("🎵 Position-based slur preservation starting...")
        
        # Extract all slurs with their note positions
        slur_data = self._extract_slur_positions(original_score)
        print(f"  Found {len(slur_data)} slurs in original score")
        
        # Apply slurs to each voice
        for voice_name, voice_score in voice_scores.items():
            print(f"  Processing {voice_name}...")
            self._add_slurs_by_position(slur_data, voice_score, voice_name)
    
    def _extract_slur_positions(self, score: music21.stream.Score) -> List[Dict]:
        """Extract slur information with note positions."""
        slur_data = []
        
        for part in score.parts:
            for spanner in part.flatten().getElementsByClass('Spanner'):
                if hasattr(spanner, 'classes') and 'Slur' in spanner.classes:
                    try:
                        spanned_elements = spanner.getSpannedElements()
                        if len(spanned_elements) >= 2:
                            start_note = spanned_elements[0]
                            end_note = spanned_elements[-1]
                            
                            start_pos = self._get_note_position(start_note)
                            end_pos = self._get_note_position(end_note)
                            
                            if start_pos and end_pos:
                                slur_data.append({
                                    'start_pos': start_pos,
                                    'end_pos': end_pos
                                })
                    except:
                        pass
        
        return slur_data
    
    def _get_note_position(self, note) -> Tuple[int, str, float]:
        """Get note position as (measure_number, pitch, offset)."""
        if not note or not hasattr(note, 'pitch'):
            return None
            
        measure_number = None
        offset = getattr(note, 'offset', 0)
        
        # Try to get measure number
        if hasattr(note, 'activeSite') and note.activeSite:
            if hasattr(note.activeSite, 'number'):
                measure_number = note.activeSite.number
        
        if measure_number is None:
            return None
            
        pitch = note.pitch.name + str(note.pitch.octave)
        return (measure_number, pitch, offset)
    
    def _add_slurs_by_position(self, slur_data: List[Dict], 
                             voice_score: music21.stream.Score, 
                             voice_name: str) -> None:
        """Add slurs to voice by finding notes at matching positions."""
        if not voice_score.parts:
            return
            
        voice_part = voice_score.parts[0]
        slurs_added = 0
        
        # Build position index of notes in this voice
        note_index = {}  # (measure, pitch, offset) -> note
        for measure in voice_part.getElementsByClass('Measure'):
            if not hasattr(measure, 'number'):
                continue
                
            for note in measure.flatten().notes:
                pitch = note.pitch.name + str(note.pitch.octave)
                offset = getattr(note, 'offset', 0)
                key = (measure.number, pitch, offset)
                note_index[key] = note
        
        # Try to match each slur
        for slur_info in slur_data:
            start_pos = slur_info['start_pos']
            end_pos = slur_info['end_pos']
            
            # Find exact matches first
            start_note = note_index.get(start_pos)
            end_note = note_index.get(end_pos)
            
            # If exact match fails, try looser matching (ignore offset)
            if not start_note:
                start_key = (start_pos[0], start_pos[1])  # (measure, pitch)
                for key, note in note_index.items():
                    if (key[0], key[1]) == start_key:
                        start_note = note
                        break
            
            if not end_note:
                end_key = (end_pos[0], end_pos[1])  # (measure, pitch)
                for key, note in note_index.items():
                    if (key[0], key[1]) == end_key:
                        end_note = note
                        break
            
            # Create slur if both notes found
            if start_note and end_note and start_note != end_note:
                new_slur = music21.spanner.Slur()
                new_slur.addSpannedElements([start_note, end_note])
                voice_part.append(new_slur)
                slurs_added += 1
                
                print(f"    ✅ Added slur: M{start_pos[0]} {start_pos[1]} → M{end_pos[0]} {end_pos[1]}")
        
        print(f"    Added {slurs_added} slurs to {voice_name}")


def add_position_based_slur_preservation(original_score: music21.stream.Score,
                                       voice_scores: Dict[str, music21.stream.Score]) -> None:
    """
    Position-based slur preservation function.
    
    Args:
        original_score: The original SATB score
        voice_scores: Dictionary of separated voice scores
    """
    fixer = PositionBasedSlurFixer()
    fixer.preserve_slurs_by_position(original_score, voice_scores)