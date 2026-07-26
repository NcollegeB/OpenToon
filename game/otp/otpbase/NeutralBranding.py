"""Runtime-only neutral names for user-facing legacy localizer text.

The game still relies on its original resource paths, Python identifiers, and
distributed-object class order.  This module deliberately changes localizer
values only; dictionary keys and strings that look like resource references
are left untouched.
"""

import re

from panda3d.core import ConfigVariableBool


NEUTRAL_BRANDING_ENABLED = ConfigVariableBool('neutral-branding', True)

# Longer phrases must be replaced before the individual character names.
_REPLACEMENTS = (
    ("Disney's Toontown Online", 'Open Town'),
    ('Disney Toontown Online', 'Open Town'),
    ('Walt Disney Internet Group', 'the legacy service operator'),
    ('Disney.com network', 'legacy game network'),
    ("Chip 'n Dale's Acorn Acres", 'Acorn Acres'),
    ("Chip 'n Dale's MiniGolf", 'Acorn MiniGolf'),
    ("Donald's Dreamland", 'Moonlight Meadows'),
    ("Donald's Dock", 'Anchor Bay'),
    ("Minnie's Melodyland", 'Melody Meadows'),
    ('Daisy Gardens', 'Bloom Gardens'),
    ('Goofy Speedway', 'Turbo Speedway'),
    ("Goofy's Gag Shops", 'Gag Shops'),
    ("Goofy's Gag Shop", 'Gag Shop'),
    ('Toontown Central', 'Central Commons'),
    ("Clarabelle's Cattlelog", 'the Catalog'),
    ('Clarabelle Cow', 'Catalog Guide'),
    ('VampireMickey', 'Vampire Milo'),
    ('WitchMinnie', 'Witch Millie'),
    ('DonaldDock', 'Harbor Duncan'),
    ('FrankenDonald', 'Franken Duncan'),
    ('SockHopDaisy', 'Sock-Hop Dahlia'),
    ('SuperGoofy', 'Super Gus'),
    ('WesternPluto', 'Western Pogo'),
    ('JailbirdDale', 'Jailbird Pebble'),
    ('PoliceChip', 'Officer Pip'),
    ('Mr. Goofywrench', 'Mr. Gearwrench'),
    ('Mickey Mouse', 'Milo Mouse'),
    ('Minnie Mouse', 'Millie Mouse'),
    ('Donald Duck', 'Duncan Duck'),
    ('Daisy Duck', 'Dahlia Duck'),
    ('Clarabelle', 'Catalog Guide'),
    ('Cattlelog', 'Catalog'),
    ('Mickey', 'Milo'),
    ('Minnie', 'Millie'),
    ('Donald', 'Duncan'),
    ('Daisy', 'Dahlia'),
    ('Goofy', 'Gus'),
    ('Pluto', 'Pogo'),
    ('Chip', 'Pip'),
    ('Dale', 'Pebble'),
    ('Toontown', 'Open Town'),
    ('Disney', 'Legacy'),
    ('WDIG', 'legacy service'),
)

_PRESERVED_NAMESPACE_NAMES = {
    # This is an account/name-validation denylist, not display copy. Rewriting
    # it would accidentally permit the names it is intended to block.
    'CopyrightedNames',
    # Daisy is a real flower species in the gardening system. These collections
    # describe plants, not the legacy character.
    'FlowerSpeciesNames',
    'FlowerFunnyNames',
}

_PRESERVED_PHRASES = (
    # These uses of "Daisy" are botanical, not character references.
    'Daisy Lamp',
    'Pink Daisy',
)

_COMPILED_REPLACEMENTS = tuple(
    (
        re.compile(
            r'(?<![A-Za-z])%s(?![A-Za-z])' % re.escape(legacy),
            re.IGNORECASE,
        ),
        replacement,
    )
    for legacy, replacement in _REPLACEMENTS
)

_RESOURCE_EXTENSIONS = (
    '.bam',
    '.egg',
    '.egg.pz',
    '.png',
    '.jpg',
    '.jpeg',
    '.rgb',
    '.tga',
    '.ttf',
    '.otf',
    '.wav',
    '.ogg',
    '.mp3',
    '.mid',
    '.ico',
    '.cur',
    '.dna',
    '.ptf',
)


def _looks_like_resource_reference(value):
    lowered = value.strip().lower()
    if lowered.startswith(('phase_', 'resources/', 'resources\\')):
        return True
    return any(lowered.endswith(extension) for extension in _RESOURCE_EXTENSIONS)


def _match_case(source, replacement):
    if source.isupper():
        return replacement.upper()
    if source.islower():
        return replacement.lower()
    return replacement


def _neutralize_string(value):
    if _looks_like_resource_reference(value):
        return value

    result = value
    protected = []
    for index, phrase in enumerate(_PRESERVED_PHRASES):
        token = '\x00neutral-branding-%s\x00' % index
        if phrase in result:
            result = result.replace(phrase, token)
            protected.append((token, phrase))

    for pattern, replacement in _COMPILED_REPLACEMENTS:
        result = pattern.sub(
            lambda match: _match_case(match.group(0), replacement),
            result,
        )
    for token, phrase in protected:
        result = result.replace(token, phrase)
    return result


def _neutralize_value(value, memo):
    if isinstance(value, str):
        return _neutralize_string(value)

    value_id = id(value)
    if value_id in memo:
        return memo[value_id]

    if isinstance(value, tuple):
        neutral = tuple(_neutralize_value(item, memo) for item in value)
        memo[value_id] = neutral
        return neutral

    if isinstance(value, list):
        neutral = [_neutralize_value(item, memo) for item in value]
        memo[value_id] = neutral
        return neutral

    if isinstance(value, dict):
        # Keys frequently act as protocol or lookup identifiers, so only
        # localizer values are changed.
        neutral = {
            key: _neutralize_value(item, memo)
            for key, item in value.items()
        }
        memo[value_id] = neutral
        return neutral

    return value


def neutralize_localizer(namespace):
    """Neutralize user-facing string values in a localizer module namespace."""
    if not NEUTRAL_BRANDING_ENABLED.value:
        return

    memo = {}
    for name, value in tuple(namespace.items()):
        if name.startswith('__') or name in _PRESERVED_NAMESPACE_NAMES:
            continue
        if isinstance(value, (str, tuple, list, dict)):
            namespace[name] = _neutralize_value(value, memo)
