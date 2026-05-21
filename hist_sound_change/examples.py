"""
Example usage and tests for the Historical English Sound Change module.

This script demonstrates how to use the module to apply historical
sound changes to Middle English words.
"""

from hist_sound_change.phoneme import Phoneme, get_phoneme, MIDDLE_ENGLISH_INVENTORY
from hist_sound_change.syllable import Syllable, parse_syllable
from hist_sound_change.transcription import Transcription, transcribe
from hist_sound_change.sound_changes import (
    GreatVowelShift, 
    ReplacementChange,
    open_syllable_lengthening,
    trisyllabic_shortening,
    apply_changes
)


def test_basic_phoneme():
    """Test basic phoneme functionality."""
    print("=== Testing Phoneme ===")
    
    # Get a phoneme from inventory
    i_long = get_phoneme('iː')
    print(f"Phoneme: {i_long}")
    print(f"  Name: {i_long.name}")
    print(f"  Is vowel: {i_long.is_vowel()}")
    print(f"  Is high: {i_long.is_high_vowel()}")
    print(f"  Is front: {i_long.is_front_vowel()}")
    print(f"  Is long: {i_long.is_long()}")
    
    # Test feature matching
    pattern = {'high': '+', 'back': '-', 'long': '+'}
    print(f"  Matches high front long vowel pattern: {i_long.matches_pattern(pattern)}")
    
    print()


def test_transcription():
    """Test transcription parsing and manipulation."""
    print("=== Testing Transcription ===")
    
    # Create a transcription from IPA string
    word = "tiːd"  # Middle English "tide" (time)
    transcription = Transcription.from_string(word)
    
    print(f"Original: {word}")
    print(f"Parsed: {transcription}")
    print(f"Number of phonemes: {len(transcription)}")
    print(f"Vowel positions: {transcription.find_vowels()}")
    print(f"Syllable count: {transcription.count_syllables()}")
    
    # Get context for a specific position
    context = transcription.get_context(1)
    print(f"\nContext at position 1:")
    print(f"  Target: {context['target']}")
    print(f"  Preceding: {context['preceding']}")
    print(f"  Following: {context['following']}")
    
    # Syllabify
    syllables = transcription.syllabify()
    print(f"\nSyllables: {[str(s) for s in syllables]}")
    
    print()


def test_great_vowel_shift():
    """Test the Great Vowel Shift sound change."""
    print("=== Testing Great Vowel Shift ===")
    
    gvs = GreatVowelShift(stage='full')
    
    # Test with Middle English words
    test_words = [
        ("tiːd", "tide"),      # time
        ("huːs", "house"),     # house
        ("neːm", "name"),      # name
        ("goːs", "goose"),     # goose
        ("biːt", "bite"),      # bite
        ("boːk", "book"),      # book
    ]
    
    print("Applying full Great Vowel Shift:")
    for ipa, word in test_words:
        result = gvs.apply_to_string(ipa)
        print(f"  {word}: {ipa} > {result}")
    
    print()


def test_chain_of_changes():
    """Test applying multiple sound changes in sequence."""
    print("=== Testing Chain of Changes ===")
    
    # Example: Open syllable lengthening followed by GVS
    # This shows how ME "nama" could develop
    
    # Start with a simplified representation
    word = "naːm"  # name (already long in this example)
    
    print(f"Starting form: {word}")
    
    # Apply GVS
    gvs = GreatVowelShift(stage='full')
    after_gvs = gvs.apply_to_string(word)
    print(f"After GVS: {after_gvs}")
    
    print()


def test_pandas_integration():
    """Demonstrate how to use with pandas DataFrames."""
    print("=== Testing Pandas Integration ===")
    
    try:
        import pandas as pd
        
        # Create a sample DataFrame with Middle English words
        df = pd.DataFrame({
            'word': ['tide', 'house', 'name', 'goose', 'bite'],
            'me_ipa': ['tiːd', 'huːs', 'naːm', 'goːs', 'biːt']
        })
        
        print("Original DataFrame:")
        print(df)
        print()
        
        # Apply Great Vowel Shift to the IPA column
        gvs = GreatVowelShift(stage='full')
        df['emodern_ipa'] = df['me_ipa'].apply(gvs.apply_to_string)
        
        print("After Great Vowel Shift:")
        print(df)
        print()
        
    except ImportError:
        print("Pandas not installed - skipping pandas integration test")
        print("Install with: pip install pandas")
    
    print()


def test_custom_sound_change():
    """Test creating a custom sound change."""
    print("=== Testing Custom Sound Change ===")
    
    # Create a custom change: final devoicing
    final_devoicing = ReplacementChange(
        name="Final Devoicing",
        description="Voiced obstruents become voiceless at end of words",
        replacements={
            'b': 'p',
            'd': 't',
            'g': 'k',
            'v': 'f',
            'z': 's',
        },
        environment={
            'following': None  # Only at end of word
        }
    )
    
    test_words = ['bad', 'bag', 'hav']
    
    for word in test_words:
        result = final_devoicing.apply_to_string(word)
        print(f"  {word} > {result}")
    
    print()


def main():
    """Run all demonstrations."""
    print("=" * 60)
    print("Historical English Sound Change Module - Demonstrations")
    print("=" * 60)
    print()
    
    test_basic_phoneme()
    test_transcription()
    test_great_vowel_shift()
    test_chain_of_changes()
    test_pandas_integration()
    test_custom_sound_change()
    
    print("=" * 60)
    print("All demonstrations completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
