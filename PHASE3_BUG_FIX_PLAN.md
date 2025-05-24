# Phase 3 Bug Fix Plan - SATB Split Project

## Overview
This document outlines the plan to address critical bugs identified in the SATB voice separation functionality following Phase 3 implementation. All fixes will use the music21 library exclusively, removing any experimental ms3 code.

## Current Bug Summary

### 1. **No dynamics are included**
- **Status**: ✅ COMPLETED
- **Description**: Dynamic markings (forte, piano, crescendo, etc.) are not being extracted from the source score or included in the separated voice parts
- **Impact**: Musical expression is lost in the output files
- **Resolution**: Implemented dynamics extraction and Phase 3 unification rules

### 2. **Lyrics and dynamics are not unified as described in Phase 3**
- **Status**: ✅ COMPLETED
- **Description**: The Phase 3 unification rules for dynamics and lyrics are not being applied
- **Impact**: Missing shared musical elements that should be applied across all voices
- **Resolution**: Implemented comprehensive Phase 3 unification logic for both dynamics and lyrics

### 3. **Two collections of measures running from 1-36 rather than a single collection**
- **Status**: ✅ COMPLETED
- **Description**: High voices (S/A) and low voices (T/B) are creating separate measure numbering sequences instead of unified measures 1-36
- **Impact**: Measure synchronization issues and incorrect score structure
- **Resolution**: Fixed unified measure numbering system ensuring all parts have consistent measure numbers 1-36

### 4. **Slurs are missing from all parts**
- **Status**: ✅ COMPLETED
- **Description**: Slur markings and other articulations are not being transferred to the separated voice parts
- **Impact**: Phrasing and articulation information is lost
- **Resolution**: Added slur and articulation extraction and transfer to all voice parts

### 5. **Low voices should be written in bass clef**
- **Status**: ✅ COMPLETED
- **Description**: All parts are using treble clef; Tenor and Bass should use bass clef
- **Impact**: Readability issues for low voice parts
- **Resolution**: Implemented proper clef assignment (treble for Soprano/Alto, bass for Tenor/Bass)

## Root Cause Analysis

### Current Implementation Issues
1. **Limited Element Extraction**: The current `split_satb_voices()` function only extracts notes and rests, ignoring dynamics, lyrics, and slurs
2. **Missing Phase 3 Logic**: Unification rules exist in experimental ms3 code but are not integrated into the main music21 workflow
3. **Measure Creation Logic**: The voice mapping creates separate measure collections instead of synchronized measures
4. **No Clef Management**: Default treble clef is applied to all parts
5. **Incomplete Music21 API Usage**: Not leveraging music21's full capabilities for musical element extraction

## Implementation Plan

### Step 1: Code Cleanup and Architecture
**Priority**: Immediate
**Estimated Time**: 30 minutes

#### 1.1 Remove MS3 Dependencies
- [x] Delete `satb_splitter/exploder.py`
- [x] Remove any ms3 imports from requirements
- [x] Clean up any ms3-related code references

#### 1.2 Focus on Music21 Implementation
- [x] Enhance existing `main.py` implementation
- [x] Ensure all functionality uses music21 exclusively

### Step 2: Fix Measure Alignment System
**Priority**: Critical
**Estimated Time**: 1-2 hours

#### 2.1 Current Problem
```python
# Current problematic approach creates separate collections
for part_idx, original_part in enumerate(score.parts):
    # This creates measures 1-36 for high voices, then 1-36 for low voices
```

#### 2.2 Solution Implementation
```python
# Proposed unified approach
def create_unified_measures(score, soprano_part, alto_part, tenor_part, bass_part):
    """Create synchronized measures 1-36 for all parts."""
    for measure_num in range(1, total_measures + 1):
        # Create corresponding measures for all parts with same number
        soprano_measure = music21.stream.Measure(number=measure_num)
        alto_measure = music21.stream.Measure(number=measure_num)
        tenor_measure = music21.stream.Measure(number=measure_num)
        bass_measure = music21.stream.Measure(number=measure_num)
        
        # Extract and distribute content to appropriate measures
        extract_measure_content(score, measure_num, soprano_measure, alto_measure, tenor_measure, bass_measure)
```

### Step 3: Enhanced Element Extraction
**Priority**: Critical
**Estimated Time**: 2-3 hours

#### 3.1 Dynamics Extraction
```python
def extract_dynamics(original_part, target_parts):
    """Extract dynamics using music21.dynamics.Dynamic objects."""
    dynamics = original_part.getElementsByClass(music21.dynamics.Dynamic)
    for dynamic in dynamics:
        # Capture position, type, and apply to appropriate voices
        position = dynamic.offset
        marking = dynamic.value  # e.g., 'f', 'p', 'mp'
        # Apply Phase 3 unification rules
```

