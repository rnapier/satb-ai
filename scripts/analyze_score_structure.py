#!/usr/bin/env python3
"""
Comprehensive diagnostic tool to analyze score structure and voice distribution.

This tool provides detailed analysis of how "Crossing The Bar" (or any SATB score) 
is structured to inform deterministic voice mapping rules.
"""

from music21 import converter
from pathlib import Path
from satb_splitter.voice_identifier import VoiceIdentifier
import statistics
from collections import defaultdict


def analyze_score_structure(score_path: str = "Crossing The Bar.musicxml"):
    """
    Comprehensive analysis of score structure for deterministic voice mapping.
    
    Args:
        score_path: Path to the MusicXML score file
    """
    score_file = Path(score_path)
    
    if not score_file.exists():
        print(f"❌ Score file not found: {score_path}")
        return
    
    print(f"=== SCORE STRUCTURE ANALYSIS: {score_file.name} ===")
    
    # Load the score
    score = converter.parse(str(score_file))
    
    # Basic score information
    print(f"\n📊 BASIC INFORMATION")
    print(f"Total Parts: {len(score.parts)}")
    
    # Count total measures
    max_measures = 0
    for part in score.parts:
        measures = part.getElementsByClass('Measure')
        max_measures = max(max_measures, len(measures))
    print(f"Total Measures: {max_measures}")
    
    # Analyze each part in detail
    print(f"\n📋 PART STRUCTURE ANALYSIS")
    
    part_analysis = []
    for part_idx, part in enumerate(score.parts):
        print(f"\n--- Part {part_idx + 1} ---")
        
        # Part metadata
        part_name = getattr(part, 'partName', f'Part {part_idx + 1}')
        part_abbrev = getattr(part, 'partAbbreviation', '')
        print(f"Name: {part_name}")
        if part_abbrev:
            print(f"Abbreviation: {part_abbrev}")
        
        # Analyze voices within this part
        voice_analysis = analyze_voices_in_part(part, part_idx + 1)
        part_analysis.append({
            'part_idx': part_idx,
            'part_name': part_name,
            'part_abbrev': part_abbrev,
            'voices': voice_analysis
        })
    
    # Analyze current heuristic system results
    print(f"\n🤖 CURRENT HEURISTIC ANALYSIS")
    analyze_current_heuristics(score)
    
    # Provide deterministic mapping recommendations
    print(f"\n💡 DETERMINISTIC MAPPING RECOMMENDATIONS")
    recommend_deterministic_rules(part_analysis)
    
    # Analyze measure-specific variations (sample)
    print(f"\n📏 MEASURE-BY-MEASURE VARIATION ANALYSIS")
    analyze_measure_variations(score, sample_measures=[1, 4, 15, 29, max_measures])
    
    # Summary and conclusions
    print(f"\n📋 SUMMARY AND CONCLUSIONS")
    provide_mapping_conclusions(part_analysis)


def analyze_voices_in_part(part, part_number):
    """Analyze voice distribution within a single part."""
    
    voice_info = {}
    
    # Collect voice statistics
    voice_notes = defaultdict(list)
    voice_pitches = defaultdict(list)
    
    for measure in part.getElementsByClass('Measure'):
        # Check for explicit voices
        voices = measure.voices
        
        if voices:
            # Part has explicit voice separation
            for voice_idx, voice in enumerate(voices):
                voice_id = voice.id or f"voice_{voice_idx + 1}"
                
                for note in voice.notes:
                    if hasattr(note, 'pitch'):
                        voice_notes[voice_id].append(note)
                        voice_pitches[voice_id].append(note.pitch.midi)
        else:
            # No explicit voices - treat as single voice
            voice_id = "voice_1"
            for note in measure.notes:
                if hasattr(note, 'pitch'):
                    voice_notes[voice_id].append(note)
                    voice_pitches[voice_id].append(note.pitch.midi)
    
    # Analyze each voice
    for voice_id, notes in voice_notes.items():
        if not notes:
            continue
            
        pitches = voice_pitches[voice_id]
        
        # Calculate statistics
        note_count = len(notes)
        pitch_min = min(pitches)
        pitch_max = max(pitches)
        pitch_mean = statistics.mean(pitches)
        pitch_range = pitch_max - pitch_min
        
        # Convert MIDI to note names
        from music21 import pitch
        min_note = pitch.Pitch(midi=pitch_min)
        max_note = pitch.Pitch(midi=pitch_max)
        mean_note = pitch.Pitch(midi=int(pitch_mean))
        
        # Determine likely voice type based on range
        likely_voice = determine_likely_voice_type(pitch_min, pitch_max, pitch_mean)
        
        voice_info[voice_id] = {
            'note_count': note_count,
            'pitch_min': pitch_min,
            'pitch_max': pitch_max,
            'pitch_mean': pitch_mean,
            'pitch_range': pitch_range,
            'min_note': str(min_note),
            'max_note': str(max_note),
            'mean_note': str(mean_note),
            'likely_voice': likely_voice
        }
        
        print(f"  {voice_id}:")
        print(f"    Notes: {note_count}")
        print(f"    Range: {min_note} to {max_note} (MIDI {pitch_min}-{pitch_max})")
        print(f"    Mean: {mean_note} (MIDI {int(pitch_mean)})")
        print(f"    Likely Voice: {likely_voice}")
    
    return voice_info


