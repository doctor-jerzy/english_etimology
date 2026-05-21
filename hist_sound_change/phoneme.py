"""
Phoneme representation with distinctive features for historical linguistics.

This module provides a phoneme class that represents speech sounds using
distinctive features, allowing for natural class operations and 
phonologically motivated sound changes.
"""

from dataclasses import dataclass, field
from typing import Optional, Set, Dict, Any
from enum import Enum


class PhonemeFeature(Enum):
    """Distinctive features for phonological analysis."""
    
    # Major class features
    SYLLABIC = "syllabic"
    CONSONANTAL = "consonantal"
    SONORANT = "sonorant"
    
    # Laryngeal features
    VOICE = "voice"
    SPREAD_GLOTTIS = "spread_glottis"  # aspiration
    CONSTRICTED_GLOTTIS = "constricted_glottis"
    
    # Manner features
    CONTINUANT = "continuant"
    NASAL = "nasal"
    STRIDENT = "strident"
    APPROXIMANT = "approximant"
    
    # Place features (labial)
    LABIAL = "labial"
    ROUND = "round"
    CORONAL = "coronal"
    
    # Place features (coronal)
    ANTERIOR = "anterior"
    DISTRIBUTED = "distributed"
    
    # Place features (dorsal)
    HIGH = "high"
    LOW = "low"
    BACK = "back"
    TENSE = "tense"
    
    # Additional features
    LONG = "long"
    RHOTIC = "rhotic"
    LATERAL = "lateral"


@dataclass(frozen=True)
class Phoneme:
    """
    Represents a phoneme with its IPA symbol and distinctive features.
    
    Features are based on SPE (Sound Pattern of English) framework,
    allowing for natural class definitions and phonologically motivated
    sound changes.
    
    Attributes:
        symbol: IPA symbol for the phoneme (e.g., 'iː', 't', 'ʃ')
        features: Dictionary mapping feature names to values (+, -, or 0)
        name: Descriptive name of the phoneme
    """
    
    symbol: str
    features: Dict[str, str] = field(default_factory=dict)
    name: Optional[str] = None
    
    def __post_init__(self):
        """Validate that all feature values are +, -, or 0."""
        for feat, value in self.features.items():
            if value not in ['+', '-', '0']:
                raise ValueError(
                    f"Feature {feat} must have value '+', '-', or '0', "
                    f"got '{value}'"
                )
    
    def has_feature(self, feature: str, value: str = '+') -> bool:
        """Check if phoneme has a specific feature value."""
        return self.features.get(feature) == value
    
    def matches_pattern(self, pattern: Dict[str, str]) -> bool:
        """
        Check if phoneme matches a feature pattern.
        
        Args:
            pattern: Dictionary of feature requirements. Values can be:
                '+' - must have the feature
                '-' - must not have the feature
                '0' - feature is irrelevant
                None or omitted - feature is not checked
        
        Returns:
            True if phoneme matches all specified features in pattern
        """
        for feat, required_value in pattern.items():
            if required_value is None:
                continue
            
            actual_value = self.features.get(feat, '0')
            
            if required_value == '0':
                continue  # Feature is irrelevant
            elif required_value != actual_value:
                return False
        
        return True
    
    def is_vowel(self) -> bool:
        """Check if phoneme is a vowel."""
        return (self.has_feature('syllabic', '+') and 
                self.has_feature('consonantal', '-'))
    
    def is_consonant(self) -> bool:
        """Check if phoneme is a consonant."""
        return self.has_feature('consonantal', '+')
    
    def is_sonorant(self) -> bool:
        """Check if phoneme is a sonorant."""
        return self.has_feature('sonorant', '+')
    
    def is_obstruent(self) -> bool:
        """Check if phoneme is an obstruent."""
        return self.has_feature('sonorant', '-')
    
    def is_high_vowel(self) -> bool:
        """Check if phoneme is a high vowel."""
        return (self.is_vowel() and 
                self.has_feature('high', '+') and 
                self.has_feature('low', '-'))
    
    def is_low_vowel(self) -> bool:
        """Check if phoneme is a low vowel."""
        return (self.is_vowel() and 
                self.has_feature('low', '+') and 
                self.has_feature('high', '-'))
    
    def is_front_vowel(self) -> bool:
        """Check if phoneme is a front vowel."""
        return self.is_vowel() and self.has_feature('back', '-')
    
    def is_back_vowel(self) -> bool:
        """Check if phoneme is a back vowel."""
        return self.is_vowel() and self.has_feature('back', '+')
    
    def is_long(self) -> bool:
        """Check if phoneme is long."""
        return self.has_feature('long', '+')
    
    def is_tense(self) -> bool:
        """Check if phoneme is tense."""
        return self.has_feature('tense', '+')
    
    def __str__(self) -> str:
        return self.symbol
    
    def __repr__(self) -> str:
        name_str = f", {self.name}" if self.name else ""
        return f"Phoneme('{self.symbol}'{name_str})"