#### 3.2 Lyrics Extraction
```python
def extract_lyrics(voice, target_part):
    """Extract lyrics from notes in voice."""
    for note in voice.getElementsByClass(music21.note.Note):
        if note.lyric:
            # Store lyric with position data
            lyric_data = {
                'text': note.lyric,
                'position': note.offset,
                'note': note
            }
```

#### 3.3 Slur Extraction
```python
def extract_slurs(original_part, target_part):
    """Extract and transfer slur spanners."""
    slurs = original_part.getElementsByClass(music21.spanner.Slur)
    for slur in slurs:
        # Map slur start/end to new voice context
        new_slur = music21.spanner.Slur(slur.getFirst(), slur.getLast())
        target_part.insert(new_slur)
```

### Step 4: Phase 3 Unification Rules Implementation
**Priority**: Critical
**Estimated Time**: 2-3 hours

#### 4.1 Dynamics Unification Logic
```python
def apply_dynamics_unification(soprano_dynamics, alto_dynamics, tenor_dynamics, bass_dynamics):
    """Apply Phase 3 dynamics unification rules."""
    
    # Rule 1: If only Soprano has dynamics → apply to all parts
    if soprano_dynamics and not (alto_dynamics or tenor_dynamics or bass_dynamics):
        return copy_dynamics_to_all_parts(soprano_dynamics)
    
    # Rule 2: If Soprano and Bass have matching dynamics → apply to all parts
    if dynamics_match(soprano_dynamics, bass_dynamics):
        return copy_dynamics_to_inner_parts(soprano_dynamics)
    
    # Rule 3: If Soprano and Tenor have matching dynamics → apply to all parts  
    if dynamics_match(soprano_dynamics, tenor_dynamics):
        return copy_dynamics_to_inner_parts(soprano_dynamics)
    
    # Otherwise, keep original distribution
    return preserve_original_dynamics()
```

#### 4.2 Lyrics Unification Logic
```python
def apply_lyrics_unification(voice_lyrics):
    """Apply Phase 3 lyrics unification rules."""
    soprano_count = len(voice_lyrics['soprano'])
    total_others = sum(len(voice_lyrics[v]) for v in ['alto', 'tenor', 'bass'])
    
    # If Soprano has significantly more lyrics, apply to parts with no lyrics
    if soprano_count > 0 and soprano_count >= total_others * 3:
        return copy_soprano_lyrics_to_empty_parts(voice_lyrics)
    
    return voice_lyrics  # Keep original distribution
```

### Step 5: Clef Assignment
**Priority**: Medium
**Estimated Time**: 30 minutes

#### 5.1 Implementation
```python
def assign_appropriate_clefs(soprano_part, alto_part, tenor_part, bass_part):
    """Set appropriate clefs for each SATB part."""
    soprano_part.insert(0, music21.clef.TrebleClef())
    alto_part.insert(0, music21.clef.TrebleClef())
    tenor_part.insert(0, music21.clef.BassClef())  # or TrebleClef8vb()
    bass_part.insert(0, music21.clef.BassClef())
```

### Step 6: Improved Voice Mapping
**Priority**: High
**Estimated Time**: 1 hour

#### 6.1 Robust Voice Detection
```python
def map_voices_to_satb(score):
    """Create robust mapping from source voices to SATB parts."""
    voice_mapping = {}
    
    for part_idx, part in enumerate(score.parts):
        voices = part.getElementsByClass(music21.stream.Voice)
        for voice_idx, voice in enumerate(voices):
            # Create flexible mapping based on part and voice position
            satb_voice = determine_satb_voice(part_idx, voice_idx, len(voices))
            voice_mapping[(part_idx, voice_idx)] = satb_voice
    
    return voice_mapping
```

## Testing Strategy

### Test Cases
1. **"Crossing The Bar.mscz"** - Primary test file
2. **Measure Verification**: Confirm all parts have measures 1-36
3. **Dynamics Verification**: Check Phase 3 unification rules apply correctly
4. **Lyrics Verification**: Ensure lyrics are distributed per Phase 3 rules
5. **Clef Verification**: Confirm Tenor/Bass use bass clef
6. **Slur Verification**: Ensure articulations are preserved

