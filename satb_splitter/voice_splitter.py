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
from .unification import apply_unification


def split_satb_voices(file_path):
    """Split a closed-score SATB file into separate voice parts.
    
    Args:
        file_path: Path to the input MuseScore file (.mscz or .musicxml)
        
    Returns:
        Dict mapping voice names to music21.stream.Score objects
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
    
    # Create empty scores and parts for each voice
    soprano_score = music21.stream.Score()
    alto_score = music21.stream.Score()
    tenor_score = music21.stream.Score()
    bass_score = music21.stream.Score()
    
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
    
    # Copy metadata and global elements to each score
    for voice_score in [soprano_score, alto_score, tenor_score, bass_score]:
        # Copy all metadata to this score
        if score.metadata:
            voice_score.metadata = copy.deepcopy(score.metadata)
        
        # Copy layout elements from the original score to each voice score
        layout_elements = score.getElementsByClass([music21.layout.PageLayout, 
                                                   music21.layout.SystemLayout,
                                                   music21.layout.StaffLayout])
        for layout_elem in layout_elements:
            voice_score.insert(0, copy.deepcopy(layout_elem))
    
    # Copy global elements to each part
    for part in [soprano_part, alto_part, tenor_part, bass_part]:
        # Copy time signatures, key signatures, etc.
        for element in score.getElementsByClass([music21.meter.TimeSignature, 
                                               music21.key.KeySignature,
                                               music21.tempo.TempoIndication]):
            # Create a copy to avoid reusing the same object
            element_copy = copy.deepcopy(element)
            part.insert(0, element_copy)
    
    # Copy part-level crescendos and diminuendos to each SATB part
    # These exist at the part level (offset 0.0) and need special handling
    print(f"\n=== Copying Part-Level Crescendos ===")
    for original_part in score.parts:
        part_crescendos = list(original_part.getElementsByClass([music21.dynamics.Crescendo,
                                                               music21.dynamics.Diminuendo,
                                                               music21.dynamics.DynamicWedge]))
        if part_crescendos:
            print(f"Found {len(part_crescendos)} part-level crescendo/diminuendo elements")
            # Copy these to all SATB parts
            for target_part in [soprano_part, alto_part, tenor_part, bass_part]:
                for cresc in part_crescendos:
                    cresc_copy = copy.deepcopy(cresc)
                    target_part.insert(cresc.offset, cresc_copy)
                    print(f"  Copied {type(cresc).__name__} to {target_part.partName}")
    
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
            
            # Extract all musical elements at measure level with their positions (ONCE per measure)
            measure_dynamics = []
            measure_slurs = []
            measure_expressions = []
            measure_tempos = []
            measure_layouts = []
            measure_crescendos = []
            
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
            
            # Get all layout elements with positions (SystemLayout support)
            for layout in measure.getElementsByClass([music21.layout.SystemLayout, 
                                                    music21.layout.PageLayout,
                                                    music21.layout.StaffLayout]):
                measure_layouts.append((layout.offset, layout))
            
            # Get all crescendo/diminuendo elements with positions
            # NOTE: music21's MusicXML parser currently doesn't preserve wedge crescendos properly.
            # See: https://github.com/cuthbertLab/music21/pull/1768 for a fix that should address this.
            # Text crescendo markings (like "cresc.") are preserved as TextExpression objects.
            for cresc in measure.getElementsByClass([music21.dynamics.Crescendo,
                                                   music21.dynamics.Diminuendo,
                                                   music21.dynamics.DynamicWedge]):
                measure_crescendos.append((cresc.offset, cresc))
            
            # Create a set to track measure-level elements we've already processed (to prevent duplication)
            processed_measure_elements = set()
            
            # Add measure-level elements to the appropriate target measure (only once per measure)
            # For part 1, add to soprano measure; for part 2, add to tenor measure
            if part_idx == 0:  # Part 1 (treble clef)
                target_for_measure_elements = soprano_measure
            elif part_idx == 1:  # Part 2 (bass clef)
                target_for_measure_elements = tenor_measure
            else:
                target_for_measure_elements = soprano_measure  # Default fallback
            
            # Add measure-level elements (with copies), but only if this is the first part to avoid duplication
            # Only add measure-level elements from part 1 to prevent duplication between parts
            if part_idx == 0:
                for offset, dynamic in measure_dynamics:
                    dynamic_copy = copy.deepcopy(dynamic)
                    target_for_measure_elements.insert(offset, dynamic_copy)
                    processed_measure_elements.add(id(dynamic))
                for offset, slur in measure_slurs:
                    slur_copy = copy.deepcopy(slur)
                    target_for_measure_elements.insert(offset, slur_copy)
                    processed_measure_elements.add(id(slur))
                for offset, expression in measure_expressions:
                    expr_copy = copy.deepcopy(expression)
                    target_for_measure_elements.insert(offset, expr_copy)
                    processed_measure_elements.add(id(expression))
                for offset, tempo in measure_tempos:
                    tempo_copy = copy.deepcopy(tempo)
                    target_for_measure_elements.insert(offset, tempo_copy)
                    processed_measure_elements.add(id(tempo))
                # Add layout elements to preserve system breaks and formatting
                for offset, layout in measure_layouts:
                    layout_copy = copy.deepcopy(layout)
                    target_for_measure_elements.insert(offset, layout_copy)
                    processed_measure_elements.add(id(layout))
                    print(f"    Added {type(layout).__name__} to measure {measure_idx + 1}")
                # Add crescendo/diminuendo elements to preserve dynamic markings
                for offset, cresc in measure_crescendos:
                    cresc_copy = copy.deepcopy(cresc)
                    target_for_measure_elements.insert(offset, cresc_copy)
                    processed_measure_elements.add(id(cresc))
                    print(f"    Added {type(cresc).__name__} to measure {measure_idx + 1}")
            
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
                    
                    # Extract dynamics and other musical elements from voice level ONLY
                    # (measure-level elements are handled separately to prevent duplication)
                    voice_dynamics = []
                    voice_slurs = []
                    voice_expressions = []
                    voice_tempos = []
                    voice_crescendos = []
                    
                    for dynamic in voice.getElementsByClass(music21.dynamics.Dynamic):
                        voice_dynamics.append((dynamic.offset, dynamic))
                    for slur in voice.getElementsByClass(music21.spanner.Slur):
                        voice_slurs.append((slur.offset, slur))
                    for expr in voice.getElementsByClass(music21.expressions.TextExpression):
                        voice_expressions.append((expr.offset, expr))
                    for tempo in voice.getElementsByClass(music21.tempo.TempoIndication):
                        voice_tempos.append((tempo.offset, tempo))
                    # Extract crescendo/diminuendo elements from voice level
                    for cresc in voice.getElementsByClass([music21.dynamics.Crescendo,
                                                          music21.dynamics.Diminuendo,
                                                          music21.dynamics.DynamicWedge]):
                        voice_crescendos.append((cresc.offset, cresc))
                    
                    print(f"{len(notes)} notes, {len(rests)} rests, {len(voice_dynamics)} voice dynamics, {len(voice_slurs)} voice slurs, {len(voice_expressions)} voice expressions, {len(voice_tempos)} voice tempos, {len(voice_crescendos)} voice crescendos -> {voice_name}")
                    
                    # Add notes and rests to target measure (with copies to avoid object reuse)
                    for note in notes:
                        target_measure.append(copy.deepcopy(note))
                    for rest in rests:
                        target_measure.append(copy.deepcopy(rest))
                    
                    # Add ONLY voice-level dynamics, slurs, expressions, tempos, and crescendos (with copies)
                    for offset, dynamic in voice_dynamics:
                        dynamic_copy = copy.deepcopy(dynamic)
                        target_measure.insert(offset, dynamic_copy)
                    for offset, slur in voice_slurs:
                        slur_copy = copy.deepcopy(slur)
                        target_measure.insert(offset, slur_copy)
                    for offset, expression in voice_expressions:
                        expr_copy = copy.deepcopy(expression)
                        target_measure.insert(offset, expr_copy)
                    for offset, tempo in voice_tempos:
                        tempo_copy = copy.deepcopy(tempo)
                        target_measure.insert(offset, tempo_copy)
                    # Add voice-level crescendo/diminuendo elements
                    for offset, cresc in voice_crescendos:
                        cresc_copy = copy.deepcopy(cresc)
                        target_measure.insert(offset, cresc_copy)
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
    
    # Add parts to their respective scores
    soprano_score.append(soprano_part)
    alto_score.append(alto_part)
    tenor_score.append(tenor_part)
    bass_score.append(bass_part)
    
    # Create result dictionary with scores
    result = {
        'Soprano': soprano_score,
        'Alto': alto_score,
        'Tenor': tenor_score,
        'Bass': bass_score
    }
    
    print(f"\n=== Voice Splitting Complete ===")
    for voice_name, voice_score in result.items():
        part = voice_score.parts[0]
        measures = list(part.getElementsByClass(music21.stream.Measure))
        total_notes = sum(len(list(measure.getElementsByClass(music21.note.Note))) for measure in measures)
        total_dynamics = sum(len(list(measure.getElementsByClass(music21.dynamics.Dynamic))) for measure in measures)
        total_layouts = sum(len(list(measure.getElementsByClass(music21.layout.LayoutBase))) for measure in measures)
        # Count crescendos/diminuendos at both part level and measure level
        part_crescendos = len(list(part.getElementsByClass([music21.dynamics.Crescendo,
                                                          music21.dynamics.Diminuendo,
                                                          music21.dynamics.DynamicWedge])))
        measure_crescendos = sum(len(list(measure.getElementsByClass([music21.dynamics.Crescendo,
                                                                    music21.dynamics.Diminuendo,
                                                                    music21.dynamics.DynamicWedge]))) for measure in measures)
        total_crescendos = part_crescendos + measure_crescendos
        print(f"{voice_name}: {len(measures)} measures, {total_notes} total notes, {total_dynamics} dynamics, {total_layouts} layout elements, {total_crescendos} crescendos/diminuendos ({part_crescendos} part-level + {measure_crescendos} measure-level)")
    
    # Apply unification rules - need to extract parts for the unification function
    print(f"\n=== Applying Unification Rules ===")
    parts_dict = {name: voice_score.parts[0] for name, voice_score in result.items()}
    apply_unification(parts_dict)
    
    return result
