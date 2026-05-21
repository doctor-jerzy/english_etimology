"""
Historical English Sound Change Module

A linguistically-correct module for applying historical sound changes
to Old and Middle English words, operating at the phoneme and syllable level.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .phoneme import Phoneme, PhonemeFeature
from .syllable import Syllable, SyllableStructure
from .transcription import Transcription
from .sound_changes import SoundChange, GreatVowelShift

__all__ = [
    'Phoneme',
    'PhonemeFeature', 
    'Syllable',
    'SyllableStructure',
    'Transcription',
    'SoundChange',
    'GreatVowelShift',
]
