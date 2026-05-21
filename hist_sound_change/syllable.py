"""
Syllable structure representation for phonological analysis.

This module provides classes for representing syllables with their
constituent parts (onset, nucleus, coda) and properties.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from .phoneme import Phoneme


@dataclass
class SyllableStructure:
    """
    Represents the internal structure of a syllable.
    
    Attributes:
        onset: List of phonemes in the onset (consonants before nucleus)
        nucleus: List of phonemes in the nucleus (vowel/syllabic core)
        coda: List of phonemes in the coda (consonants after nucleus)
        stress: Stress level ('primary', 'secondary', 'unstressed')
    """
    
    onset: List[Phoneme] = field(default_factory=list)
    nucleus: List[Phoneme] = field(default_factory=list)
    coda: List[Phoneme] = field(default_factory=list)
    stress: str = 'unstressed'
    
    def __post_init__(self):
        """Validate syllable structure."""
        if not self.nucleus:
            raise ValueError("Syllable must have a nucleus")
        
        # Validate stress value
        valid_stress = {'primary', 'secondary', 'unstressed'}
        if self.stress not in valid_stress:
            raise ValueError(f"Stress must be one of {valid_stress}")
    
    @property
    def rhyme(self) -> List[Phoneme]:
        """Get the rhyme (nucleus + coda) of the syllable."""
        return self.nucleus + self.coda
    
    @property
    def peak(self) -> Optional[Phoneme]:
        """Get the peak (main vowel) of the syllable."""
        if self.nucleus:
            return self.nucleus[0]
        return None
    
    def is_open(self) -> bool:
        """Check if syllable is open (no coda)."""
        return len(self.coda) == 0
    
    def is_closed(self) -> bool:
        """Check if syllable is closed (has coda)."""
        return len(self.coda) > 0
    
    def has_branching_nucleus(self) -> bool:
        """Check if nucleus has more than one phoneme (long vowel/diphthong)."""
        return len(self.nucleus) > 1
    
    def has_branching_rhyme(self) -> bool:
        """Check if rhyme branches (complex nucleus or coda)."""
        return len(self.rhyme) > 1
    
    def weight(self) -> int:
        """
        Calculate syllable weight.
        
        Returns:
            1 for light syllables (short vowel, open)
            2 for heavy syllables (long vowel or closed)
            3 for superheavy syllables
        """
        weight = 0
        
        # Nucleus contributes weight
        for phoneme in self.nucleus:
            if phoneme.is_long() or phoneme.is_tense():
                weight += 2
            else:
                weight += 1
        
        # Coda contributes weight
        weight += len(self.coda)
        
        # Cap at 3 for superheavy
        return min(weight, 3)
    
    def is_light(self) -> bool:
        """Check if syllable is light."""
        return self.weight() == 1
    
    def is_heavy(self) -> bool:
        """Check if syllable is heavy."""
        return self.weight() >= 2
    
    def is_superheavy(self) -> bool:
        """Check if syllable is superheavy."""
        return self.weight() >= 3
    
    def to_phonemes(self) -> List[Phoneme]:
        """Get all phonemes in the syllable as a flat list."""
        return self.onset + self.nucleus + self.coda
    
    def __str__(self) -> str:
        parts = []
        if self.onset:
            parts.append(''.join(p.symbol for p in self.onset))
        if self.nucleus:
            nucleus_str = ''.join(p.symbol for p in self.nucleus)
            if self.stress == 'primary':
                nucleus_str = 'ˈ' + nucleus_str
            elif self.stress == 'secondary':
                nucleus_str = 'ˌ' + nucleus_str
            parts.append(nucleus_str)
        if self.coda:
            parts.append(''.join(p.symbol for p in self.coda))
        return ''.join(parts)
    
    def __repr__(self) -> str:
        return (f"SyllableStructure(onset={[p.symbol for p in self.onset]}, "
                f"nucleus={[p.symbol for p in self.nucleus]}, "
                f"coda={[p.symbol for p in self.coda]}, "
                f"stress='{self.stress}')")


@dataclass
class Syllable:
    """
    High-level syllable representation.
    
    This class wraps SyllableStructure and provides additional methods
    for phonological analysis and manipulation.
    
    Attributes:
        structure: The underlying syllable structure
        position: Position in word ('initial', 'medial', 'final')
    """
    
    structure: SyllableStructure
    position: str = 'medial'
    
    def __post_init__(self):
        """Validate position value."""
        valid_positions = {'initial', 'medial', 'final'}
        if self.position not in valid_positions:
            raise ValueError(f"Position must be one of {valid_positions}")
    
    @property
    def onset(self) -> List[Phoneme]:
        """Get onset phonemes."""
        return self.structure.onset
    
    @property
    def nucleus(self) -> List[Phoneme]:
        """Get nucleus phonemes."""
        return self.structure.nucleus
    
    @property
    def coda(self) -> List[Phoneme]:
        """Get coda phonemes."""
        return self.structure.coda
    
    @property
    def peak(self) -> Optional[Phoneme]:
        """Get syllable peak."""
        return self.structure.peak
    
    @property
    def stress(self) -> str:
        """Get stress level."""
        return self.structure.stress
    
    def set_stress(self, stress: str):
        """Set stress level."""
        self.structure.stress = stress
    
    def is_open(self) -> bool:
        """Check if syllable is open."""
        return self.structure.is_open()
    
    def is_closed(self) -> bool:
        """Check if syllable is closed."""
        return self.structure.is_closed()
    
    def is_light(self) -> bool:
        """Check if syllable is light."""
        return self.structure.is_light()
    
    def is_heavy(self) -> bool:
        """Check if syllable is heavy."""
        return self.structure.is_heavy()
    
    def get_nucleus_environment(self) -> dict:
        """
        Get information about the phonological environment of the nucleus.
        
        Returns:
            Dictionary with environment information:
            - preceding_consonant: Last consonant of onset (or None)
            - following_consonant: First consonant of coda (or None)
            - syllable_type: 'open' or 'closed'
            - syllable_weight: 'light', 'heavy', or 'superheavy'
        """
        return {
            'preceding_consonant': self.onset[-1] if self.onset else None,
            'following_consonant': self.coda[0] if self.coda else None,
            'syllable_type': 'open' if self.is_open() else 'closed',
            'syllable_weight': (
                'light' if self.is_light() 
                else 'superheavy' if self.is_superheavy()
                else 'heavy'
            ),
        }
    
    def to_phonemes(self) -> List[Phoneme]:
        """Get all phonemes in syllable."""
        return self.structure.to_phonemes()
    
    def __str__(self) -> str:
        return str(self.structure)
    
    def __repr__(self) -> str:
        return f"Syllable({repr(self.structure)}, position='{self.position}')"


def parse_syllable(
    phonemes: List[Phoneme],
    stress: str = 'unstressed',
    position: str = 'medial'
) -> Syllable:
    """
    Parse a list of phonemes into a syllable structure.
    
    This is a simple parser that assumes the first vowel(s) form
    the nucleus, preceding consonants form the onset, and following
    consonants form the coda. For more complex syllabification,
    use a dedicated syllabification algorithm.
    
    Args:
        phonemes: List of phonemes to parse
        stress: Stress level for the syllable
        position: Position in word
        
    Returns:
        Syllable object
    """
    if not phonemes:
        raise ValueError("Cannot create syllable from empty phoneme list")
    
    onset = []
    nucleus = []
    coda = []
    
    # Find nucleus (first vowel or syllabic consonant)
    nucleus_start = None
    for i, phoneme in enumerate(phonemes):
        if phoneme.is_vowel() or phoneme.has_feature('syllabic', '+'):
            nucleus_start = i
            break
    
    if nucleus_start is None:
        # No vowel found - treat first phoneme as syllabic
        nucleus_start = 0
    
    # Assign phonemes to structure
    onset = phonemes[:nucleus_start]
    
    # Find nucleus extent (continue while vowels or glides)
    nucleus_end = nucleus_start
    for i in range(nucleus_start, len(phonemes)):
        phoneme = phonemes[i]
        if (phoneme.is_vowel() or 
            phoneme.has_feature('approximant', '+') and i > nucleus_start):
            nucleus_end = i + 1
        else:
            break
    
    nucleus = phonemes[nucleus_start:nucleus_end]
    coda = phonemes[nucleus_end:]
    
    structure = SyllableStructure(
        onset=onset,
        nucleus=nucleus,
        coda=coda,
        stress=stress
    )
    
    return Syllable(structure=structure, position=position)
