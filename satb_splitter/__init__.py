"""
SATB Voice Splitter - Copy-and-Remove Architecture

A new approach to splitting SATB scores that preserves all musical data
by copying complete scores and removing unwanted voices.
"""

from .main import split_satb_voices
from .score_processor import ScoreProcessor
from .voice_identifier import VoiceIdentifier, VoiceMapping, VoiceLocation
from .voice_remover import VoiceRemover
from .staff_simplifier import StaffSimplifier
from .contextual_unifier import ContextualUnifier
from .exceptions import *
from .utils import ProcessingOptions

__version__ = "2.0.0"
__all__ = [
    "split_satb_voices",
    "ScoreProcessor",
    "VoiceIdentifier",
    "VoiceMapping", 
    "VoiceLocation",
    "VoiceRemover",
    "StaffSimplifier",
    "ContextualUnifier",
    "ProcessingOptions",
]