#!/usr/bin/env python3
"""
Trace the exact source of Soprano measure offset drift.
"""

import music21
import copy
from pathlib import Path

def trace_full_voice_splitter_execution():
    """Trace the full voice splitter execution to find offset drift."""
    print("=== TRACING FULL VOICE SPLITTER EXECUTION ===")
    
    # Import the actual voice splitter
    from satb_splitter.voice_splitter import split_satb_voices
    
    # Run the actual voice splitter with detailed tracing
    print("Running actual voice splitter...")
    
    # Monkey patch the voice splitter to add tracing
    original_append = music21.stream.Part.append
    
    def traced_append(self, obj):
        if hasattr(obj, 'number') and hasattr(obj, 'offset'):
            if hasattr(self, 'partName') and self.partName == "Soprano":
                if 28 <= obj.number <= 30:
                    print(f"  TRACE: Adding measure {obj.number} to Soprano part")
                    print(f"    Before append: part duration = {self.duration.quarterLength}")
                    print(f"    Measure offset before append = {obj.offset}")
        
        result = original_append(self, obj)
        
        if hasattr(obj, 'number') and hasattr(obj, 'offset'):
            if hasattr(self, 'partName') and self.partName == "Soprano":
                if 28 <= obj.number <= 30:
                    print(f"    After append: part duration = {self.duration.quarterLength}")
                    print(f"    Measure offset after append = {obj.offset}")
        
        return result
    
    # Apply the monkey patch
    music21.stream.Part.append = traced_append
    
    try:
        # Run the voice splitter
        voices = split_satb_voices("Crossing The Bar.mscz")
        
        # Check the final results
        print("\n=== FINAL RESULTS ===")
        soprano_score = voices['Soprano']
        soprano_part = soprano_score.parts[0]
        
        measures = list(soprano_part.getElementsByClass(music21.stream.Measure))
        for measure in measures[27:30]:  # Measures 28-30
            print(f"Final Soprano measure {measure.number}: offset={measure.offset}")
            
            notes = list(measure.getElementsByClass(music21.note.Note))
            rests = list(measure.getElementsByClass(music21.note.Rest))
            
            for i, note in enumerate(notes):
                print(f"  Note {i+1}: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
            for i, rest in enumerate(rests):
                print(f"  Rest {i+1}: dur={rest.duration.quarterLength} offset={rest.offset}")
    
    finally:
        # Restore original function
        music21.stream.Part.append = original_append

def compare_all_voice_offsets():
    """Compare measure offsets across all voices to see the drift pattern."""
    print("\n=== COMPARING ALL VOICE OFFSETS ===")
    
    voice_files = {
        'Soprano': 'Crossing The Bar_voices/Crossing The Bar-Soprano.musicxml',
        'Alto': 'Crossing The Bar_voices/Crossing The Bar-Alto.musicxml',
        'Tenor': 'Crossing The Bar_voices/Crossing The Bar-Tenor.musicxml',
        'Bass': 'Crossing The Bar_voices/Crossing The Bar-Bass.musicxml'
    }
    
    # Load all voice parts
    voice_data = {}
    for voice_name, filepath in voice_files.items():
        if Path(filepath).exists():
            score = music21.converter.parse(filepath)
            part = score.parts[0]
            measures = list(part.getElementsByClass(music21.stream.Measure))
            voice_data[voice_name] = measures
    
    # Compare offsets for measures 25-35
    print("\nMeasure offset comparison:")
    print("Measure | Soprano | Alto    | Tenor   | Bass")
    print("--------|---------|---------|---------|--------")
    
    for measure_num in range(25, 36):
        measure_idx = measure_num - 1
        offsets = {}
        
        for voice_name, measures in voice_data.items():
            if measure_idx < len(measures):
                offsets[voice_name] = measures[measure_idx].offset
            else:
                offsets[voice_name] = "N/A"
        
        print(f"{measure_num:7} | {offsets.get('Soprano', 'N/A'):7} | {offsets.get('Alto', 'N/A'):7} | {offsets.get('Tenor', 'N/A'):7} | {offsets.get('Bass', 'N/A'):7}")
    
    # Calculate drift
    print("\nOffset drift analysis (difference from Tenor as baseline):")
    print("Measure | Soprano Drift | Alto Drift | Bass Drift")
    print("--------|---------------|------------|----------")
    
    for measure_num in range(25, 36):
        measure_idx = measure_num - 1
        
        if (measure_idx < len(voice_data.get('Tenor', [])) and 
            measure_idx < len(voice_data.get('Soprano', [])) and
            measure_idx < len(voice_data.get('Alto', [])) and
            measure_idx < len(voice_data.get('Bass', []))):
            
            tenor_offset = voice_data['Tenor'][measure_idx].offset
            soprano_offset = voice_data['Soprano'][measure_idx].offset
            alto_offset = voice_data['Alto'][measure_idx].offset
            bass_offset = voice_data['Bass'][measure_idx].offset
            
            soprano_drift = soprano_offset - tenor_offset
            alto_drift = alto_offset - tenor_offset
            bass_drift = bass_offset - tenor_offset
            
            print(f"{measure_num:7} | {soprano_drift:13.1f} | {alto_drift:10.1f} | {bass_drift:10.1f}")

def main():
    trace_full_voice_splitter_execution()
    compare_all_voice_offsets()

if __name__ == "__main__":
    main()