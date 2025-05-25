# Lyric Assignment Feature

## Overview

The lyric assignment feature automatically assigns lyrics to voices that have notes of the same duration at the same offset in the same measure, but don't already have lyrics. This ensures that all SATB voices receive appropriate text when they are singing together.

## Feature Requirements

The feature implements the following logic:

1. **Same timing and duration**: Only notes that occur at exactly the same musical position (offset) and have the same duration receive shared lyrics.

2. **Respect existing lyrics**: If a voice already has its own lyrics for a note, those lyrics are preserved and not overwritten.

3. **Measure-by-measure analysis**: The feature analyzes each measure independently to find lyric assignment opportunities.

## Implementation Details

### Core Algorithm

The lyric assignment is implemented in [`satb_splitter/contextual_unifier.py`](satb_splitter/contextual_unifier.py) with the following key methods:

#### `unify_lyrics()`
- Main entry point for lyric unification
- Finds lyric gaps and fills them across all voices
- Returns statistics about unified elements

#### `_find_lyric_gaps()`
- Analyzes each measure across all voices
- Identifies notes with lyrics in one voice and matching notes without lyrics in other voices
- Returns a list of gap information for processing

#### `_fill_lyric_gap()`
- Copies lyrics from source voice to target voice
- Preserves lyric properties like syllabic information and numbering
- Uses `music21.Note.addLyric()` for proper lyric attachment

#### `_find_matching_notes_without_lyrics()`
- Finds notes in other voices at the same musical position
- Checks timing (offset) and duration matching with small tolerance (0.01 quarter notes)
- Excludes notes that already have lyrics

## Examples from "Crossing The Bar"

### Measure 1, Beat 1
- **Soprano** (staff 1, voice 1): Quarter note with lyric "Sun"  
- **Alto** (staff 1, voice 2): Quarter note, no lyric → Gets "Sun"
- **Tenor** (staff 2, voice 1): Quarter note, no lyric → Gets "Sun"  
- **Bass** (staff 2, voice 2): Quarter note, no lyric → Gets "Sun"

### Measures with Existing Lyrics
- **Measures 16-18**: Bass has its own lyrics → Preserved, not overwritten
- **Measure 14**: Soprano has its own lyrics → Preserved, not overwritten

## Configuration

The feature is controlled by the `apply_lyrics_unification` option in [`ProcessingOptions`](satb_splitter/utils.py):

```python
options = ProcessingOptions(
    apply_lyrics_unification=True,  # Enable lyric assignment
    # ... other options
)
```

## Testing

The feature includes comprehensive tests:

### Basic Test ([`test_lyric_assignment.py`](test_lyric_assignment.py))
- Verifies basic lyric assignment functionality
- Tests measure 1 specifically
- Validates correct lyric content assignment

### Comprehensive Test ([`test_comprehensive_lyrics.py`](test_comprehensive_lyrics.py))
- Tests specific examples from the task requirements
- Verifies existing lyrics preservation
- Analyzes multiple measures
- Tests timing and duration matching

## Usage Example

```python
from satb_splitter.score_processor import ScoreProcessor
from satb_splitter.utils import ProcessingOptions

# Configure processing options
options = ProcessingOptions(
    auto_detect_voices=True,
    apply_lyrics_unification=True
)

# Process the score
processor = ScoreProcessor(options)
result = processor.process_satb_score("input_score.musicxml")

# Access individual voice scores with assigned lyrics
soprano_score = result.voice_scores['Soprano']
alto_score = result.voice_scores['Alto']
tenor_score = result.voice_scores['Tenor']
bass_score = result.voice_scores['Bass']
```

## Technical Notes

### Music21 Integration
- Uses `music21.Note.addLyric(text, number)` for proper lyric creation
- Preserves syllabic information (begin, middle, end, single)
- Maintains lyric numbering for multiple lyric lines

### Timing Tolerance
- Uses 0.01 quarter note tolerance for offset matching to handle floating-point precision
- Duration matching also uses 0.01 quarter note tolerance

### Performance Considerations
- Processes each measure independently for memory efficiency
- Only analyzes notes that have lyrics as potential sources
- Skips notes that already have lyrics as targets

## Validation

The feature has been validated with:
- ✅ "Crossing The Bar" by Joseph Barnby/Alfred Tennyson
- ✅ Measure 1 specific case (all voices get "Sun")
- ✅ Preservation of existing lyrics
- ✅ Timing and duration matching accuracy
- ✅ Multiple measure analysis

## Future Enhancements

Potential improvements for future versions:
1. **Smart lyric detection**: Detect when lyrics should be shared based on musical context
2. **Multi-language support**: Handle different language syllabic patterns
3. **Lyric line management**: Handle multiple lyric lines more intelligently
4. **User override options**: Allow manual control over specific lyric assignments