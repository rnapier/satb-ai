# SATB Split V2: API Specification

## Public API

### Main Entry Point

```python
def split_satb_voices_v2(input_file: str, 
                        output_dir: Optional[str] = None,
                        options: Optional[Dict[str, Any]] = None) -> Dict[str, music21.stream.Score]:
    """
    Split SATB score into individual voice parts using copy-and-remove approach.
    
    Args:
        input_file: Path to input .mscz or .musicxml file
        output_dir: Directory for output files (optional)
        options: Processing options (optional)
        
    Returns:
        Dictionary mapping voice names to Score objects
        
    Raises:
        InvalidScoreError: If input score is not valid SATB
        VoiceDetectionError: If SATB voices cannot be detected
        ProcessingError: If processing fails
    """
```

### Processing Options

```python
@dataclass
class ProcessingOptions:
    # Voice detection options
    auto_detect_voices: bool = True
    manual_voice_mapping: Optional[VoiceMapping] = None
    fallback_to_defaults: bool = True
    
    # Unification options
    apply_dynamics_unification: bool = True
    apply_lyrics_unification: bool = True
    apply_spanner_unification: bool = True
    
    # Output options
    preserve_original_clefs: bool = False
    single_staff_output: bool = True
    include_part_names: bool = True
    
    # Processing options
    validate_output: bool = True
    detailed_logging: bool = False
    memory_optimization: bool = True
```

## Core Module APIs

### 1. VoiceIdentifier API

```python
class VoiceIdentifier:
    """Identifies SATB voice locations in a score."""
    
    def __init__(self, score: music21.stream.Score, options: ProcessingOptions):
        """Initialize with score and processing options."""
        
    def analyze_score(self) -> VoiceMapping:
        """
        Analyze score to identify voice locations.
        
        Returns:
            VoiceMapping with detected voice locations
            
        Raises:
            VoiceDetectionError: If voices cannot be detected
        """
        
    def detect_part_structure(self) -> List[PartInfo]:
        """
        Analyze the part structure of the score.
        
        Returns:
            List of PartInfo objects describing each part
        """
        
    def get_detection_confidence(self) -> float:
        """
        Get confidence level of voice detection (0.0 to 1.0).
        
        Returns:
            Confidence score for the detection
        """
        
    def suggest_manual_mapping(self) -> List[VoiceMapping]:
        """
        Suggest possible manual voice mappings.
        
        Returns:
            List of possible voice mappings for user selection
        """

@dataclass
class PartInfo:
    """Information about a part in the score."""
    index: int
    name: Optional[str]
    clef: str
    voice_count: int
    pitch_range: Tuple[str, str]  # (lowest, highest)
    note_count: int

@dataclass
class VoiceLocation:
    """Location of a voice in the score."""
    part_index: int
    voice_id: str
    clef_type: str
    confidence: float = 1.0

@dataclass
class VoiceMapping:
    """Complete mapping of SATB voices."""
    soprano: VoiceLocation
    alto: VoiceLocation
    tenor: VoiceLocation
    bass: VoiceLocation
    confidence: float = 1.0
    
    def validate(self) -> bool:
        """Validate that mapping is consistent."""
        
    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """Convert to dictionary for serialization."""
        
    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, Any]]) -> 'VoiceMapping':
        """Create from dictionary."""
```

### 2. VoiceRemover API

```python
class VoiceRemover:
    """Removes unwanted voices from score copies."""
    
    def __init__(self, context: ProcessingContext):
        """Initialize with processing context."""
        
    def remove_voices_except(self, score: music21.stream.Score, 
                           keep_voice: VoiceLocation) -> RemovalResult:
        """
        Remove all voices except the specified one.
        
        Args:
            score: Score to modify (modified in place)
            keep_voice: Voice to preserve
            
        Returns:
            RemovalResult with statistics and status
            
        Raises:
            VoiceRemovalError: If removal fails
        """
        
    def preview_removal(self, score: music21.stream.Score, 
                       keep_voice: VoiceLocation) -> RemovalPreview:
        """
        Preview what would be removed without actually removing.
        
        Args:
            score: Score to analyze
            keep_voice: Voice to preserve
            
        Returns:
            RemovalPreview with details of what would be removed
        """
        
    def get_removal_statistics(self) -> RemovalStatistics:
        """Get detailed statistics about last removal operation."""

@dataclass
class RemovalResult:
    """Result of voice removal operation."""
    success: bool
    voices_removed: List[str]
    elements_preserved: int
    elements_removed: int
    warnings: List[str]
    errors: List[str]

@dataclass
class RemovalPreview:
    """Preview of voice removal operation."""
    voices_to_remove: List[str]
    elements_to_preserve: int
    elements_to_remove: int
    potential_issues: List[str]

@dataclass
class RemovalStatistics:
    """Detailed statistics about removal operation."""
    measures_processed: int
    notes_removed: int
    rests_removed: int
    voices_removed: List[str]
    elements_preserved: Dict[str, int]  # element_type -> count
    processing_time: float
```

