# SATB Splitter Test Suite

This directory contains comprehensive pytest-based tests for the SATB splitter project.

## Test Structure

### Core Test Files

- **`test_basic_functionality.py`** - Basic functionality and integration tests
  - Voice splitting with default settings
  - File output validation
  - Note conservation checks
  - Voice identification and pitch range validation
  - ScoreProcessor functionality

- **`test_lyric_assignment.py`** - Lyric assignment feature tests
  - Basic lyric assignment functionality
  - Lyric content consistency across voices
  - Existing lyrics preservation
  - Timing and duration matching
  - Comprehensive lyric assignment scenarios

- **`test_dynamics_fix.py`** - Dynamics duplication fix tests
  - Dynamics duplication prevention (specifically measure 29 issue)
  - Dynamics preservation across voices
  - Dynamics consistency validation
  - Regression tests for the dynamics fix

- **`test_voice_separation.py`** - Voice separation validation tests
  - Detailed voice separation analysis
  - Note conservation during separation
  - Pitch range validation
  - Voice isolation verification
  - Measure consistency checks

- **`test_edge_cases.py`** - Edge cases and error handling tests
  - File handling edge cases (nonexistent, invalid, empty files)
  - Malformed score handling
  - Parameter validation
  - Memory and performance edge cases
  - Utility function edge cases

- **`test_performance.py`** - Performance and stress tests
  - Processing time validation
  - Memory usage stability
  - Concurrent processing safety
  - Resource management tests
  - Scalability characteristics

### Support Files

- **`conftest.py`** - Pytest configuration and shared fixtures
  - Test data fixtures
  - Helper functions for common test operations
  - Temporary directory management
  - Score processing utilities

- **`pytest.ini`** - Pytest configuration
  - Test discovery settings
  - Marker definitions
  - Warning filters

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_basic_functionality.py

# Run specific test class
pytest tests/test_basic_functionality.py::TestBasicFunctionality

# Run specific test method
pytest tests/test_basic_functionality.py::TestBasicFunctionality::test_split_satb_voices_success
```

### Test Categories

Tests are marked with categories for selective execution:

```bash
# Run only fast tests (exclude slow performance tests)
pytest -m "not slow"

# Run only integration tests
pytest -m integration

# Run only unit tests
pytest -m unit

# Run regression tests
pytest -m regression
```

### Coverage Reports

```bash
# Run with coverage (requires pytest-cov)
pytest --cov=satb_splitter --cov-report=html

# Coverage with missing lines
pytest --cov=satb_splitter --cov-report=term-missing
```

## Test Requirements

### Test Data

Tests require the following test data file:
- `Crossing The Bar.musicxml` - Sample SATB score for testing

This file should be present in the project root directory.

### Dependencies

Core testing dependencies (defined in `pyproject.toml`):
- `pytest` - Testing framework

Optional testing dependencies:
- `pytest-cov` - Coverage reporting
- `pytest-xdist` - Parallel test execution
- `pytest-mock` - Mocking utilities

## Test Design Principles

### Fixtures and Reusability

- Common test data and utilities are provided through fixtures in `conftest.py`
- Test fixtures handle temporary directory creation and cleanup
- Helper functions provide consistent ways to analyze musical scores

### Comprehensive Coverage

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test complete workflows from input to output
- **Edge Case Tests**: Test error handling and boundary conditions
- **Performance Tests**: Test resource usage and scalability
- **Regression Tests**: Prevent regression of known issues

### Test Isolation

- Each test is independent and can run in isolation
- Temporary directories are used for file operations
- No tests depend on external state or modify global state

### Realistic Testing

- Tests use real MusicXML files representative of typical use cases
- Tests validate both in-memory results and file outputs
- Tests check musical semantics, not just data structure validity

## Writing New Tests

### Test Organization

1. **Choose the appropriate test file** based on functionality being tested
2. **Use existing fixtures** from `conftest.py` when possible
3. **Follow naming conventions**: `test_*` for functions, `Test*` for classes
4. **Add appropriate markers** for test categorization

### Example Test Structure

```python
class TestNewFeature:
    """Test new feature functionality."""

    def test_basic_functionality(self, sample_musicxml_file, expected_voices):
        """Test basic operation of new feature."""
        # Arrange
        # Act
        result = new_feature(sample_musicxml_file)
        
        # Assert
        assert result is not None
        # Additional assertions...

    def test_edge_case(self, temp_output_dir):
        """Test edge case handling."""
        # Test edge case scenarios...

    @pytest.mark.slow
    def test_performance(self, sample_musicxml_file):
        """Test performance characteristics."""
        # Performance testing...
```

### Best Practices

1. **Clear test names** that describe what is being tested
2. **Arrange-Act-Assert** structure for test organization
3. **Meaningful assertions** with descriptive failure messages
4. **Test both success and failure paths**
5. **Use fixtures** to reduce code duplication
6. **Document complex test logic** with comments

## Continuous Integration

These tests are designed to run in CI environments:

- **Fast execution**: Most tests complete quickly for rapid feedback
- **Isolated execution**: Tests don't depend on external resources
- **Clear failure reporting**: Test failures provide actionable information
- **Stable results**: Tests produce consistent results across runs

## Migration from Legacy Tests

The following legacy test files have been converted to pytest format:

- `test_fix_verification.py` → `tests/test_dynamics_fix.py`
- `test_lyric_assignment.py` → `tests/test_lyric_assignment.py`
- `test_comprehensive_lyrics.py` → `tests/test_lyric_assignment.py`
- `test_implementation.py` → `tests/test_basic_functionality.py`
- `validate_voice_separation.py` → `tests/test_voice_separation.py`

All functionality from the legacy tests has been preserved and enhanced with proper pytest structure, fixtures, and additional test cases.