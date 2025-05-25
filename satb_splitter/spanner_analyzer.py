"""
Spanner Analysis Module for SATB Voice Separation.

This module provides sophisticated analysis of musical spanners (crescendos, slurs, ties, etc.)
to determine their relevance to individual voices and their complexity level.
"""

import music21
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum


class SpannerComplexity(Enum):
    """Classification of spanner complexity levels."""
    SIMPLE_SINGLE_VOICE = "simple_single_voice"      # Single note dynamics, simple slurs
    COMPLEX_SINGLE_VOICE = "complex_single_voice"    # Multi-note crescendos within voice
    CROSS_VOICE = "cross_voice"                      # Spans multiple voices
    STRUCTURAL = "structural"                        # Global markings (pedal, tempo)


class SpannerType(Enum):
    """Classification of spanner types by musical function."""
    DYNAMICS = "dynamics"          # Crescendo, diminuendo, etc.
    ARTICULATION = "articulation"  # Slurs, staccato spans
    CONNECTION = "connection"      # Ties, beams
    EXPRESSION = "expression"      # Trills, ornaments
    STRUCTURAL = "structural"      # Pedal, tempo spans
    OTHER = "other"               # Unclassified spanners


class SpannerMetadata:
    """Metadata container for spanner analysis results."""
    
    def __init__(self, spanner: Any):
        self.spanner = spanner
        self.spanner_type = SpannerType.OTHER
        self.complexity = SpannerComplexity.SIMPLE_SINGLE_VOICE
        self.voice_coverage = {}  # voice_name -> coverage_percentage
        self.note_references = []
        self.pitch_range = None
        self.measure_span = None
        self.is_voice_relevant = {}  # voice_name -> boolean
        self.repair_strategy = "basic"
        self.export_priority = 1.0  # Higher = more important to preserve


