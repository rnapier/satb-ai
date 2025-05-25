# Testing Plan: Copy-and-Remove SATB Split Architecture

## Overview

This document outlines the comprehensive testing strategy for validating the new copy-and-remove architecture against the current extract-and-build system.

## Testing Objectives

### Primary Goals
1. **Musical Correctness**: Ensure output is musically equivalent or superior
2. **Data Preservation**: Verify no musical elements are lost
3. **Performance**: Validate acceptable performance characteristics
4. **Reliability**: Ensure robust error handling and edge case support

### Success Criteria
- All test files produce musically correct output
- No regression in musical quality compared to current system
- Improved element preservation (fewer missing dynamics, lyrics, etc.)
- Acceptable performance (memory usage may increase due to copying, but should be reasonable)

## Test Categories

### 1. Unit Tests

#### VoiceIdentifier Tests
```python
class TestVoiceIdentifier:
    def test_standard_satb_detection(self):
        """Test detection of standard closed-score SATB arrangement."""
        
    def test_open_score_detection(self):
        """Test detection of open-score SATB arrangement."""
        
    def test_non_standard_voice_ids(self):
        """Test handling of non-standard voice ID schemes."""
        
    def test_confidence_scoring(self):
        """Test confidence scoring for voice detection."""
        
    def test_edge_cases(self):
        """Test edge cases: missing voices, extra voices, etc."""
```

#### VoiceRemover Tests
```python
class TestVoiceRemover:
    def test_surgical_voice_removal(self):
        """Test that only target voices are removed."""
        
    def test_element_preservation(self):
        """Test that non-voice elements are preserved."""
        
    def test_timing_preservation(self):
        """Test that timing relationships are maintained."""
        
    def test_empty_measure_handling(self):
        """Test handling of measures that become empty."""
        
    def test_cross_voice_elements(self):
        """Test handling of elements that span multiple voices."""
```

#### StaffSimplifier Tests
```python
class TestStaffSimplifier:
    def test_two_staff_to_one_conversion(self):
        """Test conversion from two-staff to single-staff layout."""
        
    def test_clef_assignment(self):
        """Test appropriate clef assignment for each voice type."""
        
    def test_metadata_preservation(self):
        """Test preservation of part names and metadata."""
        
    def test_layout_element_handling(self):
        """Test handling of layout elements during simplification."""
```

#### ContextualUnifier Tests
```python
class TestContextualUnifier:
    def test_dynamics_unification(self):
        """Test dynamics unification rules."""
        
    def test_lyrics_unification(self):
        """Test lyrics distribution and unification."""
        
    def test_spanner_unification(self):
        """Test spanner unification with full context."""
        
    def test_cross_reference_analysis(self):
        """Test cross-reference analysis between voice scores."""
```

### 2. Integration Tests

#### End-to-End Processing
```python
class TestIntegration:
    def test_complete_pipeline(self):
        """Test complete processing pipeline from input to output."""
        
    def test_file_format_support(self):
        """Test support for .mscz and .musicxml input formats."""
        
    def test_output_file_generation(self):
        """Test generation of output MusicXML files."""
        
    def test_cli_integration(self):
        """Test CLI interface integration."""
```

#### Comparison with Current System
```python
class TestSystemComparison:
    def test_output_equivalence(self):
        """Compare output with current system for equivalence."""
        
    def test_musical_content_preservation(self):
        """Verify musical content is preserved or improved."""
        
    def test_element_count_comparison(self):
        """Compare element counts between systems."""
        
    def test_timing_accuracy_comparison(self):
        """Compare timing accuracy between systems."""
```

### 3. Validation Tests

#### Musical Correctness
```python
class TestMusicalCorrectness:
    def test_note_preservation(self):
        """Verify all notes are preserved with correct timing."""
        
    def test_rhythm_preservation(self):
        """Verify rhythmic relationships are maintained."""
        
    def test_harmonic_content(self):
        """Verify harmonic content is preserved across voices."""
        
    def test_lyric_alignment(self):
        """Verify lyrics are correctly aligned with notes."""
```

#### Data Integrity
```python
class TestDataIntegrity:
    def test_no_data_loss(self):
        """Verify no musical data is lost during processing."""
        
    def test_metadata_preservation(self):
        """Verify score metadata is preserved."""
        
    def test_layout_preservation(self):
        """Verify appropriate layout elements are preserved."""
        
    def test_spanner_integrity(self):
        """Verify spanners are correctly preserved and assigned."""
```

### 4. Performance Tests

