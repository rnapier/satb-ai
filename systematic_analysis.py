#!/usr/bin/env python3
"""
Systematic analysis to check if the corruption affects multiple measures.
"""

import music21
from pathlib import Path

def analyze_measure_systematically(measure_number, base_score, voice_files):
    """Analyze a specific measure across all parts."""
    print(f"\n{'='*60}")
    print(f"ANALYZING MEASURE {measure_number}")
    print(f"{'='*60}")
    
    # Analyze base score
    base_data = {}
    for part_idx, part in enumerate(base_score.parts):
        part_name = f"Part {part_idx + 1}"
        measures = list(part.getElementsByClass(music21.stream.Measure))
        
        if measure_number <= len(measures):
            measure = measures[measure_number - 1]
            voices = list(measure.getElementsByClass(music21.stream.Voice))
            
            print(f"\n--- Base {part_name} ---")
            print(f"Measure offset: {measure.offset}")
            
            for voice in voices:
                voice_id = str(voice.id)
                notes = list(voice.getElementsByClass(music21.note.Note))
                rests = list(voice.getElementsByClass(music21.note.Rest))
                
                print(f"  Voice {voice_id}: {len(notes)} notes, {len(rests)} rests")
                
                voice_data = []
                for note in notes:
                    voice_data.append({
                        'type': 'note',
                        'pitch': f"{note.pitch.name}{note.pitch.octave}",
                        'duration': note.duration.quarterLength,
                        'offset': note.offset
                    })
                for rest in rests:
                    voice_data.append({
                        'type': 'rest',
                        'duration': rest.duration.quarterLength,
                        'offset': rest.offset
                    })
                
                base_data[f"Part{part_idx}_Voice{voice_id}"] = voice_data
    
    # Analyze voice parts
    voice_data = {}
    voice_names = ['Soprano', 'Alto', 'Tenor', 'Bass']
    
    for voice_name in voice_names:
        filename = f"Crossing The Bar-{voice_name}.musicxml"
        filepath = Path("Crossing The Bar_voices") / filename
        
        if not filepath.exists():
            print(f"\nERROR: {filepath} not found")
            continue
        
        print(f"\n--- {voice_name} Voice Part ---")
        score = music21.converter.parse(str(filepath))
        part = score.parts[0]
        measures = list(part.getElementsByClass(music21.stream.Measure))
        
        if measure_number <= len(measures):
            measure = measures[measure_number - 1]
            print(f"Measure offset: {measure.offset}")
            
            notes = list(measure.getElementsByClass(music21.note.Note))
            rests = list(measure.getElementsByClass(music21.note.Rest))
            
            print(f"  {len(notes)} notes, {len(rests)} rests")
            
            part_data = []
            for note in notes:
                part_data.append({
                    'type': 'note',
                    'pitch': f"{note.pitch.name}{note.pitch.octave}",
                    'duration': note.duration.quarterLength,
                    'offset': note.offset
                })
                print(f"    Note: {note.pitch.name}{note.pitch.octave} dur={note.duration.quarterLength} offset={note.offset}")
            
            for rest in rests:
                part_data.append({
                    'type': 'rest',
                    'duration': rest.duration.quarterLength,
                    'offset': rest.offset
                })
                print(f"    Rest: dur={rest.duration.quarterLength} offset={rest.offset}")
            
            voice_data[voice_name] = part_data
    
    # Compare and detect corruption
    print(f"\n--- CORRUPTION ANALYSIS FOR MEASURE {measure_number} ---")
    
    # Expected mapping
    mapping = {
        'Soprano': 'Part0_Voice1',
        'Alto': 'Part0_Voice2',
        'Tenor': 'Part1_Voice5',
        'Bass': 'Part1_Voice6'
    }
    
    corruptions_found = []
    
    for voice_name, base_key in mapping.items():
        if voice_name not in voice_data or base_key not in base_data:
            continue
        
        voice_elements = voice_data[voice_name]
        base_elements = base_data[base_key]
        
        print(f"\n{voice_name} vs {base_key}:")
        print(f"  Voice part: {len(voice_elements)} elements")
        print(f"  Base: {len(base_elements)} elements")
        
        # Check for obvious corruption signs
        corruption_detected = False
        
        # Check 1: Different number of elements
        if len(voice_elements) != len(base_elements):
            print(f"  ⚠️  CORRUPTION: Different element count")
            corruption_detected = True
        
        # Check 2: Check for unexpected rests
        voice_rests = [e for e in voice_elements if e['type'] == 'rest']
        base_rests = [e for e in base_elements if e['type'] == 'rest']
        
        if len(voice_rests) != len(base_rests):
            print(f"  ⚠️  CORRUPTION: Rest count mismatch (voice: {len(voice_rests)}, base: {len(base_rests)})")
            corruption_detected = True
        
        # Check 3: Check total duration
        voice_duration = sum(e['duration'] for e in voice_elements)
        base_duration = sum(e['duration'] for e in base_elements)
        
        if abs(voice_duration - base_duration) > 0.1:
            print(f"  ⚠️  CORRUPTION: Duration mismatch (voice: {voice_duration}, base: {base_duration})")
            corruption_detected = True
        
        # Check 4: Check for timing issues (gaps/overlaps)
        if len(voice_elements) > 1:
            voice_elements_sorted = sorted(voice_elements, key=lambda x: x['offset'])
            for i in range(len(voice_elements_sorted) - 1):
                current_end = voice_elements_sorted[i]['offset'] + voice_elements_sorted[i]['duration']
                next_start = voice_elements_sorted[i + 1]['offset']
                gap = next_start - current_end
                if abs(gap) > 0.1:  # More than 0.1 beat gap/overlap
                    print(f"  ⚠️  CORRUPTION: Timing gap/overlap of {gap} beats")
                    corruption_detected = True
        
        if corruption_detected:
            corruptions_found.append({
                'measure': measure_number,
                'voice': voice_name,
                'voice_elements': voice_elements,
                'base_elements': base_elements
            })
        else:
            print(f"  ✅ No corruption detected")
    
    return corruptions_found