def determine_likely_voice_type(pitch_min, pitch_max, pitch_mean):
    """Determine likely voice type based on pitch characteristics."""
    
    # Standard SATB ranges (MIDI numbers)
    voice_ranges = {
        'Soprano': {'min': 60, 'max': 84, 'center': 72},    # C4 to C6, center G4
        'Alto': {'min': 55, 'max': 79, 'center': 67},       # G3 to G5, center G4
        'Tenor': {'min': 48, 'max': 72, 'center': 60},      # C3 to C5, center C4
        'Bass': {'min': 40, 'max': 64, 'center': 52}        # E2 to E4, center E3
    }
    
    best_match = "Unknown"
    best_score = float('inf')
    
    for voice_type, ranges in voice_ranges.items():
        # Calculate how well this voice fits the expected range
        range_penalty = 0
        
        # Penalty for notes outside expected range
        if pitch_min < ranges['min']:
            range_penalty += (ranges['min'] - pitch_min) * 2
        if pitch_max > ranges['max']:
            range_penalty += (pitch_max - ranges['max']) * 2
        
        # Penalty for mean pitch distance from expected center
        center_penalty = abs(pitch_mean - ranges['center'])
        
        total_score = range_penalty + center_penalty
        
        if total_score < best_score:
            best_score = total_score
            best_match = voice_type
    
    return f"{best_match} (score: {best_score:.1f})"


def analyze_current_heuristics(score):
    """Analyze what the current heuristic system produces."""
    
    try:
        voice_identifier = VoiceIdentifier(score)
        voice_mapping = voice_identifier.analyze_score()
        
        print("Current heuristic assignments:")
        for voice_name, location in voice_mapping.items():
            confidence = getattr(location, 'confidence', 'unknown')
            part_idx = getattr(location, 'part_index', 'unknown')
            voice_idx = getattr(location, 'voice_index', 'unknown')
            
            print(f"  {voice_name}: Part {part_idx}, Voice {voice_idx} (confidence: {confidence})")
    
    except Exception as e:
        print(f"❌ Error analyzing current heuristics: {e}")


def recommend_deterministic_rules(part_analysis):
    """Recommend deterministic mapping rules based on analysis."""
    
    print("Based on the analysis, recommended deterministic rules:")
    
    if len(part_analysis) == 2:
        # Standard 2-staff SATB layout
        print("Standard 2-staff SATB layout detected:")
        print("  Staff 1, Voice 1 → Soprano")
        print("  Staff 1, Voice 2 → Alto") 
        print("  Staff 2, Voice 1 → Tenor")
        print("  Staff 2, Voice 2 → Bass")
    
    elif len(part_analysis) == 4:
        # 4-staff layout (one voice per staff)
        print("4-staff layout detected:")
        print("  Staff 1 → Soprano")
        print("  Staff 2 → Alto")
        print("  Staff 3 → Tenor") 
        print("  Staff 4 → Bass")
    
    elif len(part_analysis) == 1:
        # Single staff with multiple voices
        print("Single staff layout detected:")
        part = part_analysis[0]
        voice_count = len(part['voices'])
        
        if voice_count == 4:
            print("  Voice 1 → Soprano")
            print("  Voice 2 → Alto")
            print("  Voice 3 → Tenor")
            print("  Voice 4 → Bass")
        elif voice_count == 2:
            print("  Voice 1 → Soprano/Tenor (mixed)")
            print("  Voice 2 → Alto/Bass (mixed)")
    
    else:
        print(f"Unusual layout with {len(part_analysis)} parts - needs custom analysis")


def analyze_measure_variations(score, sample_measures):
    """Analyze how voice structure varies across different measures."""
    
    print("Sampling voice structure across key measures:")
    
    for measure_num in sample_measures:
        print(f"\nMeasure {measure_num}:")
        
        for part_idx, part in enumerate(score.parts):
            measures = part.getElementsByClass('Measure')
            
            if measure_num <= len(measures):
                measure = measures[measure_num - 1]  # Convert to 0-based
                
                # Count voices in this measure
                voices = measure.voices
                voice_count = len(voices) if voices else 1
                
                # Count notes
                note_count = len(measure.notes)
                
                print(f"  Part {part_idx + 1}: {voice_count} voices, {note_count} notes")
                
                # Check for special elements
                special_elements = []
                if measure.getElementsByClass('Dynamic'):
                    special_elements.append("dynamics")
                if measure.getElementsByClass('Spanner'):
                    special_elements.append("spanners") 
                if measure.getElementsByClass('Lyric'):
                    special_elements.append("lyrics")
                
                if special_elements:
                    print(f"    Special elements: {', '.join(special_elements)}")


def provide_mapping_conclusions(part_analysis):
    """Provide final conclusions and recommendations."""
    
    print("Key findings:")
    
    # Check for standard SATB patterns
    total_parts = len(part_analysis)
    total_voices = sum(len(part['voices']) for part in part_analysis)
    
    print(f"- Total parts: {total_parts}")
    print(f"- Total voices: {total_voices}")
    
    if total_parts == 2 and total_voices == 4:
        print("- Structure: Standard 2-staff SATB (recommended)")
        print("- Confidence: High - follows common conventions")
        print("- Mapping: Use positional rules (staff/voice index)")
    
    elif total_parts == 4 and total_voices == 4:
        print("- Structure: 4-staff SATB (one voice per staff)")
        print("- Confidence: High - clear voice separation")
        print("- Mapping: Use staff index only")
    
    else:
        print("- Structure: Non-standard layout")
        print("- Confidence: Medium - may need custom rules")
        print("- Mapping: Analyze pitch ranges for assignment")
    
    print("\nRecommendations:")
    print("1. Implement deterministic positional rules as primary method")
    print("2. Use pitch analysis as validation/fallback")
    print("3. Eliminate confidence-based scoring")
    print("4. Provide clear error messages for ambiguous cases")


if __name__ == "__main__":
    analyze_score_structure()