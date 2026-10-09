"""
What every component's token layer does the same way.

Each src/components/<c>/tokens.py says which tokens the component has and which
Foundation token each one points to. The helpers below - finding a token by
path, writing the CSS reference, saving the file - used to be copied into the
23 files, with small variations. Now they live here.

The name is not tokens.py on purpose: every component already has a tokens.py,
and the import would find the component's one before this.
"""
import json
import os

from paths import TOKENS_JSON, comp_out, rel

FOUND = json.load(open(TOKENS_JSON))

TRANSPARENT = 'transparent'   # absence of color, not a color choice

# Foundation path -> custom property name. The first matching prefix wins;
# whatever is left of the path becomes the end of the name.
_PREFIXES = [
    ('focusRing.', '--al-focus-ring-'),
    ('elevation.', '--al-elevation-'),
    ('space.', '--al-space-'),
    ('radius.', '--al-radius-'),
    ('border.width.', '--al-border-width-'),
    ('iconSize.', '--al-icon-size-'),
    ('type.size.', '--al-font-size-'),
    ('type.leading.', '--al-line-height-'),
    ('type.weight.', '--al-font-weight-'),
]


def resolve_foundation(path):
    """Follows a dotted path inside tokens.json. Raises if it doesn't exist.

    A text style is a list ([name, size, ...]): the step looks it up by name.
    """
    node = FOUND
    for part in path.split('.'):
        if isinstance(node, list):
            match = next((s for s in node if s and s[0] == part), None)
            if match is None:
                raise KeyError(path)
            node = match
            continue
        if not isinstance(node, dict) or part not in node:
            raise KeyError(path)
        node = node[part]
    return node


def css_ref(ref):
    """Foundation path (or semantic name) -> CSS value.

    'space.8' -> var(--al-space-8); 'bg-brand' -> var(--al-bg-brand).
    A text style ('type.styles.body') returns only the name: the caller builds
    the style's four vars.
    """
    if ref == TRANSPARENT:
        return TRANSPARENT
    for prefix, var in _PREFIXES:
        if ref.startswith(prefix):
            return f'var({var}{ref[len(prefix):]})'
    if ref.startswith('motion.'):
        _, kind, key = ref.split('.')
        return f'var(--al-motion-{kind}-{key})'
    if ref.startswith('type.styles.'):
        return ref.split('.')[2]
    return f'var(--al-{ref})'


def size_key(font_size):
    """font-size value -> scale key (16 -> 'md')."""
    for key, v in FOUND['type']['size'].items():
        if v == font_size:
            return key
    raise KeyError(f'type.size with value {font_size} does not exist in the Foundation')


def save_css(c, text):
    """Writes build/components/<c>/al-<c>-tokens.css."""
    path = comp_out(c, f'al-{c}-tokens.css')
    open(path, 'w').write(text)
    print(f'{rel(path)} written ({os.path.getsize(path)} bytes)')
