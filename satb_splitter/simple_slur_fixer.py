"""
Simple slur preservation for voice separation.
Based on successful minimal reproduction.
"""

import music21
import copy
from typing import Dict, List, Any


class SimpleSlurFixer:
    """Simple approach to preserve slurs during voice separation."""
    
    def __init__(self):
        """Initialize the slur fixer."""
        pass
    
    def preserve_slurs_for_voices(self, 
                                 original_score: music21.stream.Score,
                                 voice_scores: Dict[str, music21.stream.Score],
                                 voice_mapping: Dict[str, List[str]]) -> None:
        """
        Preserve slurs for separated voices using simple note matching.
        
        Args:
            original_score: Original SATB score
            voice_scores: Dictionary of separated voice scores  
            voice_mapping: Maps voice names to voice IDs (e.g., {'Alto': ['2']})
        """
        print("🎵 Simple slur preservation starting...")
        
        # Get all original slurs
        original_slurs = []
        for part in original_score.parts:
            for spanner in part.flatten().getElementsByClass('Spanner'):
                if hasattr(spanner, 'classes') and 'Slur' in spanner.classes:
                    original_slurs.append(spanner)
        
        print(f"  Found {len(original_slurs)} slurs in original score")
        
        # Process each voice
        for voice_name, voice_score in voice_scores.items():
            if voice_name not in voice_mapping:
                continue
                
            print(f"  Processing {voice_name}...")
            self._add_slurs_to_voice(original_slurs, voice_score, voice_name)
    
    def _add_slurs_to_voice(self,
                           original_slurs: List[Any],
                           voice_score: music21.stream.Score,
                           voice_name: str) -> None:
        """Add relevant slurs to a voice score with precise note matching."""
        slurs_added = 0
        
        if not voice_score.parts:
            return
            
        voice_part = voice_score.parts[0]
        
        for slur in original_slurs:
            try:
                # Get spanned elements
                spanned_elements = slur.getSpannedElements()
                if len(spanned_elements) < 2:
                    continue
                
                start_note = spanned_elements[0]
                end_note = spanned_elements[-1]
                
                # Find the exact notes in the voice that correspond to the original slur
                voice_start = self._find_corresponding_note(start_note, voice_part)
                voice_end = self._find_corresponding_note(end_note, voice_part)
                
                if voice_start and voice_end and voice_start != voice_end:
                    # Create new slur
                    new_slur = music21.spanner.Slur()
                    new_slur.addSpannedElements([voice_start, voice_end])
                    voice_part.append(new_slur)
                    slurs_added += 1
                    
                    start_pitch = start_note.pitch.name + str(start_note.pitch.octave)
                    end_pitch = end_note.pitch.name + str(end_note.pitch.octave)
                    print(f"    ✅ Added slur: {start_pitch} → {end_pitch}")
                
            except Exception as e:
                # Skip problematic slurs
                pass
        
        print(f"    Added {slurs_added} slurs to {voice_name}")
    
    def _find_corresponding_note(self, original_note, voice_part):
        """
        Find the note in the voice part that corresponds to the original note.
        Uses multiple criteria: pitch, offset, measure, and position.
        """
        if not original_note or not hasattr(original_note, 'pitch'):
            return None
            
        target_pitch = original_note.pitch.name + str(original_note.pitch.octave)
        target_offset = getattr(original_note, 'offset', None)
        
        # Try to get measure context
        target_measure = None
        if hasattr(original_note, 'activeSite') and original_note.activeSite:
            if hasattr(original_note.activeSite, 'number'):
                target_measure = original_note.activeSite.number
        
        # Find candidate notes with matching pitch
        candidates = []
        
        for measure in voice_part.getElementsByClass('Measure'):
            if target_measure and hasattr(measure, 'number') and measure.number != target_measure:
                continue
                
            for note in measure.flatten().notes:
                note_pitch = note.pitch.name + str(note.pitch.octave)
                if note_pitch == target_pitch:
                    candidates.append({
                        'note': note,
                        'measure': getattr(measure, 'number', None),
                        'offset': getattr(note, 'offset', None)
                    })
        
        if not candidates:
            return None
            
        # If only one candidate, use it
        if len(candidates) == 1:
            return candidates[0]['note']
        
        # Multiple candidates - use best match
        best_candidate = None
        best_score = -1
        
        for candidate in candidates:
            score = 0
            
            # Prefer same measure
            if target_measure and candidate['measure'] == target_measure:
                score += 10
            
            # Prefer same offset
            if target_offset is not None and candidate['offset'] is not None:
                if abs(target_offset - candidate['offset']) < 0.1:
                    score += 5
            
            # First candidate with positive score wins
            if score > best_score:
                best_score = score
                best_candidate = candidate
        
        return best_candidate['note'] if best_candidate else candidates[0]['note']


def add_simple_slur_preservation(original_score: music21.stream.Score,
                                voice_scores: Dict[str, music21.stream.Score]) -> None:
    """
    Simple function to add slur preservation after voice separation.
    
    Args:
        original_score: The original SATB score
        voice_scores: Dictionary of separated voice scores
    """
    # Simple voice mapping (adjust if needed)
    voice_mapping = {
        'Soprano': ['1'],
        'Alto': ['2'], 
        'Tenor': ['5'],
        'Bass': ['6']
    }
    
    fixer = SimpleSlurFixer()
    fixer.preserve_slurs_for_voices(original_score, voice_scores, voice_mapping)