### Validation Checklist
- [x] All parts have synchronized measure numbering (1-36)
- [x] Dynamics are present and properly unified
- [x] Lyrics follow Phase 3 distribution rules
- [x] Slurs and articulations are preserved
- [x] Appropriate clefs are assigned
- [x] No duplicate or missing measures
- [x] Output files are valid MusicXML

## Implementation Order

### Phase 1 (Immediate - Day 1)
1. [x] Remove ms3 code and dependencies
2. [x] Fix measure alignment system
3. [x] Add clef assignments

### Phase 2 (Critical - Day 1-2) 
1. [x] Implement dynamics extraction and Phase 3 unification
2. [x] Add slur extraction and transfer
3. [x] Improve voice mapping robustness

### Phase 3 (Important - Day 2)
1. [x] Implement lyrics extraction and Phase 3 unification
2. [x] Comprehensive testing with "Crossing The Bar"
3. [x] Validation and bug fixes

## Risk Assessment

### High Risk
- **Measure synchronization complexity**: May require significant refactoring of existing logic
- **Phase 3 rule implementation**: Complex business logic for musical element unification

### Medium Risk  
- **Slur mapping**: Ensuring slur start/end points map correctly to single-voice context
- **Voice detection reliability**: Handling variations in how voices are structured in different files

### Low Risk
- **Clef assignment**: Straightforward music21 API usage
- **Code cleanup**: Well-defined removal tasks

## Success Criteria

1. **Functional**: All 5 identified bugs are resolved
2. **Quality**: Output files are musically accurate and properly formatted
3. **Maintainable**: Code uses music21 API consistently and clearly
4. **Testable**: Changes can be verified with the test score
5. **Documented**: Implementation includes clear comments and documentation

## Next Steps

1. **Approval**: Get stakeholder approval for this plan
2. **Implementation**: Execute phases in priority order  
3. **Testing**: Validate fixes with test files
4. **Documentation**: Update code comments and user documentation
5. **Delivery**: Provide completed, tested solution

---

## ✅ COMPLETION STATUS - ALL PHASE 3 BUGS RESOLVED

### Implementation Summary
**Completed**: 2025-05-24  
**Status**: ALL 5 CRITICAL BUGS FIXED

#### What Was Accomplished:
1. **✅ Dynamics Extraction**: Implemented comprehensive dynamics extraction and Phase 3 unification rules
2. **✅ Lyrics Unification**: Added Phase 3 lyrics distribution logic (Soprano lyrics copied to Tenor when appropriate)
3. **✅ Unified Measure Numbering**: Fixed measure synchronization - all parts now have consistent measures 1-36
4. **✅ Slur Transfer**: Added slur and articulation extraction and transfer to all voice parts
5. **✅ Proper Clef Assignment**: Treble clef for Soprano/Alto, bass clef for Tenor/Bass
6. **✅ .mscz File Support**: Added robust MuseScore file format support with automatic conversion
7. **✅ Output Naming Convention**: Updated to use format `{original_name}-{part}.musicxml` with titles `{original_name} ({part})`

#### Technical Achievements:
- **Complete music21 Integration**: Removed all experimental ms3 dependencies
- **Robust Voice Mapping**: Handles voice IDs 1,2,5,6 mapping to Soprano,Alto,Tenor,Bass respectively
- **Phase 3 Business Logic**: Implemented all unification rules for dynamics and lyrics
- **Temporary File Management**: Safe .mscz conversion with automatic cleanup
- **Error Handling**: Comprehensive error handling and fallback mechanisms

#### Test Results:
- **Primary Test File**: "Crossing The Bar.mscz" processes successfully
- **Voice Separation**: Correctly extracts 4 SATB parts with proper content distribution
- **Musical Elements**: Dynamics, lyrics, slurs, and articulations properly transferred
- **Output Quality**: Valid MusicXML files with appropriate clefs and unified measure numbering

#### Final Output Format:
- **Filenames**: `Crossing The Bar-Soprano.musicxml`, `Crossing The Bar-Alto.musicxml`, etc.
- **Titles**: "Crossing The Bar (Soprano)", "Crossing The Bar (Alto)", etc.
- **Structure**: 36 measures per part with synchronized numbering
- **Clefs**: Treble for S/A, Bass for T/B
- **Content**: Complete musical content including dynamics, lyrics, slurs, and articulations

### Project Status: ✅ COMPLETE
All Phase 3 bugs have been successfully resolved. The satb-split tool now provides comprehensive SATB voice separation with full musical content preservation and proper Phase 3 unification rules.

---

*Document Version: 2.0 - COMPLETION UPDATE*  
*Created: 2025-05-24*  
*Completed: 2025-05-24*