class SpannerAnalyzer:
    """
    Sophisticated analyzer for musical spanners in SATB contexts.
    
    Analyzes spanners to determine:
    - Which voices they affect
    - Their complexity level
    - Appropriate processing strategy
    - Export priority
    """
    
    def __init__(self):
        """Initialize the spanner analyzer."""
        self.voice_pitch_ranges = {
            'Soprano': {'min': 60, 'max': 84},  # C4 to C6
            'Alto': {'min': 55, 'max': 79},     # G3 to G5  
            'Tenor': {'min': 48, 'max': 72},    # C3 to C5
            'Bass': {'min': 40, 'max': 64}      # E2 to E4
        }
    
    def analyze_spanner(self, spanner: Any, voice_notes: Dict[str, List] = None) -> SpannerMetadata:
        """
        Comprehensive analysis of a single spanner.
        
        Args:
            spanner: The music21 spanner object to analyze
            voice_notes: Optional dict of voice_name -> list of notes for analysis
            
        Returns:
            SpannerMetadata with complete analysis results
        """
        metadata = SpannerMetadata(spanner)
        
        # Classify spanner type
        metadata.spanner_type = self._classify_spanner_type(spanner)
        
        # Extract note references
        metadata.note_references = self._extract_note_references(spanner)
        
        # Analyze pitch characteristics
        metadata.pitch_range = self._analyze_pitch_range(metadata.note_references)
        
        # Determine measure span
        metadata.measure_span = self._analyze_measure_span(metadata.note_references)
        
        # Analyze voice relevance
        if voice_notes:
            metadata.voice_coverage = self._analyze_voice_coverage(metadata.note_references, voice_notes)
            metadata.is_voice_relevant = self._determine_voice_relevance(metadata.voice_coverage)
        else:
            # Fallback analysis based on pitch ranges
            metadata.is_voice_relevant = self._estimate_voice_relevance_by_pitch(metadata.pitch_range)
        
        # Determine complexity
        metadata.complexity = self._determine_complexity(metadata)
        
        # Set processing strategy
        metadata.repair_strategy = self._determine_repair_strategy(metadata)
        
        # Calculate export priority
        metadata.export_priority = self._calculate_export_priority(metadata)
        
        return metadata
    
    def batch_analyze_spanners(self, spanners: List[Any], voice_notes: Dict[str, List] = None) -> List[SpannerMetadata]:
        """
        Analyze multiple spanners efficiently.
        
        Args:
            spanners: List of spanner objects to analyze
            voice_notes: Optional dict of voice_name -> list of notes
            
        Returns:
            List of SpannerMetadata objects with analysis results
        """
        return [self.analyze_spanner(spanner, voice_notes) for spanner in spanners]
    
    def filter_spanners_for_voice(self, spanner_metadata_list: List[SpannerMetadata], 
                                 voice_name: str, min_relevance: float = 0.1) -> List[SpannerMetadata]:
        """
        Filter spanners relevant to a specific voice.
        
        Args:
            spanner_metadata_list: List of analyzed spanner metadata
            voice_name: Target voice name
            min_relevance: Minimum relevance threshold (0.0 to 1.0)
            
        Returns:
            List of relevant SpannerMetadata objects
        """
        relevant_spanners = []
        
        for metadata in spanner_metadata_list:
            if metadata.is_voice_relevant.get(voice_name, False):
                coverage = metadata.voice_coverage.get(voice_name, 0.0)
                if coverage >= min_relevance:
                    relevant_spanners.append(metadata)
        
        # Sort by export priority (highest first)
        relevant_spanners.sort(key=lambda m: m.export_priority, reverse=True)
        
        return relevant_spanners
    
    def _classify_spanner_type(self, spanner: Any) -> SpannerType:
        """Classify the musical function of a spanner."""
        spanner_class_name = type(spanner).__name__.lower()
        
        if 'crescendo' in spanner_class_name or 'diminuendo' in spanner_class_name:
            return SpannerType.DYNAMICS
        elif 'slur' in spanner_class_name:
            return SpannerType.ARTICULATION
        elif 'tie' in spanner_class_name or 'beam' in spanner_class_name:
            return SpannerType.CONNECTION
        elif 'trill' in spanner_class_name or 'ornament' in spanner_class_name:
            return SpannerType.EXPRESSION
        elif 'pedal' in spanner_class_name or 'tempo' in spanner_class_name:
            return SpannerType.STRUCTURAL
        else:
            return SpannerType.OTHER
    
    def _extract_note_references(self, spanner: Any) -> List[Any]:
        """Extract all note references from a spanner."""
        notes = []
        
        try:
            # Try the standard getSpannedElements method
            if hasattr(spanner, 'getSpannedElements'):
                spanned_elements = spanner.getSpannedElements()
                for element in spanned_elements:
                    if hasattr(element, 'pitch'):  # It's a note
                        notes.append(element)
                    elif hasattr(element, 'pitches'):  # It's a chord
                        notes.extend(element.notes)
            
            # Also check direct note references
            if hasattr(spanner, 'noteStart') and spanner.noteStart:
                if spanner.noteStart not in notes:
                    notes.append(spanner.noteStart)
            
            if hasattr(spanner, 'noteEnd') and spanner.noteEnd:
                if spanner.noteEnd not in notes:
                    notes.append(spanner.noteEnd)
                    
            if hasattr(spanner, 'note') and spanner.note:
                if spanner.note not in notes:
                    notes.append(spanner.note)
                    
        except Exception:
            # If extraction fails, return empty list
            pass
        
        return notes
    
    def _analyze_pitch_range(self, notes: List[Any]) -> Optional[Dict[str, int]]:
        """Analyze the pitch range of notes referenced by a spanner."""
        if not notes:
            return None
        
        midi_pitches = []
        for note in notes:
            try:
                if hasattr(note, 'pitch'):
                    midi_pitches.append(note.pitch.midi)
            except Exception:
                continue
        
        if not midi_pitches:
            return None
        
        return {
            'min': min(midi_pitches),
            'max': max(midi_pitches),
            'range': max(midi_pitches) - min(midi_pitches),
            'count': len(midi_pitches)
        }
    
    def _analyze_measure_span(self, notes: List[Any]) -> Optional[Dict[str, int]]:
        """Analyze the measure span of a spanner."""
        if not notes:
            return None
        
        measures = []
        for note in notes:
            try:
                if hasattr(note, 'activeSite') and note.activeSite:
                    if hasattr(note.activeSite, 'number'):
                        measures.append(note.activeSite.number)
            except Exception:
                continue
        
        if not measures:
            return None
        
        return {
            'start': min(measures),
            'end': max(measures),
            'span': max(measures) - min(measures) + 1,
            'measures': sorted(set(measures))
        }
    
    def _analyze_voice_coverage(self, spanner_notes: List[Any],
                               voice_notes: Dict[str, List]) -> Dict[str, float]:
        """
        Analyze what percentage of a spanner's notes belong to each voice.
        
        Uses pitch-based matching since note objects differ after voice separation.
        """
        coverage = {}
        
        if not spanner_notes:
            return coverage
        
        for voice_name, notes in voice_notes.items():
            matching_notes = 0
            
            for spanner_note in spanner_notes:
                if not hasattr(spanner_note, 'pitch'):
                    continue
                    
                # Look for pitch matches in this voice
                spanner_pitch = spanner_note.pitch
                for voice_note in notes:
                    if (hasattr(voice_note, 'pitch') and
                        voice_note.pitch.name == spanner_pitch.name and
                        voice_note.pitch.octave == spanner_pitch.octave):
                        matching_notes += 1
                        break  # Found a match, move to next spanner note
            
            coverage[voice_name] = matching_notes / len(spanner_notes) if spanner_notes else 0.0
        
        return coverage
    
    def _estimate_voice_relevance_by_pitch(self, pitch_range: Optional[Dict[str, int]]) -> Dict[str, bool]:
        """
        Estimate voice relevance based on pitch ranges (fallback method).
        """
        relevance = {}
        
        if not pitch_range:
            # If no pitch information, assume relevant to all voices
            for voice_name in self.voice_pitch_ranges:
                relevance[voice_name] = True
            return relevance
        
        spanner_min = pitch_range['min']
        spanner_max = pitch_range['max']
        
        for voice_name, voice_range in self.voice_pitch_ranges.items():
            # Check for overlap between spanner and voice pitch ranges
            overlap = not (spanner_max < voice_range['min'] or spanner_min > voice_range['max'])
            relevance[voice_name] = overlap
        
        return relevance
    
    def _determine_voice_relevance(self, voice_coverage: Dict[str, float]) -> Dict[str, bool]:
        """Determine which voices a spanner is relevant to based on coverage."""
        relevance = {}
        
        for voice_name, coverage in voice_coverage.items():
            # Consider relevant if spanner covers at least 10% of notes in that voice
            relevance[voice_name] = coverage >= 0.1
        
        return relevance
    
    def _determine_complexity(self, metadata: SpannerMetadata) -> SpannerComplexity:
        """Determine the complexity level of a spanner."""
        # Count how many voices the spanner affects
        relevant_voices = sum(1 for is_relevant in metadata.is_voice_relevant.values() if is_relevant)
        
        if relevant_voices == 0:
            return SpannerComplexity.SIMPLE_SINGLE_VOICE
        elif relevant_voices == 1:
            # Single voice - check if it's simple or complex
            note_count = len(metadata.note_references)
            if note_count <= 1:
                return SpannerComplexity.SIMPLE_SINGLE_VOICE
            else:
                return SpannerComplexity.COMPLEX_SINGLE_VOICE
        elif metadata.spanner_type == SpannerType.STRUCTURAL:
            return SpannerComplexity.STRUCTURAL
        else:
            return SpannerComplexity.CROSS_VOICE
    
    def _determine_repair_strategy(self, metadata: SpannerMetadata) -> str:
        """Determine the appropriate repair strategy for a spanner."""
        if metadata.complexity == SpannerComplexity.SIMPLE_SINGLE_VOICE:
            return "basic"
        elif metadata.complexity == SpannerComplexity.COMPLEX_SINGLE_VOICE:
            return "contextual"
        elif metadata.complexity == SpannerComplexity.CROSS_VOICE:
            return "selective"
        elif metadata.complexity == SpannerComplexity.STRUCTURAL:
            return "duplicate"
        else:
            return "fallback"
    
    def _calculate_export_priority(self, metadata: SpannerMetadata) -> float:
        """Calculate export priority for a spanner (0.0 to 1.0, higher = more important)."""
        base_priority = 0.5
        
        # Boost priority for important musical elements
        if metadata.spanner_type == SpannerType.DYNAMICS:
            base_priority += 0.3  # Dynamics are very important
        elif metadata.spanner_type == SpannerType.ARTICULATION:
            base_priority += 0.2  # Articulation is important
        elif metadata.spanner_type == SpannerType.CONNECTION:
            base_priority += 0.1  # Connections are somewhat important
        
        # Boost priority for single-voice spanners (easier to preserve)
        if metadata.complexity in [SpannerComplexity.SIMPLE_SINGLE_VOICE, SpannerComplexity.COMPLEX_SINGLE_VOICE]:
            base_priority += 0.2
        
        # Reduce priority for cross-voice spanners (harder to preserve correctly)
        elif metadata.complexity == SpannerComplexity.CROSS_VOICE:
            base_priority -= 0.2
        
        # Ensure priority stays in valid range
        return max(0.0, min(1.0, base_priority))