### 3. StaffSimplifier API

```python
class StaffSimplifier:
    """Converts multi-staff scores to single-staff layout."""
    
    def __init__(self, context: ProcessingContext):
        """Initialize with processing context."""
        
    def convert_to_single_staff(self, score: music21.stream.Score, 
                              voice_type: str) -> SimplificationResult:
        """
        Convert score to single staff layout.
        
        Args:
            score: Score to convert (modified in place)
            voice_type: Type of voice (Soprano, Alto, Tenor, Bass)
            
        Returns:
            SimplificationResult with conversion details
            
        Raises:
            StaffSimplificationError: If conversion fails
        """
        
    def get_appropriate_clef(self, voice_type: str) -> music21.clef.Clef:
        """
        Get appropriate clef for voice type.
        
        Args:
            voice_type: Voice type name
            
        Returns:
            Appropriate clef object
        """
        
    def merge_staff_elements(self, parts: List[music21.stream.Part]) -> music21.stream.Part:
        """
        Merge elements from multiple parts into single part.
        
        Args:
            parts: List of parts to merge
            
        Returns:
            Single merged part
        """

@dataclass
class SimplificationResult:
    """Result of staff simplification operation."""
    success: bool
    original_staff_count: int
    final_staff_count: int
    clef_assigned: str
    elements_merged: int
    warnings: List[str]
    errors: List[str]
```

### 4. ContextualUnifier API

```python
class ContextualUnifier:
    """Applies unification rules using complete score context."""
    
    def __init__(self, context: ProcessingContext):
        """Initialize with processing context."""
        
    def apply_unification_rules(self, voice_scores: Dict[str, music21.stream.Score]) -> UnificationResult:
        """
        Apply all unification rules to voice scores.
        
        Args:
            voice_scores: Dictionary of voice scores (modified in place)
            
        Returns:
            UnificationResult with details of applied rules
            
        Raises:
            UnificationError: If unification fails
        """
        
    def unify_dynamics(self, voice_scores: Dict[str, music21.stream.Score]) -> UnificationStepResult:
        """Apply dynamics unification rules."""
        
    def unify_lyrics(self, voice_scores: Dict[str, music21.stream.Score]) -> UnificationStepResult:
        """Apply lyrics unification rules."""
        
    def unify_spanners(self, voice_scores: Dict[str, music21.stream.Score]) -> UnificationStepResult:
        """Apply spanner unification rules."""
        
    def cross_reference_elements(self, voice_scores: Dict[str, music21.stream.Score]) -> CrossReferenceResult:
        """Cross-reference elements between voice scores for analysis."""

@dataclass
class UnificationResult:
    """Result of complete unification process."""
    success: bool
    rules_applied: List[str]
    dynamics_unified: int
    lyrics_unified: int
    spanners_unified: int
    warnings: List[str]
    errors: List[str]
    processing_time: float

@dataclass
class UnificationStepResult:
    """Result of individual unification step."""
    step_name: str
    success: bool
    elements_processed: int
    elements_unified: int
    details: Dict[str, Any]

@dataclass
class CrossReferenceResult:
    """Result of cross-reference analysis."""
    common_elements: Dict[str, List[Any]]
    voice_specific_elements: Dict[str, List[Any]]
    potential_unifications: List[str]
```

### 5. ScoreProcessor API

