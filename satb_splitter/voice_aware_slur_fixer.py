"""
Voice-aware slur preservation that maintains note mappings during extraction.
"""

import music21
import copy
from typing import Dict, List, Any, Optional


class VoiceAwareSlurFixer:
    """Preserve slurs during voice separation with proper note tracking."""
    
    def __init__(self):
        """Initialize the voice-aware slur fixer."""
        self.note_mappings = {}  # original_note -> extracted_note
        
    def preserve_slurs_with_note_tracking(self, 
                                        original_score: music21.stream.Score,
                                        voice_scores: Dict[str, music21.stream.Score],
                                        voice_mapping: Dict[str, List[str]]) -> None:
        """
        Preserve slurs by tracking note mappings during voice extraction.
        
        Args:
            original_score: Original SATB score
            voice_scores: Dictionary of separated voice scores  
            voice_mapping: Maps voice names to voice IDs
        """
        print("🎵 Voice-aware slur preservation starting...")
        
        # Get all original slurs
        original_slurs = []
        for part in original_score.parts:
            for spanner in part.flatten().getElementsByClass('Spanner'):
                if hasattr(spanner, 'classes') and 'Slur' in spanner.classes:
                    original_slurs.append(spanner)
        
        print(f"  Found {len(original_slurs)} slurs in original score")
        
        # Build note mappings for each voice
        for voice_name, voice_score in voice_scores.items():
            if voice_name not in voice_mapping:
                continue
                
            print(f"  Building note mapping for {voice_name}...")
            voice_ids = voice_mapping[voice_name]
            self._build_note_mapping(original_score, voice_score, voice_ids, voice_name)
        
        # Apply slurs using note mappings
        for voice_name, voice_score in voice_scores.items():
            if voice_name not in voice_mapping:
                continue
                
            print(f"  Adding slurs to {voice_name}...")
            self._add_slurs_with_mapping(original_slurs, voice_score, voice_name)
    
    def _build_note_mapping(self, original_score, voice_score, voice_ids, voice_name):
        """Build mapping between original notes and extracted notes."""
        if not voice_score.parts:
            return
            
        voice_part = voice_score.parts[0]
        
        # Get all notes from original score that belong to this voice
        original_voice_notes = []
        for part_idx, part in enumerate(original_score.parts):
            for measure in part.getElementsByClass('Measure'):
                for note in measure.flatten().notes:
                    if hasattr(note, 'voice') and note.voice in voice_ids:
                        original_voice_notes.append({
                            'note': note,
                            'part_idx': part_idx,
                            'measure': getattr(measure, 'number', None),
                            'offset': getattr(note, 'offset', None),
                            'pitch': note.pitch.name + str(note.pitch.octave)
                        })
        
        # Get all notes from extracted voice
        extracted_notes = []
        for measure in voice_part.getElementsByClass('Measure'):
            for note in measure.flatten().notes:
                extracted_notes.append({
                    'note': note,
                    'measure': getattr(measure, 'number', None),
                    'offset': getattr(note, 'offset', None),
                    'pitch': note.pitch.name + str(note.pitch.octave)
                })
        
        print(f"    Original voice notes: {len(original_voice_notes)}")
        print(f"    Extracted notes: {len(extracted_notes)}")
        
        # Match notes by measure, pitch, and position
        for orig_info in original_voice_notes:
            best_match = None
            best_score = -1
            
            for ext_info in extracted_notes:
                score = 0
                
                # Same pitch (required)
                if orig_info['pitch'] != ext_info['pitch']:
                    continue
                    
                score += 10
                
                # Same measure (highly preferred)
                if orig_info['measure'] and ext_info['measure']:
                    if orig_info['measure'] == ext_info['measure']:
                        score += 100
                
                # Similar offset (preferred)
                if orig_info['offset'] is not None and ext_info['offset'] is not None:
                    if abs(orig_info['offset'] - ext_info['offset']) < 0.1:
                        score += 10
                
                if score > best_score:
                    best_score = score
                    best_match = ext_info
            
            if best_match and best_score > 10:  # Minimum: same pitch
                self.note_mappings[orig_info['note']] = best_match['note']
        
        print(f"    Created {len(self.note_mappings)} note mappings for {voice_name}")
    
    def _add_slurs_with_mapping(self, original_slurs, voice_score, voice_name):
        """Add slurs using the note mappings."""
        if not voice_score.parts:
            return
            
        voice_part = voice_score.parts[0]
        slurs_added = 0
        
        for slur in original_slurs:
            try:
                spanned_elements = slur.getSpannedElements()
                if len(spanned_elements) < 2:
                    continue
                
                start_note = spanned_elements[0]
                end_note = spanned_elements[-1]
                
                # Find mapped notes
                mapped_start = self.note_mappings.get(start_note)
                mapped_end = self.note_mappings.get(end_note)
                
                if mapped_start and mapped_end and mapped_start != mapped_end:
                    # Create new slur
                    new_slur = music21.spanner.Slur()
                    new_slur.addSpannedElements([mapped_start, mapped_end])
                    voice_part.append(new_slur)
                    slurs_added += 1
                    
                    start_pitch = start_note.pitch.name + str(start_note.pitch.octave)
                    end_pitch = end_note.pitch.name + str(end_note.pitch.octave)
                    print(f"    ✅ Added slur: {start_pitch} → {end_pitch}")
            
            except Exception as e:
                pass
        
        print(f"    Added {slurs_added} slurs to {voice_name}")


def add_voice_aware_slur_preservation(original_score: music21.stream.Score,
                                    voice_scores: Dict[str, music21.stream.Score]) -> None:
    """
    Voice-aware slur preservation function.
    
    Args:
        original_score: The original SATB score
        voice_scores: Dictionary of separated voice scores
    """
    # Voice mapping (adjust if needed)
    voice_mapping = {
        'Soprano': ['1'],
        'Alto': ['2'], 
        'Tenor': ['5'],
        'Bass': ['6']
    }
    
    fixer = VoiceAwareSlurFixer()
    fixer.preserve_slurs_with_note_tracking(original_score, voice_scores, voice_mapping)