# Predefined phonemes for Middle/Early Modern English
# These can be expanded as needed

MIDDLE_ENGLISH_VOWELS = {
    'iː': Phoneme(
        symbol='iː',
        features={
            'syllabic': '+', 'consonantal': '-', 'sonorant': '+',
            'voice': '+', 'continuant': '+', 'high': '+', 'low': '-',
            'back': '-', 'tense': '+', 'long': '+', 'round': '-'
        },
        name='long high front unrounded vowel'
    ),
    'ɪ': Phoneme(
        symbol='ɪ',
        features={
            'syllabic': '+', 'consonantal': '-', 'sonorant': '+',
            'voice': '+', 'continuant': '+', 'high': '+', 'low': '-',
            'back': '-', 'tense': '-', 'long': '-', 'round': '-'
        },
        name='short high front unrounded vowel'
    ),
    'eː': Phoneme(
        symbol='eː',
        features={
            'syllabic': '+', 'consonantal': '-', 'sonorant': '+',
            'voice': '+', 'continuant': '+', 'high': '-', 'low': '-',
            'back': '-', 'tense': '+', 'long': '+', 'round': '-'
        },
        name='long mid front unrounded vowel'
    ),
    'ɛ': Phoneme(
        symbol='ɛ',
        features={
            'syllabic': '+', 'consonantal': '-', 'sonorant': '+',
            'voice': '+', 'continuant': '+', 'high': '-', 'low': '-',
            'back': '-', 'tense': '-', 'long': '-', 'round': '-'
        },
        name='short mid front unrounded vowel'
    ),
    'aː': Phoneme(
        symbol='aː',
        features={
            'syllabic': '+', 'consonantal': '-', 'sonorant': '+',
            'voice': '+', 'continuant': '+', 'high': '-', 'low': '+',
            'back': '-', 'tense': '+', 'long': '+', 'round': '-'
        },
        name='long low front unrounded vowel'
    ),
    'uː': Phoneme(
        symbol='uː',
        features={
            'syllabic': '+', 'consonantal': '-', 'sonorant': '+',
            'voice': '+', 'continuant': '+', 'high': '+', 'low': '-',
            'back': '+', 'tense': '+', 'long': '+', 'round': '+'
        },
        name='long high back rounded vowel'
    ),
    'ʊ': Phoneme(
        symbol='ʊ',
        features={
            'syllabic': '+', 'consonantal': '-', 'sonorant': '+',
            'voice': '+', 'continuant': '+', 'high': '+', 'low': '-',
            'back': '+', 'tense': '-', 'long': '-', 'round': '+'
        },
        name='short high back rounded vowel'
    ),
    'oː': Phoneme(
        symbol='oː',
        features={
            'syllabic': '+', 'consonantal': '-', 'sonorant': '+',
            'voice': '+', 'continuant': '+', 'high': '-', 'low': '-',
            'back': '+', 'tense': '+', 'long': '+', 'round': '+'
        },
        name='long mid back rounded vowel'
    ),
    'ɔ': Phoneme(
        symbol='ɔ',
        features={
            'syllabic': '+', 'consonantal': '-', 'sonorant': '+',
            'voice': '+', 'continuant': '+', 'high': '-', 'low': '-',
            'back': '+', 'tense': '-', 'long': '-', 'round': '+'
        },
        name='short mid back rounded vowel'
    ),
    'ɔː': Phoneme(
        symbol='ɔː',
        features={
            'syllabic': '+', 'consonantal': '-', 'sonorant': '+',
            'voice': '+', 'continuant': '+', 'high': '-', 'low': '-',
            'back': '+', 'tense': '+', 'long': '+', 'round': '+'
        },
        name='long open-mid back rounded vowel'
    ),
}

