#!/usr/bin/env python3
"""
Trace the exact order and timing of element processing in measure 4 to diagnose the timing issue.
"""

import music21
import copy

def trace_measure_4_processing():
    """Trace how measure 4 elements are processed during voice splitting."""
    print("=== Tracing Measure 4 Element Processing ===")
    
    # Load original score
    score = music21.converter.parse("Crossing The Bar.musicxml")
    
    # Get measure 4 from first part
    first_part = score.parts[0]
    measures = list(first_part.getElementsByClass(music21.stream.Measure))
    measure_4 = measures[3]  # 0-indexed
    
    print(f"\n1. Original Measure 4 Analysis:")
    print(f"   Measure number: {measure_4.number}")
    
    # Get voices in measure 4
    voices = list(measure_4.getElementsByClass(music21.stream.Voice))
    
    for voice in voices:
        voice_id = str(voice.id) if voice.id else 'unknown'
        if voice_id == '1':  # Focus on soprano voice
            print(f"\n2. Original Voice 1 (Soprano) Elements:")
            
            # Get ALL elements in voice, not just notes and rests
            all_elements = list(voice.elements)
            print(f"   Total elements in voice: {len(all_elements)}")
            
            # Show elements in their original order
            for i, element in enumerate(all_elements):
                element_type = type(element).__name__
                offset = element.offset
                if hasattr(element, 'duration'):
                    duration = element.duration.quarterLength
                else:
                    duration = 'N/A'
                
                if isinstance(element, music21.note.Note):
                    print(f"   [{i}] Offset {offset}: Note {element.pitch} (duration: {duration})")
                elif isinstance(element, music21.note.Rest):
                    print(f"   [{i}] Offset {offset}: Rest (duration: {duration})")
                else:
                    print(f"   [{i}] Offset {offset}: {element_type} (duration: {duration})")
            
            # Now trace how getElementsByClass retrieves them
            print(f"\n3. getElementsByClass([Note, Rest]) order:")
            notes_and_rests = list(voice.getElementsByClass([music21.note.Note, music21.note.Rest]))
            for i, element in enumerate(notes_and_rests):
                offset = element.offset
                duration = element.duration.quarterLength
                if isinstance(element, music21.note.Note):
                    print(f"   [{i}] Offset {offset}: Note {element.pitch} (duration: {duration})")
                else:
                    print(f"   [{i}] Offset {offset}: Rest (duration: {duration})")
            
            # Simulate the voice splitting process
            print(f"\n4. Simulating Voice Splitting Process:")
            target_measure = music21.stream.Measure(number=4)
            
            # Copy notes first (as done in original code)
            notes = list(voice.getElementsByClass(music21.note.Note))
            print(f"   Copying {len(notes)} notes:")
            for note in notes:
                note_copy = copy.deepcopy(note)
                print(f"     Adding Note {note.pitch} at offset {note.offset} (duration: {note.duration.quarterLength})")
                target_measure.append(note_copy)
            
            # Copy rests second (as done in original code)
            rests = list(voice.getElementsByClass(music21.note.Rest))
            print(f"   Copying {len(rests)} rests:")
            for rest in rests:
                rest_copy = copy.deepcopy(rest)
                print(f"     Adding Rest at offset {rest.offset} (duration: {rest.duration.quarterLength})")
                target_measure.append(rest_copy)
            
            # Check the resulting measure
            print(f"\n5. Resulting Target Measure:")
            result_elements = []
            for element in target_measure.getElementsByClass([music21.note.Note, music21.note.Rest]):
                result_elements.append((element.offset, element))
            
            # Sort by offset to see the final order
            result_elements.sort(key=lambda x: x[0])
            
            for offset, element in result_elements:
                if isinstance(element, music21.note.Note):
                    print(f"   Offset {offset}: Note {element.pitch} (duration: {element.duration.quarterLength})")
                else:
                    print(f"   Offset {offset}: Rest (duration: {element.duration.quarterLength})")
            
            # Check if Music21 auto-adjusted offsets
            print(f"\n6. Checking for Music21 Auto-Adjustment:")
            print(f"   Target measure duration: {target_measure.duration.quarterLength}")
            print(f"   Target measure elements count: {len(list(target_measure.getElementsByClass([music21.note.Note, music21.note.Rest])))}")
            
            # Test alternative approach: insert with explicit offsets
            print(f"\n7. Testing Alternative Approach (insert with explicit offsets):")
            alt_measure = music21.stream.Measure(number=4)
            
            # Get all notes and rests with their offsets, sorted by offset
            all_note_rest_elements = []
            for element in voice.getElementsByClass([music21.note.Note, music21.note.Rest]):
                all_note_rest_elements.append((element.offset, element))
            all_note_rest_elements.sort(key=lambda x: x[0])
            
            for offset, element in all_note_rest_elements:
                element_copy = copy.deepcopy(element)
                print(f"     Inserting at offset {offset}: {type(element).__name__}")
                alt_measure.insert(offset, element_copy)
            
            # Check the alternative result
            print(f"\n8. Alternative Approach Result:")
            alt_result_elements = []
            for element in alt_measure.getElementsByClass([music21.note.Note, music21.note.Rest]):
                alt_result_elements.append((element.offset, element))
            alt_result_elements.sort(key=lambda x: x[0])
            
            for offset, element in alt_result_elements:
                if isinstance(element, music21.note.Note):
                    print(f"   Offset {offset}: Note {element.pitch} (duration: {element.duration.quarterLength})")
                else:
                    print(f"   Offset {offset}: Rest (duration: {element.duration.quarterLength})")

if __name__ == "__main__":
    trace_measure_4_processing()