```python
class ScoreProcessor:
    """Main orchestrator for SATB splitting process."""
    
    def __init__(self, options: ProcessingOptions):
        """Initialize with processing options."""
        
    def process_satb_score(self, input_file: str) -> ProcessingResult:
        """
        Process SATB score through complete pipeline.
        
        Args:
            input_file: Path to input score file
            
        Returns:
            ProcessingResult with voice scores and metadata
            
        Raises:
            ProcessingError: If processing fails at any stage
        """
        
    def validate_input(self, score: music21.stream.Score) -> ValidationResult:
        """Validate that input score is suitable for SATB splitting."""
        
    def create_voice_copies(self, original: music21.stream.Score) -> Dict[str, music21.stream.Score]:
        """Create complete copies of score for each voice."""
        
    def validate_output(self, voice_scores: Dict[str, music21.stream.Score]) -> ValidationResult:
        """Validate that output scores are correct and complete."""

@dataclass
class ProcessingResult:
    """Complete result of SATB processing."""
    success: bool
    voice_scores: Dict[str, music21.stream.Score]
    voice_mapping: VoiceMapping
    processing_steps: List[str]
    statistics: ProcessingStatistics
    warnings: List[str]
    errors: List[str]
    processing_time: float

@dataclass
class ProcessingStatistics:
    """Statistics about the processing operation."""
    input_measures: int
    input_parts: int
    input_voices: int
    output_scores: int
    elements_preserved: Dict[str, int]
    memory_usage_mb: float
    processing_stages: Dict[str, float]  # stage_name -> time_seconds
```

## Exception Hierarchy

```python
class SATBSplitError(Exception):
    """Base exception for SATB splitting errors."""
    pass

class InvalidScoreError(SATBSplitError):
    """Raised when input score is not valid for SATB splitting."""
    pass

class VoiceDetectionError(SATBSplitError):
    """Raised when SATB voices cannot be detected."""
    pass

class VoiceRemovalError(SATBSplitError):
    """Raised when voice removal fails."""
    pass

class StaffSimplificationError(SATBSplitError):
    """Raised when staff simplification fails."""
    pass

class UnificationError(SATBSplitError):
    """Raised when unification process fails."""
    pass

class ProcessingError(SATBSplitError):
    """Raised when overall processing fails."""
    pass

class ValidationError(SATBSplitError):
    """Raised when validation fails."""
    pass
```

## Utility Functions

```python
def load_score(file_path: str) -> music21.stream.Score:
    """
    Load score from file with proper error handling.
    
    Args:
        file_path: Path to score file
        
    Returns:
        Loaded score object
        
    Raises:
        InvalidScoreError: If file cannot be loaded or is invalid
    """

def save_voice_scores(voice_scores: Dict[str, music21.stream.Score], 
                     output_dir: str,
                     base_name: str) -> List[str]:
    """
    Save voice scores to files.
    
    Args:
        voice_scores: Dictionary of voice scores
        output_dir: Output directory
        base_name: Base name for output files
        
    Returns:
        List of created file paths
    """

def compare_with_v1_output(v2_scores: Dict[str, music21.stream.Score],
                          v1_scores: Dict[str, music21.stream.Score]) -> ComparisonResult:
    """
    Compare V2 output with V1 output for validation.
    
    Args:
        v2_scores: Voice scores from V2 system
        v1_scores: Voice scores from V1 system
        
    Returns:
        ComparisonResult with detailed comparison
    """

@dataclass
class ComparisonResult:
    """Result of comparing V1 and V2 outputs."""
    equivalent: bool
    differences: List[str]
    improvements: List[str]
    regressions: List[str]
    statistics: Dict[str, Any]
```

## Configuration API

```python
@dataclass
class UnificationRules:
    """Configuration for unification rules."""
    dynamics_soprano_to_all: bool = True
    dynamics_common_to_all: bool = True
    lyrics_fill_gaps: bool = True
    lyrics_preserve_voice_specific: bool = True
    spanners_system_wide_to_all: bool = True
    spanners_preserve_voice_specific: bool = True

@dataclass
class VoiceDetectionConfig:
    """Configuration for voice detection."""
    confidence_threshold: float = 0.8
    use_pitch_analysis: bool = True
    use_clef_analysis: bool = True
    use_pattern_matching: bool = True
    fallback_strategies: List[str] = None

@dataclass
class OutputConfig:
    """Configuration for output generation."""
    file_format: str = 'musicxml'
    include_metadata: bool = True
    preserve_layout: bool = False
    single_staff_only: bool = True
    part_name_format: str = "{base_name} ({voice_name})"
```

## CLI Integration

```python
def create_cli_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser for V2 system."""

def main_cli():
    """Main CLI entry point for V2 system."""

def migrate_from_v1(v1_options: Dict[str, Any]) -> ProcessingOptions:
    """Convert V1 options to V2 ProcessingOptions."""
```

This API specification provides a comprehensive interface for the new SATB split system while maintaining compatibility with existing workflows and enabling future extensions.