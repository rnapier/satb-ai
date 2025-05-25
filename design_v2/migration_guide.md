# Migration Guide: From Extract-and-Build to Copy-and-Remove

## Overview

This guide outlines the migration from the current extract-and-build approach to the new copy-and-remove architecture. The migration will be a direct replacement using version control for safety.

## Migration Strategy

### Direct Replacement with Version Control Safety
1. Move current implementation to `satb_splitter_old/` for reference during development
2. Implement new system directly in `satb_splitter/`
3. Test thoroughly with existing test files
4. Remove old reference code once satisfied

## Implementation Plan

### Phase 1: Preserve Current Implementation
```bash
# Move current implementation for reference
mv satb_splitter/ satb_splitter_old/
mkdir satb_splitter/
```

### Phase 2: New Implementation Structure
```
satb_splitter/
├── __init__.py
├── main.py                  # Entry point
├── voice_identifier.py      # Voice detection logic
├── voice_remover.py         # Voice removal engine
├── staff_simplifier.py      # Staff layout conversion
├── contextual_unifier.py    # Simplified unification
├── score_processor.py       # Main orchestration
├── utils.py                 # Common utilities
└── converter.py             # Reuse existing file conversion
```

### Phase 3: Clean API Design
```python
# Main API - clean naming, no version suffixes
def split_satb_voices(input_file: str, 
                     output_dir: Optional[str] = None,
                     options: Optional[ProcessingOptions] = None) -> Dict[str, music21.stream.Score]:
    """Split SATB score into individual voice parts using copy-and-remove approach."""
```

## Key Changes from Current System

### Simplified Architecture
- **Current**: Extract elements → Build new scores → Apply unification
- **New**: Copy complete scores → Remove unwanted voices → Simplify layout → Apply unification

### Eliminated Complexity
- Remove complex voice mapping logic: `(0, '1'): soprano_measure`
- Remove manual element enumeration and copying
- Remove complex spanner extraction and reconstruction
- Remove timing validation and correction code

### Preserved Functionality
- Same CLI interface: `satb-split input.mscz`
- Same output format: Individual voice MusicXML files
- Same unification behavior (but simplified implementation)

## Testing Strategy

### Validation Against Current System
```python
def validate_against_reference():
    """Test new implementation against current system output."""
    test_files = ["Crossing The Bar.mscz", "Crossing The Bar.musicxml"]
    
    for test_file in test_files:
        # Process with reference implementation
        reference_result = process_with_reference(test_file)
        
        # Process with new implementation
        new_result = split_satb_voices(test_file)
        
        # Validate equivalent or improved output
        assert_musical_equivalence(reference_result, new_result)
        assert_no_data_loss(new_result)
        assert_improved_element_preservation(new_result, reference_result)

def process_with_reference(test_file):
    """Process file using old implementation for comparison."""
    # Import from reference directory
    sys.path.insert(0, 'satb_splitter_old')
    from voice_splitter import split_satb_voices as old_split
    return old_split(test_file)
```

### Quality Validation
1. **Element Preservation**: Verify all musical elements are preserved
2. **Timing Integrity**: Ensure no timing corruption
3. **Unification Correctness**: Validate unification rules work correctly
4. **Output Quality**: Compare output files for musical accuracy

## Expected Improvements

### Code Quality
- **Reduced Complexity**: Eliminate ~200 lines of complex voice mapping
- **Better Separation**: Clear module boundaries and responsibilities
- **Easier Debugging**: Simpler data flow and error handling

### Musical Quality
- **No Data Loss**: Complete score copying preserves all elements
- **Better Timing**: Original timing relationships maintained
- **Cleaner Output**: Less risk of corruption during processing

### Maintainability
- **Clearer Logic**: Copy-and-remove is conceptually simpler
- **Fewer Edge Cases**: Less special case handling needed
- **Easier Extension**: Modular design supports future enhancements

## Implementation Steps

### Step 1: Setup
```bash
# Preserve current implementation
git add -A && git commit -m "Checkpoint before architecture change"
mv satb_splitter/ satb_splitter_old/
mkdir satb_splitter/
```

### Step 2: Core Implementation
Implement new modules in clean `satb_splitter/` directory:
1. `score_processor.py` - Main orchestration
2. `voice_identifier.py` - Voice detection
3. `voice_remover.py` - Voice removal
4. `staff_simplifier.py` - Layout conversion
5. `contextual_unifier.py` - Unification rules

### Step 3: Integration
- Update `main.py` to use new architecture
- Ensure CLI compatibility
- Test with existing files

### Step 4: Validation
- Compare output with reference implementation
- Validate musical correctness
- Performance testing

### Step 5: Cleanup
```bash
# Once satisfied with new implementation
rm -rf satb_splitter_old/
git add -A && git commit -m "Replace extract-and-build with copy-and-remove architecture"
```

## File Reuse Strategy

### Reusable Components
- `converter.py` - File conversion logic can be reused as-is
- Test files - Existing test files for validation
- CLI structure - Basic CLI interface structure

### Components to Replace
- `voice_splitter.py` - Replace with `score_processor.py` + modules
- `unification.py` - Replace with `contextual_unifier.py`
- `spanner_extractor.py` - Eliminate (no longer needed)
- `spanner_builder.py` - Eliminate (no longer needed)
- `timing_validator.py` - Eliminate (no longer needed)

This approach provides a clean transition while maintaining the safety net of version control and reference implementation during development.