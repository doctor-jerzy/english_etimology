"""
Transcription representation for phonological sequences.

This module provides a class for representing phonetic transcriptions
as sequences of phonemes, with support for syllabification and
phonological operations.
"""

import re
from typing import List, Optional, Union, Iterator, Tuple
from dataclasses import dataclass
from .phoneme import Phoneme, get_phoneme, MIDDLE_ENGLISH_INVENTORY
from .syllable import Syllable, SyllableStructure, parse_syllable


@dataclass
class Transcription:
    """
    Represents a phonetic transcription as a sequence of phonemes.
    
    This class provides methods for manipulating transcriptions,
    applying sound changes, and analyzing phonological structure.
    
    Attributes:
        phonemes: List of Phoneme objects
        original: Original IPA string (if parsed from string)
        syllables: List of Syllable objects (computed on demand)
    """
    
    phonemes: List[Phoneme]
    original: Optional[str] = None
    _syllables: Optional[List[Syllable]] = None
    
    @classmethod
    def from_string(cls, ipa_string: str, inventory: Optional[dict] = None) -> 'Transcription':
        """
        Create a Transcription from an IPA string.
        
        Args:
            ipa_string: IPA transcription string
            inventory: Optional custom phoneme inventory
            
        Returns:
            Transcription object
        """
        if inventory is None:
            inventory = MIDDLE_ENGLISH_INVENTORY
        
        phonemes = []
        remaining = ipa_string
        
        # Simple tokenizer - tries to match longest symbols first
        # This handles multi-character symbols like 'iː', 'ɔː', etc.
        sorted_symbols = sorted(inventory.keys(), key=len, reverse=True)
        
        while remaining:
            matched = False
            
            # Try to match a symbol from the inventory
            for symbol in sorted_symbols:
                if remaining.startswith(symbol):
                    phonemes.append(inventory[symbol])
                    remaining = remaining[len(symbol):]
                    matched = True
                    break
            
            # If no match, check for stress markers or syllable boundaries
            if not matched:
                if remaining[0] in 'ˈˌ.':
                    # Skip stress markers and syllable boundaries for now
                    # They could be stored separately if needed
                    remaining = remaining[1:]
                else:
                    # Unknown symbol - create a placeholder
                    # In production, you might want to raise an error
                    print(f"Warning: Unknown symbol '{remaining[0]}' in '{ipa_string}'")
                    remaining = remaining[1:]
        
        return cls(phonemes=phonemes, original=ipa_string)
    
    @classmethod
    def from_phonemes(cls, phonemes: List[Phoneme]) -> 'Transcription':
        """
        Create a Transcription from a list of Phoneme objects.
        
        Args:
            phonemes: List of Phoneme objects
            
        Returns:
            Transcription object
        """
        return cls(phonemes=phonemes)
    
    def to_string(self) -> str:
        """
        Convert transcription back to IPA string.
        
        Returns:
            IPA string representation
        """
        return ''.join(p.symbol for p in self.phonemes)
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        orig_str = f", original='{self.original}'" if self.original else ""
        return f"Transcription('{self.to_string()}'{orig_str})"
    
    def __len__(self) -> int:
        return len(self.phonemes)
    
    def __iter__(self) -> Iterator[Phoneme]:
        return iter(self.phonemes)
    
    def __getitem__(self, index: Union[int, slice]) -> Union[Phoneme, 'Transcription']:
        """
        Get phoneme(s) by index.
        
        Args:
            index: Integer index or slice
            
        Returns:
            Single Phoneme or new Transcription
        """
        if isinstance(index, int):
            return self.phonemes[index]
        else:
            return Transcription(
                phonemes=self.phonemes[index],
                original=f"{self.original}[{index}]" if self.original else None
            )
    
    def get_phoneme_at(self, position: int) -> Optional[Phoneme]:
        """Get phoneme at specific position."""
        if 0 <= position < len(self.phonemes):
            return self.phonemes[position]
        return None
    
    def get_context(self, position: int) -> dict:
        """
        Get phonological context around a position.
        
        Args:
            position: Index of target phoneme
            
        Returns:
            Dictionary with:
            - target: Phoneme at position
            - preceding: Phoneme before (or None)
            - following: Phoneme after (or None)
            - position_in_word: 'initial', 'medial', or 'final'
        """
        if not 0 <= position < len(self.phonemes):
            raise IndexError(f"Position {position} out of range")
        
        return {
            'target': self.phonemes[position],
            'preceding': self.phonemes[position - 1] if position > 0 else None,
            'following': (
                self.phonemes[position + 1] 
                if position < len(self.phonemes) - 1 
                else None
            ),
            'position_in_word': (
                'initial' if position == 0
                else 'final' if position == len(self.phonemes) - 1
                else 'medial'
            ),
        }
    
    def find_vowels(self) -> List[int]:
        """Find indices of all vowels in transcription."""
        return [i for i, p in enumerate(self.phonemes) if p.is_vowel()]
    
    def find_consonants(self) -> List[int]:
        """Find indices of all consonants in transcription."""
        return [i for i, p in enumerate(self.phonemes) if p.is_consonant()]
    
    def count_syllables(self) -> int:
        """Estimate number of syllables based on vowel count."""
        return len(self.find_vowels())
    
    def syllabify(self) -> List[Syllable]:
        """
        Divide transcription into syllables.
        
        This uses a simple syllabification algorithm. For more accurate
        results, especially with complex clusters, a more sophisticated
        algorithm should be used.
        
        Returns:
            List of Syllable objects
        """
        if self._syllables is not None:
            return self._syllables
        
        if not self.phonemes:
            return []
        
        syllables = []
        vowel_indices = self.find_vowels()
        
        if not vowel_indices:
            # No vowels - treat entire word as one syllable
            syllable = parse_syllable(
                self.phonemes,
                stress='unstressed',
                position='medial'
            )
            return [syllable]
        
        # Create syllables around each vowel
        for i, vowel_idx in enumerate(vowel_indices):
            # Determine syllable boundaries
            if i == 0:
                start = 0
            else:
                # Divide consonants between previous and current vowel
                prev_vowel = vowel_indices[i - 1]
                midpoint = (prev_vowel + vowel_idx) // 2
                start = midpoint
            
            if i == len(vowel_indices) - 1:
                end = len(self.phonemes)
            else:
                next_vowel = vowel_indices[i + 1]
                midpoint = (vowel_idx + next_vowel) // 2
                end = midpoint
            
            # Extract syllable phonemes
            syll_phonemes = self.phonemes[start:end]
            
            # Determine position
            position = 'medial'
            if i == 0:
                position = 'initial'
            if i == len(vowel_indices) - 1:
                position = 'final'
            
            # Simple stress assignment (first syllable gets primary stress)
            stress = 'primary' if i == 0 else 'unstressed'
            
            syllable = parse_syllable(
                syll_phonemes,
                stress=stress,
                position=position
            )
            syllables.append(syllable)
        
        self._syllables = syllables
        return syllables
    
    def replace_phoneme(self, position: int, new_phoneme: Phoneme) -> 'Transcription':
        """
        Replace a phoneme at a specific position.
        
        Args:
            position: Index of phoneme to replace
            new_phoneme: New Phoneme object
            
        Returns:
            New Transcription with replacement
        """
        new_phonemes = self.phonemes.copy()
        new_phonemes[position] = new_phoneme
        return Transcription(
            phonemes=new_phonemes,
            original=f"{self.original} (modified)" if self.original else None
        )
    
    def replace_sequence(
        self, 
        old_sequence: List[Phoneme], 
        new_sequence: List[Phoneme]
    ) -> 'Transcription':
        """
        Replace a sequence of phonemes with another sequence.
        
        Args:
            old_sequence: Sequence to find and replace
            new_sequence: Replacement sequence
            
        Returns:
            New Transcription with replacements applied
        """
        if not old_sequence:
            return self
        
        new_phonemes = []
        i = 0
        
        while i < len(self.phonemes):
            # Check if sequence matches at current position
            if self.phonemes[i:i+len(old_sequence)] == old_sequence:
                new_phonemes.extend(new_sequence)
                i += len(old_sequence)
            else:
                new_phonemes.append(self.phonemes[i])
                i += 1
        
        return Transcription(
            phonemes=new_phonemes,
            original=f"{self.original} (modified)" if self.original else None
        )
    
    def apply_change(
        self,
        target_pattern: dict,
        replacement: Phoneme,
        environment: Optional[dict] = None
    ) -> 'Transcription':
        """
        Apply a phonological change to matching phonemes.
        
        Args:
            target_pattern: Feature pattern for target phonemes
            replacement: Phoneme to replace matches with
            environment: Optional environment constraints
                        {'preceding': pattern, 'following': pattern}
        
        Returns:
            New Transcription with changes applied
        """
        new_phonemes = []
        
        for i, phoneme in enumerate(self.phonemes):
            # Check if phoneme matches target pattern
            if phoneme.matches_pattern(target_pattern):
                # Check environment if specified
                if environment:
                    context = self.get_context(i)
                    
                    # Check preceding environment
                    if 'preceding' in environment:
                        preceding = context['preceding']
                        if preceding is None:
                            if environment['preceding'] is not None:
                                new_phonemes.append(phoneme)
                                continue
                        elif not preceding.matches_pattern(environment['preceding']):
                            new_phonemes.append(phoneme)
                            continue
                    
                    # Check following environment
                    if 'following' in environment:
                        following = context['following']
                        if following is None:
                            if environment['following'] is not None:
                                new_phonemes.append(phoneme)
                                continue
                        elif not following.matches_pattern(environment['following']):
                            new_phonemes.append(phoneme)
                            continue
                
                # Apply change
                new_phonemes.append(replacement)
            else:
                new_phonemes.append(phoneme)
        
        return Transcription(
            phonemes=new_phonemes,
            original=f"{self.original} (modified)" if self.original else None
        )
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Transcription):
            return NotImplemented
        return self.phonemes == other.phonemes


def transcribe(text: str, inventory: Optional[dict] = None) -> Transcription:
    """
    Convenience function to create a Transcription from IPA string.
    
    Args:
        text: IPA transcription string
        inventory: Optional custom phoneme inventory
        
    Returns:
        Transcription object
    """
    return Transcription.from_string(text, inventory)
