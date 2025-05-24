"""
Core voice splitting functionality for satb-split.
"""

import copy
from pathlib import Path

try:
    import music21
except ImportError:
    print("Error: music21 library not found. Please install with: uv add music21", file=sys.stderr)
    sys.exit(1)

from .converter import convert_mscz_to_musicxml
from .phase3_unification import apply_phase3_unification


def split_satb_voices(file_path):
    """Split a closed-score SATB file into separate voice parts.
    
    Args:
        file_path: Path to the input MuseScore file (.mscz or .musicxml)
        
    Returns:
        Dict mapping voice names to music21.stream.Part objects
    """
    print(f"=== Splitting SATB Voices from {file_path} ===")
    
    # Handle .mscz files by converting to .musicxml first
    input_path = Path(file_path)
    temp_musicxml = None
    
    if input_path.suffix.lower() == '.mscz':
        try:
            temp_musicxml = convert_mscz_to_musicxml(input_path)
            file_path = str(temp_musicxml)
            print(f"Using converted file: {file_path}")
        except Exception as e:
            print(f"Warning: Could not convert .mscz file: {e}")
            print("Attempting direct music21 parsing of .mscz file...")
    
    try:
        # Load the score
        score = music21.converter.parse(str(file_path))
    finally:
        # Clean up temporary file if created
        if temp_musicxml and temp_musicxml.exists():
            temp_musicxml.unlink()
            print(f"Cleaned up temporary file: {temp_musicxml}")
    
    # Create empty parts for each voice
    soprano_part = music21.stream.Part()
    alto_part = music21.stream.Part()
    tenor_part = music21.stream.Part()
    bass_part = music21.stream.Part()
    
    # Set part names and clefs
    soprano_part.partName = "Soprano"
    alto_part.partName = "Alto"
    tenor_part.partName = "Tenor"
    bass_part.partName = "Bass"
    
    # Add appropriate clefs for each voice
    soprano_part.insert(0, music21.clef.TrebleClef())
    alto_part.insert(0, music21.clef.TrebleClef())
    tenor_part.insert(0, music21.clef.BassClef())
    bass_part.insert(0, music21.clef.BassClef())
    
    # Copy metadata and global elements to each part
    for part in [soprano_part, alto_part, tenor_part, bass_part]:
        # Copy time signatures, key signatures, etc.
        for element in score.getElementsByClass([music21.meter.TimeSignature, 
                                               music21.key.KeySignature,
                                               music21.tempo.TempoIndication]):
            # Create a copy to avoid reusing the same object
            element_copy = copy.deepcopy(element)
            part.insert(0, element_copy)
    
    # Get all measures from the first part to establish unified measure numbering
    first_part_measures = list(score.parts[0].getElementsByClass(music21.stream.Measure))
    total_measures = len(first_part_measures)
    print(f"\nEstablishing unified measure numbering: 1-{total_measures}")
    
    # Create unified measures for all SATB parts
    soprano_measures = []
    alto_measures = []
    tenor_measures = []
    bass_measures = []
    
    for measure_num in range(1, total_measures + 1):
        soprano_measures.append(music21.stream.Measure(number=measure_num))
        alto_measures.append(music21.stream.Measure(number=measure_num))
        tenor_measures.append(music21.stream.Measure(number=measure_num))
        bass_measures.append(music21.stream.Measure(number=measure_num))
    
    # Process each part in the original score
    for part_idx, original_part in enumerate(score.parts):
        print(f"\nProcessing Part {part_idx + 1}: {original_part.partName}")
        
        # Get all measures in this part
        measures = list(original_part.getElementsByClass(music21.stream.Measure))
        print(f"  Found {len(measures)} measures")
        
        # Process each measure
        for measure_idx, measure in enumerate(measures):
            # Get all voices in this measure
            voices = list(measure.getElementsByClass(music21.stream.Voice))
            print(f"  Measure {measure_idx + 1}: {len(voices)} voices")
            
            # Get target measures from our unified numbering system
            if measure_idx < len(soprano_measures):
                soprano_measure = soprano_measures[measure_idx]
                alto_measure = alto_measures[measure_idx]
                tenor_measure = tenor_measures[measure_idx]
                bass_measure = bass_measures[measure_idx]
            else:
                print(f"    Warning: Measure index {measure_idx} out of range")
                continue
            
            # Map voices to SATB parts based on typical closed score layout
            voice_mapping = {
                # Part 1 (treble clef): Voice 1 = Soprano, Voice 2 = Alto
                # Part 2 (bass clef): Voice 5 = Tenor, Voice 6 = Bass (based on observed voice IDs)
                (0, '1'): soprano_measure,  # Part 1, Voice 1 -> Soprano
                (0, '2'): alto_measure,     # Part 1, Voice 2 -> Alto
                (1, '5'): tenor_measure,    # Part 2, Voice 5 -> Tenor
                (1, '6'): bass_measure,     # Part 2, Voice 6 -> Bass
            }
            
            # Extract all musical elements at measure level with their positions
            measure_dynamics = []
            measure_slurs = []
            measure_expressions = []
            measure_tempos = []
            
            # Get all dynamics with positions
            for dynamic in measure.getElementsByClass(music21.dynamics.Dynamic):
                measure_dynamics.append((dynamic.offset, dynamic))
            
            # Get all slurs with positions  
            for slur in measure.getElementsByClass(music21.spanner.Slur):
                measure_slurs.append((slur.offset, slur))
            
            # Get all text expressions (including tempo markings) with positions
            for expr in measure.getElementsByClass(music21.expressions.TextExpression):
                measure_expressions.append((expr.offset, expr))
            
            # Get all tempo indications with positions
            for tempo in measure.getElementsByClass(music21.tempo.TempoIndication):
                measure_tempos.append((tempo.offset, tempo))
            
            # Also check for direction-type elements (like "Andante")
            for direction in measure.getElementsByClass(music21.expressions.TextExpression):
                if hasattr(direction, 'content') and 'andante' in str(direction.content).lower():
                    measure_expressions.append((direction.offset, direction))
            
            # Extract content from each voice
            for voice in voices:
                voice_id = str(voice.id) if voice.id else 'unknown'
                print(f"    Voice {voice_id}: ", end="")
                
                # Get target measure based on part and voice
                key = (part_idx, voice_id)
                if key in voice_mapping:
                    target_measure = voice_mapping[key]
                    voice_name = {
                        (0, '1'): 'Soprano',
                        (0, '2'): 'Alto', 
                        (1, '5'): 'Tenor',
                        (1, '6'): 'Bass'
                    }[key]
                    
                    # Copy all notes and rests from this voice
                    notes = list(voice.getElementsByClass(music21.note.Note))
                    rests = list(voice.getElementsByClass(music21.note.Rest))
                    
                    # Extract dynamics and other musical elements from voice level with positions
                    voice_dynamics = []
                    voice_slurs = []
                    voice_expressions = []
                    voice_tempos = []
                    
                    for dynamic in voice.getElementsByClass(music21.dynamics.Dynamic):
                        voice_dynamics.append((dynamic.offset, dynamic))
                    for slur in voice.getElementsByClass(music21.spanner.Slur):
                        voice_slurs.append((slur.offset, slur))
                    for expr in voice.getElementsByClass(music21.expressions.TextExpression):
                        voice_expressions.append((expr.offset, expr))
                    for tempo in voice.getElementsByClass(music21.tempo.TempoIndication):
                        voice_tempos.append((tempo.offset, tempo))
                    
                    # Combine voice-level and measure-level elements
                    all_dynamics = voice_dynamics + measure_dynamics
                    all_slurs = voice_slurs + measure_slurs
                    all_expressions = voice_expressions + measure_expressions
                    all_tempos = voice_tempos + measure_tempos
                    
                    print(f"{len(notes)} notes, {len(rests)} rests, {len(all_dynamics)} dynamics, {len(all_slurs)} slurs, {len(all_expressions)} expressions, {len(all_tempos)} tempos -> {voice_name}")
                    
                    # Add notes and rests to target measure (with copies to avoid object reuse)
                    for note in notes:
                        target_measure.append(copy.deepcopy(note))
                    for rest in rests:
                        target_measure.append(copy.deepcopy(rest))
                    
                    # Add dynamics, slurs, expressions, and tempos at their correct positions (with copies)
                    for offset, dynamic in all_dynamics:
                        dynamic_copy = copy.deepcopy(dynamic)
                        target_measure.insert(offset, dynamic_copy)
                    for offset, slur in all_slurs:
                        slur_copy = copy.deepcopy(slur)
                        target_measure.insert(offset, slur_copy)
                    for offset, expression in all_expressions:
                        expr_copy = copy.deepcopy(expression)
                        target_measure.insert(offset, expr_copy)
                    for offset, tempo in all_tempos:
                        tempo_copy = copy.deepcopy(tempo)
                        target_measure.insert(offset, tempo_copy)
                else:
                    print(f"unmapped voice (part={part_idx}, voice={voice_id})")
    
    # Add all measures to their respective parts with unified numbering
    print(f"\nAdding {total_measures} measures to each SATB part...")
    for measure in soprano_measures:
        soprano_part.append(measure)
    for measure in alto_measures:
        alto_part.append(measure)
    for measure in tenor_measures:
        tenor_part.append(measure)
    for measure in bass_measures:
        bass_part.append(measure)
    
    # Return the split voices
    result = {
        'Soprano': soprano_part,
        'Alto': alto_part,
        'Tenor': tenor_part,
        'Bass': bass_part
    }
    
    print(f"\n=== Voice Splitting Complete ===")
    for voice_name, part in result.items():
        measures = list(part.getElementsByClass(music21.stream.Measure))
        total_notes = sum(len(list(measure.getElementsByClass(music21.note.Note))) for measure in measures)
        total_dynamics = sum(len(list(measure.getElementsByClass(music21.dynamics.Dynamic))) for measure in measures)
        print(f"{voice_name}: {len(measures)} measures, {total_notes} total notes, {total_dynamics} dynamics")
    
    # Apply Phase 3 unification rules
    print(f"\n=== Applying Phase 3 Unification Rules ===")
    apply_phase3_unification(result)
    
    return result