#### Memory Usage
```python
class TestPerformance:
    def test_memory_usage_reasonable(self):
        """Test that memory usage is reasonable for typical files."""
        
    def test_large_file_handling(self):
        """Test handling of large SATB files."""
        
    def test_memory_cleanup(self):
        """Test that memory is properly cleaned up after processing."""
```

#### Processing Time
```python
class TestProcessingTime:
    def test_processing_speed(self):
        """Test processing speed compared to current system."""
        
    def test_scalability(self):
        """Test performance scaling with file size."""
```

### 5. Edge Case Tests

#### Unusual Score Structures
```python
class TestEdgeCases:
    def test_non_standard_arrangements(self):
        """Test non-standard SATB arrangements."""
        
    def test_incomplete_voices(self):
        """Test handling of incomplete or missing voices."""
        
    def test_complex_rhythms(self):
        """Test handling of complex rhythmic patterns."""
        
    def test_extended_techniques(self):
        """Test handling of extended musical techniques."""
```

#### Error Conditions
```python
class TestErrorHandling:
    def test_invalid_input_files(self):
        """Test handling of invalid or corrupted input files."""
        
    def test_unsupported_formats(self):
        """Test handling of unsupported file formats."""
        
    def test_processing_failures(self):
        """Test graceful handling of processing failures."""
        
    def test_recovery_mechanisms(self):
        """Test error recovery and rollback mechanisms."""
```

## Test Data

### Primary Test Files
1. **"Crossing The Bar.mscz"** - Primary test file (existing)
2. **"Crossing The Bar.musicxml"** - MusicXML version (existing)

### Additional Test Files Needed
3. **Simple SATB** - Basic four-part harmony for baseline testing
4. **Complex SATB** - Advanced harmonies, multiple verses, complex rhythms
5. **Open Score SATB** - Four separate staves instead of closed score
6. **Incomplete SATB** - Missing voices or partial arrangements
7. **Extended SATB** - With additional parts or instruments

### Synthetic Test Cases
```python
def create_test_scores():
    """Create synthetic test scores for specific test scenarios."""
    
    # Test case 1: Dynamics only in Soprano
    score1 = create_score_with_soprano_dynamics()
    
    # Test case 2: Different lyrics in different voices
    score2 = create_score_with_voice_specific_lyrics()
    
    # Test case 3: Complex spanner arrangements
    score3 = create_score_with_complex_spanners()
    
    # Test case 4: Cross-staff elements
    score4 = create_score_with_cross_staff_elements()
    
    return [score1, score2, score3, score4]
```

## Test Execution Strategy

### Automated Testing
```python
# Continuous testing during development
def run_unit_tests():
    """Run all unit tests."""
    
def run_integration_tests():
    """Run integration tests with real files."""
    
def run_comparison_tests():
    """Run comparison tests against current system."""
    
def run_performance_tests():
    """Run performance benchmarks."""
```

### Manual Testing
1. **Visual Inspection**: Open output files in MuseScore for visual verification
2. **Audio Comparison**: Generate audio from both systems and compare
3. **Musical Analysis**: Verify musical content is correct and complete

### Regression Testing
```python
def test_regression_suite():
    """Run complete regression test suite."""
    
    # Test all existing functionality
    test_files = get_all_test_files()
    
    for test_file in test_files:
        # Process with current system (reference)
        reference_output = process_with_current_system(test_file)
        
        # Process with new system
        new_output = process_with_new_system(test_file)
        
        # Validate equivalence or improvement
        validate_output_quality(reference_output, new_output, test_file)
```

## Success Metrics

### Quantitative Metrics
- **Test Coverage**: >95% code coverage
- **Pass Rate**: 100% of tests pass
- **Performance**: Processing time within 2x of current system
- **Memory**: Memory usage within reasonable bounds (4x max due to copying)

### Qualitative Metrics
- **Musical Quality**: No loss of musical information
- **Code Quality**: Improved maintainability and readability
- **Error Handling**: Robust error handling and recovery
- **User Experience**: Same or better CLI experience

## Test Environment Setup

### Dependencies
```python
# Testing dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
music21>=8.0.0
memory-profiler>=0.60.0
```

### Test Configuration
```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=satb_splitter --cov-report=html --cov-report=term
```

### Continuous Integration
```yaml
# GitHub Actions workflow for testing
name: Test SATB Splitter
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync
      - name: Run tests
        run: uv run pytest
```

This comprehensive testing plan ensures the new architecture meets all quality and functionality requirements while providing confidence in the migration from the current system.