MIDDLE_ENGLISH_CONSONANTS = {
    'p': Phoneme(
        symbol='p',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '-',
            'voice': '-', 'continuant': '-', 'nasal': '-',
            'labial': '+', 'coronal': '-', 'anterior': '+'
        },
        name='voiceless bilabial plosive'
    ),
    'b': Phoneme(
        symbol='b',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '-',
            'voice': '+', 'continuant': '-', 'nasal': '-',
            'labial': '+', 'coronal': '-', 'anterior': '+'
        },
        name='voiced bilabial plosive'
    ),
    't': Phoneme(
        symbol='t',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '-',
            'voice': '-', 'continuant': '-', 'nasal': '-',
            'labial': '-', 'coronal': '+', 'anterior': '+'
        },
        name='voiceless alveolar plosive'
    ),
    'd': Phoneme(
        symbol='d',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '-',
            'voice': '+', 'continuant': '-', 'nasal': '-',
            'labial': '-', 'coronal': '+', 'anterior': '+'
        },
        name='voiced alveolar plosive'
    ),
    'k': Phoneme(
        symbol='k',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '-',
            'voice': '-', 'continuant': '-', 'nasal': '-',
            'labial': '-', 'coronal': '-', 'high': '+', 'back': '+'
        },
        name='voiceless velar plosive'
    ),
    'g': Phoneme(
        symbol='g',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '-',
            'voice': '+', 'continuant': '-', 'nasal': '-',
            'labial': '-', 'coronal': '-', 'high': '+', 'back': '+'
        },
        name='voiced velar plosive'
    ),
    'f': Phoneme(
        symbol='f',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '-',
            'voice': '-', 'continuant': '+', 'strident': '+',
            'labial': '+', 'coronal': '-'
        },
        name='voiceless labiodental fricative'
    ),
    'v': Phoneme(
        symbol='v',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '-',
            'voice': '+', 'continuant': '+', 'strident': '+',
            'labial': '+', 'coronal': '-'
        },
        name='voiced labiodental fricative'
    ),
    'θ': Phoneme(
        symbol='θ',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '-',
            'voice': '-', 'continuant': '+', 'strident': '-',
            'labial': '-', 'coronal': '+', 'anterior': '+'
        },
        name='voiceless dental fricative'
    ),
    'ð': Phoneme(
        symbol='ð',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '-',
            'voice': '+', 'continuant': '+', 'strident': '-',
            'labial': '-', 'coronal': '+', 'anterior': '+'
        },
        name='voiced dental fricative'
    ),
    's': Phoneme(
        symbol='s',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '-',
            'voice': '-', 'continuant': '+', 'strident': '+',
            'labial': '-', 'coronal': '+', 'anterior': '+'
        },
        name='voiceless alveolar fricative'
    ),
    'z': Phoneme(
        symbol='z',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '-',
            'voice': '+', 'continuant': '+', 'strident': '+',
            'labial': '-', 'coronal': '+', 'anterior': '+'
        },
        name='voiced alveolar fricative'
    ),
    'ʃ': Phoneme(
        symbol='ʃ',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '-',
            'voice': '-', 'continuant': '+', 'strident': '+',
            'labial': '-', 'coronal': '+', 'anterior': '-',
            'distributed': '+'
        },
        name='voiceless postalveolar fricative'
    ),
    'ʒ': Phoneme(
        symbol='ʒ',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '-',
            'voice': '+', 'continuant': '+', 'strident': '+',
            'labial': '-', 'coronal': '+', 'anterior': '-',
            'distributed': '+'
        },
        name='voiced postalveolar fricative'
    ),
    'm': Phoneme(
        symbol='m',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '+',
            'voice': '+', 'continuant': '-', 'nasal': '+',
            'labial': '+', 'coronal': '-'
        },
        name='bilabial nasal'
    ),
    'n': Phoneme(
        symbol='n',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '+',
            'voice': '+', 'continuant': '-', 'nasal': '+',
            'labial': '-', 'coronal': '+', 'anterior': '+'
        },
        name='alveolar nasal'
    ),
    'ŋ': Phoneme(
        symbol='ŋ',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '+',
            'voice': '+', 'continuant': '-', 'nasal': '+',
            'labial': '-', 'coronal': '-', 'high': '+', 'back': '+'
        },
        name='velar nasal'
    ),
    'l': Phoneme(
        symbol='l',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '+',
            'voice': '+', 'continuant': '+', 'lateral': '+',
            'labial': '-', 'coronal': '+', 'anterior': '+'
        },
        name='alveolar lateral approximant'
    ),
    'r': Phoneme(
        symbol='r',
        features={
            'syllabic': '-', 'consonantal': '+', 'sonorant': '+',
            'voice': '+', 'continuant': '+', 'rhotic': '+',
            'labial': '-', 'coronal': '+', 'anterior': '-'
        },
        name='alveolar approximant'
    ),
    'j': Phoneme(
        symbol='j',
        features={
            'syllabic': '-', 'consonantal': '-', 'sonorant': '+',
            'voice': '+', 'continuant': '+', 'approximant': '+',
            'high': '+', 'back': '-', 'round': '-'
        },
        name='palatal approximant'
    ),
    'w': Phoneme(
        symbol='w',
        features={
            'syllabic': '-', 'consonantal': '-', 'sonorant': '+',
            'voice': '+', 'continuant': '+', 'approximant': '+',
            'high': '+', 'back': '+', 'round': '+'
        },
        name='labio-velar approximant'
    ),
    'h': Phoneme(
        symbol='h',
        features={
            'syllabic': '-', 'consonantal': '-', 'sonorant': '-',
            'voice': '-', 'continuant': '+', 'spread_glottis': '+'
        },
        name='glottal fricative'
    ),
}

# Combined inventory
MIDDLE_ENGLISH_INVENTORY = {**MIDDLE_ENGLISH_VOWELS, **MIDDLE_ENGLISH_CONSONANTS}


def get_phoneme(symbol: str) -> Phoneme:
    """
    Get a phoneme from the Middle English inventory.
    
    Args:
        symbol: IPA symbol of the phoneme
        
    Returns:
        Phoneme object
        
    Raises:
        KeyError: If symbol is not in the inventory
    """
    if symbol not in MIDDLE_ENGLISH_INVENTORY:
        raise KeyError(f"Phoneme '{symbol}' not found in inventory")
    return MIDDLE_ENGLISH_INVENTORY[symbol]


def create_phoneme(
    symbol: str,
    features: Dict[str, str],
    name: Optional[str] = None
) -> Phoneme:
    """
    Create a custom phoneme not in the predefined inventory.
    
    Args:
        symbol: IPA symbol
        features: Dictionary of distinctive features
        name: Optional descriptive name
        
    Returns:
        New Phoneme object
    """
    return Phoneme(symbol=symbol, features=features, name=name)
