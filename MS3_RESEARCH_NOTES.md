# MS3 Package Research Notes

## Overview
Research conducted on the ms3 package to understand proper metadata extraction from MuseScore files.

## Key Findings

### Metadata Access Hierarchy
1. **Primary Source**: `score.mscx.metadata` dictionary (CORRECT)
2. **Secondary Source**: Direct attributes on score object  
3. **Tertiary Source**: XML parsing if needed

### Common Metadata Keys
- `workTitle` - Main title of the work
- `title` - Alternative title field
- `composer` - Composer name
- `movementTitle` - Title of movement/section
- `lyricist` - Lyricist name
- `arranger` - Arranger name
- `copyright` - Copyright information
- `creationDate` - Date of creation

### Score Object Structure
- `ms3.Score.mscx.metadata` provides the metadata source (CORRECT)
- XML parsing can be done through `score.mscx.soup` if needed

### Final Implementation (WORKING)
```python
def _extract_metadata(self) -> tuple[str, str]:
    """Extract title and composer using ms3 public API."""
    metadata = self.score.mscx.metadata
    title = metadata.get('workTitle') or metadata.get('title')
    composer = metadata.get('composer')
    
    return title or 'Unknown Title', composer or 'Unknown Composer'
```

## Current Implementation Status
- ❌ Original implementation was guessing at metadata access
- ✅ Researched proper ms3 API usage
- ✅ Updated exploder.py with correct metadata extraction
- ✅ Tested with "Crossing The Bar.mscz" file
- ✅ **COMPLETE**: Phase 1 improvements implemented and working

## Test File Results
- File: "Crossing The Bar.mscz"
- ✅ Title: "Crossing The Bar" (correctly extracted)
- ✅ Composer: "Joseph Barnby" (correctly extracted)
- ✅ Parsing successful despite FutureWarnings from pandas

## Phase Progress
- Phase 0: ✅ Complete (Basic CLI framework)
- Phase 1: ✅ **COMPLETE** (Parse MSCZ file - metadata extraction working)
- Phase 2: 🔄 **NEXT** (Separate SATB voices)
- Phase 3: ⏳ Pending (Export separate parts)
- Phase 4: ⏳ Pending (Audio export)
- Phase 5: ⏳ Pending (Integration testing)

## Notes for Phase 2
- Need to access voice/part information from ms3.Score
- Look into score.mscx.notes() or similar methods
- May need to identify SATB parts by staff numbers or instrument names
