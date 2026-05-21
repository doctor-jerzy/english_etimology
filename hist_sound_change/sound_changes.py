"""
Sound change rules for historical linguistics.

This module provides classes and functions for defining and applying
historical sound changes, including the Great Vowel Shift and other
changes that occurred in the history of English.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Callable, Union
from dataclasses import dataclass
import re

from .phoneme import Phoneme, create_phoneme, MIDDLE_ENGLISH_INVENTORY
from .transcription import Transcription


@dataclass
class SoundChange(ABC):
    """
    Abstract base class for sound changes.
    
    Sound changes are phonological rules that transform phonemes
    in specific environments. This class provides the interface
    for defining new sound changes.
    
    Attributes:
        name: Name of the sound change
        description: Linguistic description of the change
        period: Historical period when change occurred
        language: Language or dialect affected
    """
    
    name: str
    description: str = ""
    period: str = ""
    language: str = ""
    
    @abstractmethod
    def apply(self, transcription: Transcription) -> Transcription:
        """
        Apply the sound change to a transcription.
        
        Args:
            transcription: Input transcription
            
        Returns:
            New Transcription with change applied
        """
        pass
    
    def apply_to_string(self, ipa_string: str) -> str:
        """
        Apply sound change to an IPA string.
        
        Args:
            ipa_string: Input IPA string
            
        Returns:
            Output IPA string
        """
        transcription = Transcription.from_string(ipa_string)
        result = self.apply(transcription)
        return result.to_string()
    
    def __call__(self, transcription: Union[Transcription, str]) -> Union[Transcription, str]:
        """Allow sound change to be called like a function."""
        if isinstance(transcription, str):
            return self.apply_to_string(transcription)
        return self.apply(transcription)
    
    def __repr__(self) -> str:
        return f"SoundChange('{self.name}')"


@dataclass
class FeatureChange(SoundChange):
    """
    A sound change defined by feature modifications.
    
    This class represents changes where phonemes matching a target
    pattern are modified by changing specific features.
    
    Attributes:
        target_pattern: Feature pattern for target phonemes
        feature_changes: Dictionary of feature modifications
        environment: Optional environment constraints
    """
    
    name: str = "Feature Change"
    description: str = ""
    period: str = ""
    language: str = ""
    target_pattern: Dict[str, str] = None
    feature_changes: Dict[str, str] = None
    environment: Optional[Dict] = None
    
    def __post_init__(self):
        if self.target_pattern is None:
            self.target_pattern = {}
        if self.feature_changes is None:
            self.feature_changes = {}
    
    def apply(self, transcription: Transcription) -> Transcription:
        """Apply feature change to transcription."""
        new_phonemes = []
        
        for i, phoneme in enumerate(transcription.phonemes):
            # Check if phoneme matches target pattern
            if phoneme.matches_pattern(self.target_pattern):
                # Check environment if specified
                if self.environment:
                    context = transcription.get_context(i)
                    
                    # Check preceding environment
                    if 'preceding' in self.environment:
                        preceding = context['preceding']
                        env_pattern = self.environment['preceding']
                        
                        if env_pattern is None:
                            if preceding is not None:
                                new_phonemes.append(phoneme)
                                continue
                        elif preceding is None or not preceding.matches_pattern(env_pattern):
                            new_phonemes.append(phoneme)
                            continue
                    
                    # Check following environment
                    if 'following' in self.environment:
                        following = context['following']
                        env_pattern = self.environment['following']
                        
                        if env_pattern is None:
                            if following is not None:
                                new_phonemes.append(phoneme)
                                continue
                        elif following is None or not following.matches_pattern(env_pattern):
                            new_phonemes.append(phoneme)
                            continue
                
                # Apply feature changes
                new_features = phoneme.features.copy()
                for feat, value in self.feature_changes.items():
                    new_features[feat] = value
                
                # Create new phoneme with updated features
                new_phoneme = Phoneme(
                    symbol=phoneme.symbol,  # Keep original symbol as base
                    features=new_features,
                    name=f"{phoneme.name} (changed)" if phoneme.name else None
                )
                new_phonemes.append(new_phoneme)
            else:
                new_phonemes.append(phoneme)
        
        return Transcription(
            phonemes=new_phonemes,
            original=f"{transcription.original} ({self.name})" if transcription.original else None
        )


@dataclass
class ReplacementChange(SoundChange):
    """
    A sound change defined by phoneme replacement.
    
    This class represents changes where specific phonemes or
    sequences are replaced with other phonemes.
    
    Attributes:
        replacements: Dictionary mapping input symbols to output symbols
        environment: Optional environment constraints
    """
    
    name: str = "Replacement Change"
    description: str = ""
    period: str = ""
    language: str = ""
    replacements: Dict[str, str] = None
    environment: Optional[Dict] = None
    
    def __post_init__(self):
        if self.replacements is None:
            self.replacements = {}
    
    def apply(self, transcription: Transcription) -> Transcription:
        """Apply replacement change to transcription."""
        new_phonemes = []
        
        for i, phoneme in enumerate(transcription.phonemes):
            # Check if phoneme symbol is in replacements
            if phoneme.symbol in self.replacements:
                # Check environment if specified
                if self.environment:
                    context = transcription.get_context(i)
                    
                    # Check preceding environment
                    if 'preceding' in self.environment:
                        preceding = context['preceding']
                        env_constraint = self.environment['preceding']
                        
                        if callable(env_constraint):
                            if not env_constraint(preceding):
                                new_phonemes.append(phoneme)
                                continue
                        elif env_constraint is None:
                            if preceding is not None:
                                new_phonemes.append(phoneme)
                                continue
                        elif isinstance(env_constraint, dict):
                            if preceding is None or not preceding.matches_pattern(env_constraint):
                                new_phonemes.append(phoneme)
                                continue
                    
                    # Check following environment
                    if 'following' in self.environment:
                        following = context['following']
                        env_constraint = self.environment['following']
                        
                        if callable(env_constraint):
                            if not env_constraint(following):
                                new_phonemes.append(phoneme)
                                continue
                        elif env_constraint is None:
                            if following is not None:
                                new_phonemes.append(phoneme)
                                continue
                        elif isinstance(env_constraint, dict):
                            if following is None or not following.matches_pattern(env_constraint):
                                new_phonemes.append(phoneme)
                                continue
                
                # Get replacement symbol(s)
                replacement_symbol = self.replacements[phoneme.symbol]
                
                # Handle multi-phoneme replacements (e.g., monophthong > diphthong)
                if ' ' in replacement_symbol:
                    # Multiple phonemes - need to look them up
                    for symbol in replacement_symbol.split():
                        if symbol in MIDDLE_ENGLISH_INVENTORY:
                            new_phonemes.append(MIDDLE_ENGLISH_INVENTORY[symbol])
                        else:
                            # Create new phoneme if not in inventory
                            new_phonemes.append(create_phoneme(symbol, phoneme.features))
                else:
                    # Single phoneme replacement
                    if replacement_symbol in MIDDLE_ENGLISH_INVENTORY:
                        new_phonemes.append(MIDDLE_ENGLISH_INVENTORY[replacement_symbol])
                    else:
                        # Preserve features from original where possible
                        new_phonemes.append(create_phoneme(replacement_symbol, phoneme.features))
            else:
                new_phonemes.append(phoneme)
        
        return Transcription(
            phonemes=new_phonemes,
            original=f"{transcription.original} ({self.name})" if transcription.original else None
        )


class GreatVowelShift(SoundChange):
    """
    The Great Vowel Shift (c. 1400-1700).
    
    A major chain shift in English vowel pronunciation that occurred
    between Middle English and Early Modern English. Long vowels
    were raised, and the highest vowels became diphthongs.
    
    Changes:
        iː > əɪ > iɪ̯ > ai (modern /aɪ/)
        eː > iː
        ɛː > eː > iː (merge with original eː)
        aː > ɛː > eː > ei (modern /eɪ/)
        uː > əʊ > ʊʊ̯ > au (modern /aʊ/)
        oː > uː
        ɔː > oː (in some dialects)
    
    This implementation provides both the full shift and individual
    stages.
    """
    
    def __init__(self, stage: str = 'full'):
        """
        Initialize the Great Vowel Shift.
        
        Args:
            stage: Which stage of the shift to apply
                   'full' - complete shift
                   'early' - initial raising (iː > ei, uː > ou)
                   'late' - diphthongization of high vowels
        """
        super().__init__(
            name="Great Vowel Shift",
            description="Chain shift of long vowels in Early Modern English",
            period="c. 1400-1700",
            language="English"
        )
        self.stage = stage
        
        # Define the vowel changes for each stage
        self.changes = {
            'full': {
                'iː': 'ai',      # > modern /aɪ/
                'eː': 'iː',
                'ɛː': 'iː',      # merge
                'aː': 'eɪ',      # > modern /eɪ/
                'uː': 'au',      # > modern /aʊ/
                'oː': 'uː',
                'ɔː': 'oː',
            },
            'early': {
                'iː': 'ei',      # beginning of raising
                'uː': 'ou',      # beginning of raising
                'eː': 'iː',
                'oː': 'uː',
            },
            'late': {
                'iː': 'ai',      # diphthongization
                'uː': 'au',      # diphthongization
            }
        }
    
    def apply(self, transcription: Transcription) -> Transcription:
        """Apply the Great Vowel Shift to a transcription."""
        replacements = self.changes.get(self.stage, self.changes['full'])
        
        new_phonemes = []
        
        for phoneme in transcription.phonemes:
            if phoneme.symbol in replacements:
                # Get replacement symbol
                replacement_symbol = replacements[phoneme.symbol]
                
                # For diphthongs, we need special handling
                if len(replacement_symbol) == 2:
                    # This is a simplified representation
                    # In a more sophisticated system, we'd create proper diphthongs
                    first_vowel = replacement_symbol[0]
                    second_vowel = replacement_symbol[1]
                    
                    # Create offglide
                    if second_vowel == 'i':
                        offglide = 'ɪ'
                    elif second_vowel == 'u':
                        offglide = 'ʊ'
                    else:
                        offglide = second_vowel
                    
                    # For now, just use the first vowel + offglide notation
                    # A proper implementation would create diphthong objects
                    new_symbol = f"{first_vowel}{offglide}̯"
                    
                    if new_symbol in MIDDLE_ENGLISH_INVENTORY:
                        new_phonemes.append(MIDDLE_ENGLISH_INVENTORY[new_symbol])
                    else:
                        # Create approximate phoneme
                        new_phonemes.append(create_phoneme(
                            new_symbol,
                            {**phoneme.features, 'long': '+'}
                        ))
                elif replacement_symbol in MIDDLE_ENGLISH_INVENTORY:
                    new_phonemes.append(MIDDLE_ENGLISH_INVENTORY[replacement_symbol])
                else:
                    # Fallback: keep original
                    new_phonemes.append(phoneme)
            else:
                new_phonemes.append(phoneme)
        
        return Transcription(
            phonemes=new_phonemes,
            original=f"{transcription.original} ({self.name} - {self.stage})" 
                     if transcription.original else None
        )


# Predefined sound changes for English historical linguistics

def get_gvs_change(stage: str = 'full') -> GreatVowelShift:
    """Get the Great Vowel Shift sound change."""
    return GreatVowelShift(stage=stage)


# Example: i-mutation (umlaut)
I_MUTATION = ReplacementChange(
    name="i-Mutation (Umlaut)",
    description="Fronting of back vowels before front vowels/glides",
    period="Pre-Old English",
    language="Old English",
    replacements={
        'uː': 'yː',
        'oː': 'øː',
        'ɑː': 'æː',
        'ɑ': 'æ',
        'o': 'ø',
        'u': 'y',
    },
    environment={
        'following': {'high': '+', 'back': '-'}  # followed by front high vowel/glide
    }
)


# Example: Open Syllable Lengthening
def open_syllable_lengthening(transcription: Transcription) -> Transcription:
    """
    Open Syllable Lengthening (Middle English, c. 1200-1300).
    
    Short vowels were lengthened in open syllables (syllables ending
    in a vowel, with no coda consonant).
    
    This is implemented as a function rather than a class to demonstrate
    how complex changes can be programmed.
    """
    syllables = transcription.syllabify()
    new_syllables = []
    
    for syllable in syllables:
        if syllable.is_open() and len(syllable.nucleus) == 1:
            nucleus_vowel = syllable.nucleus[0]
            
            # Lengthen short vowels
            if nucleus_vowel.has_feature('long', '-'):
                # Create lengthened version
                new_features = nucleus_vowel.features.copy()
                new_features['long'] = '+'
                new_features['tense'] = '+'
                
                # Map to appropriate long vowel symbol
                length_map = {
                    'ɪ': 'iː',
                    'ɛ': 'ɛː',
                    'æ': 'aː',
                    'ɔ': 'ɔː',
                    'ʊ': 'uː',
                }
                
                if nucleus_vowel.symbol in length_map:
                    new_symbol = length_map[nucleus_vowel.symbol]
                    if new_symbol in MIDDLE_ENGLISH_INVENTORY:
                        new_vowel = MIDDLE_ENGLISH_INVENTORY[new_symbol]
                    else:
                        new_vowel = Phoneme(
                            symbol=new_symbol,
                            features=new_features,
                            name=f"{nucleus_vowel.name} (lengthened)"
                        )
                    
                    # Reconstruct syllable with new vowel
                    new_syllable = parse_syllable(
                        syllable.onset + [new_vowel] + syllable.coda,
                        stress=syllable.stress,
                        position=syllable.position
                    )
                    new_syllables.append(new_syllable)
                    continue
        
        new_syllables.append(syllable)
    
    # Flatten syllables back to phoneme sequence
    all_phonemes = []
    for syllable in new_syllables:
        all_phonemes.extend(syllable.to_phonemes())
    
    return Transcription(
        phonemes=all_phonemes,
        original=f"{transcription.original} (Open Syllable Lengthening)" 
                 if transcription.original else None
    )


# Example: Trisyllabic Shortening
def trisyllabic_shortening(transcription: Transcription) -> Transcription:
    """
    Trisyllabic Shortening (Middle English).
    
    Long vowels were shortened when followed by two or more syllables.
    This explains alternations like divine/divinity, serene/serenity.
    """
    syllables = transcription.syllabify()
    
    if len(syllables) < 3:
        return transcription
    
    new_syllables = []
    
    for i, syllable in enumerate(syllables):
        # Check if there are at least two syllables following
        if len(syllables) - i >= 3 and len(syllable.nucleus) == 1:
            nucleus_vowel = syllable.nucleus[0]
            
            # Shorten long vowels
            if nucleus_vowel.has_feature('long', '+'):
                # Map to appropriate short vowel symbol
                shorten_map = {
                    'iː': 'ɪ',
                    'eː': 'ɛ',
                    'aː': 'æ',
                    'ɛː': 'ɛ',
                    'uː': 'ʊ',
                    'oː': 'ɔ',
                    'ɔː': 'ɔ',
                }
                
                if nucleus_vowel.symbol in shorten_map:
                    new_symbol = shorten_map[nucleus_vowel.symbol]
                    if new_symbol in MIDDLE_ENGLISH_INVENTORY:
                        new_vowel = MIDDLE_ENGLISH_INVENTORY[new_symbol]
                    else:
                        new_features = nucleus_vowel.features.copy()
                        new_features['long'] = '-'
                        new_features['tense'] = '-'
                        new_vowel = Phoneme(
                            symbol=new_symbol,
                            features=new_features,
                            name=f"{nucleus_vowel.name} (shortened)"
                        )
                    
                    # Reconstruct syllable with new vowel
                    new_syllable = parse_syllable(
                        syllable.onset + [new_vowel] + syllable.coda,
                        stress=syllable.stress,
                        position=syllable.position
                    )
                    new_syllables.append(new_syllable)
                    continue
        
        new_syllables.append(syllable)
    
    # Flatten syllables back to phoneme sequence
    all_phonemes = []
    for syllable in new_syllables:
        all_phonemes.extend(syllable.to_phonemes())
    
    return Transcription(
        phonemes=all_phonemes,
        original=f"{transcription.original} (Trisyllabic Shortening)" 
                 if transcription.original else None
    )


# Convenience function to apply multiple changes in sequence
def apply_changes(
    transcription: Union[Transcription, str],
    changes: List[Union[SoundChange, Callable]]
) -> Transcription:
    """
    Apply a sequence of sound changes to a transcription.
    
    Args:
        transcription: Input transcription or IPA string
        changes: List of sound changes to apply in order
        
    Returns:
        Transcription after all changes applied
    """
    if isinstance(transcription, str):
        result = Transcription.from_string(transcription)
    else:
        result = transcription
    
    for change in changes:
        result = change(result)
    
    return result
