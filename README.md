# Historical English Sound Change Module

A linguistically-correct Python module for applying historical sound changes to Old and Middle English words, operating at the phoneme and syllable level rather than simple string manipulation.

## Features

- **Phoneme representation** with distinctive features based on the SPE (Sound Pattern of English) framework
- **Syllable structure** analysis with onset, nucleus, and coda
- **Transcription handling** for IPA strings
- **Sound change rules** that operate on natural classes of sounds
- **Environment-sensitive changes** (preceding/following context)
- **Pandas integration** for batch processing

## Quick Start

```python
from hist_sound_change import Transcription, GreatVowelShift

# Create a transcription from Middle English IPA
word = Transcription.from_string("tiːd")  # "tide" (time)
print(f"Original: {word}")

# Apply the Great Vowel Shift
gvs = GreatVowelShift(stage='full')
result = gvs.apply(word)
print(f"After GVS: {result}")
# Output: taɪ̯d
```

## Working with Pandas

```python
import pandas as pd
from hist_sound_change import GreatVowelShift

df = pd.DataFrame({
    'word': ['tide', 'house', 'name'],
    'me_ipa': ['tiːd', 'huːs', 'naːm']
})

gvs = GreatVowelShift()
df['modern_ipa'] = df['me_ipa'].apply(gvs.apply_to_string)
```

## Core Components

### Phonemes
```python
from hist_sound_change import get_phoneme

i_long = get_phoneme('iː')
print(i_long.is_vowel())        # True
print(i_long.is_high_vowel())   # True
print(i_long.matches_pattern({'high': '+', 'back': '-'}))  # True
```

### Sound Changes
```python
from hist_sound_change import ReplacementChange

final_devoicing = ReplacementChange(
    name="Final Devoicing",
    replacements={'b': 'p', 'd': 't', 'g': 'k'},
    environment={'following': None}
)
```

## Predefined Changes

- `GreatVowelShift` - The Great Vowel Shift (1400-1700)
- `I_MUTATION` - i-mutation/umlaut
- `open_syllable_lengthening` - Open syllable lengthening (ME)
- `trisyllabic_shortening` - Trisyllabic shortening (ME)

## Requirements

- Python 3.8+
- pandas (optional)

## License

MIT License