def find_measures_with_dynamics():
    """Find measures that have dynamics, as these might be corruption hotspots."""
    print("=== FINDING MEASURES WITH DYNAMICS ===")
    
    base_score = music21.converter.parse('Crossing The Bar-base.musicxml')
    measures_with_dynamics = set()
    
    for part_idx, part in enumerate(base_score.parts):
        measures = list(part.getElementsByClass(music21.stream.Measure))
        for measure_idx, measure in enumerate(measures):
            dynamics = list(measure.getElementsByClass(music21.dynamics.Dynamic))
            if dynamics:
                measure_num = measure_idx + 1
                measures_with_dynamics.add(measure_num)
                print(f"  Measure {measure_num}: {len(dynamics)} dynamics")
                for dyn in dynamics:
                    print(f"    {dyn.value} at offset {dyn.offset}")
    
    return sorted(measures_with_dynamics)

def main():
    """Main analysis function."""
    print("=== SYSTEMATIC CORRUPTION ANALYSIS ===")
    
    # Load base score
    base_score = music21.converter.parse('Crossing The Bar-base.musicxml')
    
    # Voice files
    voice_files = {
        'Soprano': 'Crossing The Bar_voices/Crossing The Bar-Soprano.musicxml',
        'Alto': 'Crossing The Bar_voices/Crossing The Bar-Alto.musicxml',
        'Tenor': 'Crossing The Bar_voices/Crossing The Bar-Tenor.musicxml',
        'Bass': 'Crossing The Bar_voices/Crossing The Bar-Bass.musicxml'
    }
    
    # Find measures with dynamics (potential corruption hotspots)
    dynamic_measures = find_measures_with_dynamics()
    
    # Analyze key measures
    test_measures = [1, 4, 8, 16, 20, 24, 28, 29, 30, 32, 36]  # Sample across the piece
    test_measures.extend(dynamic_measures)  # Add all measures with dynamics
    test_measures = sorted(set(test_measures))  # Remove duplicates and sort
    
    print(f"\nTesting measures: {test_measures}")
    
    all_corruptions = []
    
    for measure_num in test_measures:
        corruptions = analyze_measure_systematically(measure_num, base_score, voice_files)
        all_corruptions.extend(corruptions)
    
    # Summary
    print(f"\n{'='*60}")
    print("CORRUPTION SUMMARY")
    print(f"{'='*60}")
    
    if all_corruptions:
        print(f"Found {len(all_corruptions)} corruptions:")
        
        corruption_by_voice = {}
        corruption_by_measure = {}
        
        for corruption in all_corruptions:
            voice = corruption['voice']
            measure = corruption['measure']
            
            if voice not in corruption_by_voice:
                corruption_by_voice[voice] = []
            corruption_by_voice[voice].append(measure)
            
            if measure not in corruption_by_measure:
                corruption_by_measure[measure] = []
            corruption_by_measure[measure].append(voice)
        
        print("\nBy voice:")
        for voice, measures in corruption_by_voice.items():
            print(f"  {voice}: measures {measures}")
        
        print("\nBy measure:")
        for measure, voices in corruption_by_measure.items():
            print(f"  Measure {measure}: {voices}")
        
        # Check if corruption correlates with dynamics
        dynamic_corruptions = [c for c in all_corruptions if c['measure'] in dynamic_measures]
        print(f"\nCorruptions in measures with dynamics: {len(dynamic_corruptions)}/{len(all_corruptions)}")
        
    else:
        print("No corruptions found in tested measures!")

if __name__ == "__main__":
    main()